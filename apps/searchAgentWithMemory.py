from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b")

tavily_search_tool = TavilySearch(max_results=3, topic="general")

agent = create_agent(
    model=llm,
    tools=[tavily_search_tool],
    system_prompt="You are a agent and can search any query on internet",
    checkpointer=InMemorySaver(),
)

while True:
    user_query = input("USER : ")
    if user_query.lower() in ["quit", "stop", "exit"]:
        print("Stopped.")
        break

    res = agent.invoke(
        {"messages": [{"role": "user", "content": user_query}]},
        {"configurable": {"thread_id": "1"}},
    )

    r = res["messages"][-1].content

    print("AI :", r)  # ? this will answer directly => no streaming like answer
