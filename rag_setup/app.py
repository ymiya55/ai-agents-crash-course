import asyncio
import os

import chainlit as cl
import chromadb
import dotenv
from agents import Agent, HostedMCPTool, Runner, SQLiteSession, function_tool
from openai.types.responses import ResponseTextDeltaEvent

if "OPENAI_API_KEY" not in os.environ:
    dotenv.load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY is not set")

chroma_client = chromadb.PersistentClient()
collection = chroma_client.get_collection(name="my_collection")


@function_tool
@cl.step(type="tool")
def search_kb(query: str) -> str:
    "Search the knowledge base for information about fruits"
    results = collection.query(query_texts=[query], n_results=2)
    return results


agent = Agent(
    name="Assistant",
    instructions="""
    You are a helpful assistant. If it's about calories, first always search the knowledge base for information about the question.
    IMPORTANT: If there is no explicit quantitative information about the calories in the knowledge base, ALWAYS use the exasearch tool to search the web for information.
    If it's not about calories, don't use tools. Only talk about calories, not about arbitrary topics
    If it's not about food and not saying hi, but about an arbitrary topic, respond with: "I'm sorry, I can only talk about calories.".
    If it's about food, it's OK to answer the question even if it's not about calories.
    """,
    tools=[
        search_kb,
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "exasearch",
                "server_url": "https://mcp.exa.ai/mcp?exaApiKey=ecdb1348-0ebf-4adf-ae6d-f08620c8bdc5",
                "require_approval": "never",
            }),
    ],
)

# enable_verbose_stdout_logging()


@cl.on_chat_start
def on_chat_start():
    session = SQLiteSession("calorie conversation")
    cl.user_session.set("agent_session", session)


@cl.on_message
async def main(message: cl.Message):
    session = cl.user_session.get("agent_session")
    result = Runner.run_streamed(
        agent,
        message.content,
        session=session,
    )

    msg = cl.Message(content="")
    async for event in result.stream_events():

        # Stream final message text to screen
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(token=event.data.delta)
            # print(event.data.delta, end="", flush=True)

        elif event.type == "raw_response_event" and hasattr(event.data, "item"):
            item = event.data.item
            if hasattr(item, "type") and item.type == "mcp_call":
                async with cl.Step(name="MCP call: ExaSearch") as step:
                    step.output = f"MCP call: {
                        item.name} on server '{
                        item.server_label}' with args: {
                        item.arguments}"
                    step.update()
                    # print(
                    #    f"\nMCP call: {item.name} on server '{item.server_label}' with args: {item.arguments}"
                    # )
            elif hasattr(item, "type") and item.type == "function_call":
                print(f"\nTool call: {item.name} with args: {item.arguments}")

    await msg.update()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("agentic", os.getenv("CHAINLIT_PASSWORD")):
        return cl.User(
            identifier="Student",
            metadata={"role": "student", "provider": "credentials"},
        )
    else:
        return None


if __name__ == "__main__":
    asyncio.run(main())
