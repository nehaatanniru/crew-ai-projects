from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from ddgs import DDGS

llm = LLM(model="gemini/gemini-flash-latest", temperature=0.2)


@tool("DuckDuckGo Search")
def search_tool(query: str) -> str:
    """Search the web using DuckDuckGo. Input is a search query.
    Returns the top results with title, link and short snippet."""
    try:
        results = DDGS().text(query, max_results=5)
        return "\n\n".join(
            f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}"
            for r in results
        )
    except Exception as e:
        return f"Search failed: {e}"


def run_blog_crew(topic: str) -> str:
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Find accurate, current facts, statistics and real examples about {topic}",
        backstory="You are a careful researcher. You search multiple sources and "
                  "always note where each fact came from.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role="Blog Writer",
        goal="Turn research notes into an engaging 600-word blog post about {topic}",
        backstory="You write clear, friendly blog posts for a general audience. "
                  "You only use facts given to you in the research notes.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    editor = Agent(
        role="Editor",
        goal="Polish the blog post about {topic} for tone, clarity and factual accuracy",
        backstory="You are a strict editor. You fix awkward sentences, remove any claim "
                  "not supported by the research, and keep the post around 600 words.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description="Research the topic: {topic}. Use the search tool to find recent facts, "
                    "statistics and real-world examples. Collect at least 5 key points, "
                    "each with its source link.",
        expected_output="A bullet list of at least 5 key findings about {topic}, "
                        "each with a source link.",
        agent=researcher,
    )

    write_task = Task(
        description="Using the research notes, write an engaging 600-word blog post "
                    "about {topic} with a title, subheadings and a conclusion.",
        expected_output="A 600-word blog post in Markdown with a title, subheadings "
                        "and a conclusion.",
        agent=writer,
        context=[research_task],
    )

    edit_task = Task(
        description="Edit the blog post for tone, clarity and factual accuracy. Remove any "
                    "claim not supported by the research notes.",
        expected_output="The final polished 600-word blog post in Markdown.",
        agent=editor,
        context=[research_task, write_task],
    )

    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, write_task, edit_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={"topic": topic})
    return result.raw
