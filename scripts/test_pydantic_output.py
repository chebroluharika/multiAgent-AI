import os

from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Blog(BaseModel):
    title: str
    content: str


def test_pydantic_output(llm):
    blog_agent = Agent(
        role="Blog Content Generator Agent",
        goal="Generate a blog title and content",
        backstory="""You are an expert content creator, skilled in crafting engaging and informative blog posts.""",
        verbose=False,
        allow_delegation=False,
        llm=llm,
    )

    task1 = Task(
        description="""Create a blog title and content on a given topic. Make sure the content is under 200 words.""",
        expected_output="A compelling blog title and well-written content.",
        agent=blog_agent,
        output_pydantic=Blog,
    )

    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[blog_agent],
        tasks=[task1],
        verbose=True,
        process=Process.sequential,
    )

    result = crew.kickoff()

    return result


if __name__ == "__main__":
    groq_llm = LLM(model="groq/llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))

    huggingface_llm = LLM(
        model="huggingface/mistralai/Mistral-7B-Instruct-v0.3",
        api_key=os.getenv("HUGGINGFACE_API_KEY"),
    )

    print("Testing Groq LLM")
    result = test_pydantic_output(groq_llm)
    print(f"{result.pydantic = }")

    print("Testing Huggingface LLM")
    result = test_pydantic_output(huggingface_llm)
    print(f"{result.pydantic = }")
