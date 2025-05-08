import fitz  # PyMuPDF
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a smaller and faster pre-trained sentence-transformers model
model = SentenceTransformer('all-MiniLM-L6-v2')


class DocumentParse:
    def __init__(self, document_path):
        self.pdf_path = document_path
        self.query = None

    def extract_text_from_pdf(self):
        text = ""
        try:
            doc = fitz.open(self.pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text")  # Use "text" mode for faster extraction
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")

    def preprocess_text (self, text):
        """Lightweight text preprocessing."""
        # Remove extra whitespace and special characters
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        return text.lower()

    def chunk_text (self, text, chunk_size=60, overlap=50):
        """Split text into smaller chunks with overlap."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def create_faiss_index (self, chunks):
        """Create a FAISS index for the text chunks."""
        embeddings = model.encode(chunks)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search
        index.add(np.array(embeddings).astype('float32'))
        return index, embeddings

    def search_faiss_index (self, query, index, chunks, embeddings, top_k=1):
        """Search the FAISS index for the most relevant chunks."""
        query_embedding = model.encode([query])
        distances, indices = index.search(np.array(query_embedding).astype('float32'), top_k)
        results = [(chunks[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
        return results

    def answer_query(self, query):
        """Answer a query based on the PDF content."""
        self.query = query
        # Extract and preprocess text
        text = self.extract_text_from_pdf()
        processed_text = self.preprocess_text(text)

        # Split text into chunks
        chunks = self.chunk_text(processed_text)

        # Create FAISS index
        index, embeddings = self.create_faiss_index(chunks)

        # Search for the most relevant chunks
        results = self.search_faiss_index(query, index, chunks, embeddings, top_k=1)

        # Return the most relevant chunk as the answer
        if results:
            return results[0][0]
        else:
            return "No relevant information found."
