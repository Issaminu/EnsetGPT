import os
import sys
import signal
from dotenv import load_dotenv
from rich.console import Console
from langchain import hub
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores.chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.chains.conversation.base import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain_core.messages.system import SystemMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.chains.question_answering import load_qa_chain
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()


def initialize_vectorstore():
    try:
        vectorstore = Chroma(
            persist_directory="persist", embedding_function=OpenAIEmbeddings()
        )
        retriever = VectorStoreIndexWrapper(
            vectorstore=vectorstore
        ).vectorstore.as_retriever()
    except FileNotFoundError:
        print("No vector database found. Please run `python create_vector_db.py`")
        retriever = None

    return retriever


def initialize_chains_and_tools(llm, retriever):
    memory = ConversationBufferMemory(return_messages=True)

    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_chain(llm=llm, chain_type="stuff")
    enset_chain = RetrievalQA(
        retriever=retriever,
        combine_documents_chain=doc_chain,
        verbose=False,
        output_key="output",
    )
    general_chain = ConversationChain(llm=llm)
    web_search = TavilySearchResults(max_results=6)

    tools = [
        Tool(
            name="qa-enset",
            func=enset_chain.invoke,
            description="Useful for ENSET-related questions",
        ),
        Tool(
            name="web-search",
            func=web_search.run,
            description="Useful for web searches and up-to-date information",
        ),
        Tool(
            name="qa-general",
            func=general_chain.invoke,
            description="Useful for general, non-ENSET-related questions",
        ),
    ]

    prompt = hub.pull("hwchase17/openai-tools-agent")
    agent = create_openai_tools_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        max_execution_time=30,
        memory=memory,
        max_iterations=6,
    )

    return agent_executor, memory


def handle_signals():
    def signal_handler(sig, frame):
        print("\nGoodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)


def main_loop(agent_executor, messages, query):
    console = Console()

    while True:
        if query in ["exit", "q", "quit"]:
            print("\nGoodbye!")
            sys.exit(0)
        result = agent_executor.invoke({"input": query, "chat_history": messages})
        console.print(result["output"])
        messages.extend(
            [HumanMessage(content=query), AIMessage(content=result["output"])]
        )
        query = input("Prompt: ")


if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    retriever = initialize_vectorstore()

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    agent_executor, memory = initialize_chains_and_tools(llm, retriever)

    messages = [
        SystemMessage(
            content="Your name is EnsetGPT, a chatbot that knows everything about ENSET Mohammedia. Use the conversation history as context. If the question is too vague, respond by asking for clarification. For information tied to time, use the tool web-search to search for the most recent information possible."
        )
    ]

    handle_signals()

    query = None
    if len(sys.argv) > 1:
        query = sys.argv[1:][0]
    else:
        query = input("Prompt: ")

    main_loop(agent_executor, messages, query)
