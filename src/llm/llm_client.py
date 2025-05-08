import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def openai_llm_client(model: str = "openai/gpt-4o-mini"):
    assert model.startswith("openai/"), "Model must start with 'openai/'"
    return LLM(
        model=model,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def groq_llm_client(model: str = "groq/llama3-70b-8192"):
    assert model.startswith("groq/"), "Model must start with 'groq/'"
    return LLM(
        model=model,
        api_key=os.getenv("GROQ_API_KEY"),
    )


def hf_llm_client(model: str = "huggingface/mistralai/Mistral-7B-Instruct-v0.3"):
    assert model.startswith("huggingface/"), "Model must start with 'huggingface/'"

    return LLM(
        model=model,
        api_key=os.getenv("HF_TOKEN"),
    )


if __name__ == "__main__":
    print(os.getenv("OPENAI_API_KEY"))
    openai_llm = openai_llm_client("openai/gpt-4o-mini")
    print(openai_llm.call("Hello, how are you?"))

    # groq_llm = groq_llm_client("groq/llama3-70b-8192")
    # print(groq_llm.call("Hello, how are you?"))

    # hf_llm = hf_llm_client("huggingface/mistralai/Mistral-7B-Instruct-v0.3")
    # print(hf_llm.call("Hello, how are you?"))
