import re
from pathlib import Path

import faiss
import fitz  # PyMuPDF
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# Load a smaller and faster pre-trained sentence-transformers model
model = SentenceTransformer("all-MiniLM-L6-v2")


class DocumentParse:
    def __init__(
        self,
        document_path: str,
        chunk_size: int = 200,
        overlap: int = 20,
        index_name: str = "ceph_documentation_index",
        folder_path: str | Path = "data",
    ):
        self.doc_path = document_path
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.index_name = index_name
        self.folder_path = folder_path

        self.local_index_name = Path(self.folder_path) / f"{self.index_name}.faiss"

    def extract_text_from_pdf(self):
        if self.doc_path.startswith("http"):
            response = requests.get(self.doc_path)
            text = response.text
        elif self.doc_path.endswith(".txt"):
            with open(self.doc_path, encoding="utf-8") as file:
                text = file.read()
        elif self.doc_path.endswith(".pdf"):
            text = ""
            try:
                doc = fitz.open(self.doc_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text += page.get_text(
                        "text"
                    )  # Use "text" mode for faster extraction
            except Exception as e:
                raise Exception(f"Failed to extract text from PDF: {e}")
        else:
            raise ValueError(f"Unsupported file type: {self.doc_path}")

        return text

    def preprocess_text(self, text):
        """Lightweight text preprocessing."""
        # Remove extra whitespace and special characters
        text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with a single space
        text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
        return text.lower()

    def chunk_text(self, text):
        """Split text into smaller chunks with overlap."""
        words = text.split()
        chunks: list[str] = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i : i + self.chunk_size])
            chunks.append(chunk)
        return chunks

    def create_faiss_index(self, chunks):
        """Create a FAISS index for the text chunks."""
        embeddings = model.encode(chunks, show_progress_bar=True)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search
        index.add(np.array(embeddings).astype("float32"))
        return index, embeddings

    def save_faiss_index(self):
        print(f"Saving index to {self.local_index_name}")
        Path(self.folder_path).mkdir(exist_ok=True, parents=True)
        faiss.write_index(self.index, str(self.local_index_name))
        print("Done")

    def load_faiss_index(self):
        print(f"Loading index from {self.local_index_name}")
        self.index = faiss.read_index(str(self.local_index_name))
        self.chunks = self.get_chunks()
        print("Done")

    def search_faiss_index(self, query, top_k=1):
        """Search the FAISS index for the most relevant chunks."""
        query_embedding = model.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype("float32"), top_k
        )
        results = [
            (self.chunks[idx], distances[0][i]) for i, idx in enumerate(indices[0])
        ]
        return results

    def get_chunks(self):
        text = self.extract_text_from_pdf()
        processed_text = self.preprocess_text(text)
        chunks = self.chunk_text(processed_text)

        return chunks

    def ingest_document(self):
        """Ingest the document and create a FAISS index."""
        print("Ingesting chunks")
        self.chunks = self.get_chunks()
        self.index, self.embeddings = self.create_faiss_index(self.chunks)

        print(f"Ingested {len(self.chunks)} chunks")

        self.save_faiss_index()

    def answer_query(self, query):
        # Search for the most relevant chunks
        results = self.search_faiss_index(query, top_k=1)

        # Return the most relevant chunk as the answer
        if results:
            return results[0][0]
        else:
            return "No relevant information found."


if __name__ == "__main__":
    # parser = DocumentParse(
    #     "https://docs.ceph.com/en/reef/_sources/radosgw/sync-modules.rst.txt"
    # )

    import os

    from dotenv import load_dotenv

    load_dotenv()

    documentation_path = os.getenv("DOCUMENTATION")
    parser = DocumentParse(
        documentation_path,
        folder_path=Path(documentation_path).parent,
        index_name="ceph_documentation_index",
    )
    print("Answer:")
    parser.ingest_document()

    parser.load_faiss_index()
    print(parser.answer_query("What is the sync module?"))
