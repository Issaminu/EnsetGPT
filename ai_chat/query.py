import json
import os
import sys
from langchain import hub
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores.chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.chains.conversation.base import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents.agent_types import AgentType
from langchain_core.messages.system import SystemMessage
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
    create_self_ask_with_search_agent,
    create_openai_tools_agent,
    initialize_agent,
)
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.chains.question_answering import load_qa_chain
import sqlite3
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID_ENSET = os.getenv("GOOGLE_CSE_ID_ENSET")
GOOGLE_CSE_ID_WEB = os.getenv("GOOGLE_CSE_ID_WEB")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

PERSIST = True

session_id = sys.argv[1]
query = sys.argv[2:][0]

if PERSIST and os.path.exists("persist"):
    vectorstore = Chroma(
        persist_directory="persist", embedding_function=OpenAIEmbeddings()
    )
    retreiver = VectorStoreIndexWrapper(
        vectorstore=vectorstore
    ).vectorstore.as_retriever()
else:
    # loader = TextLoader("combined.txt")
    loader = DirectoryLoader("text/www.enset-media.ac.ma")
    if PERSIST:
        retreiver = (
            VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"})
            .from_loaders([loader])
            .vectorstore.as_retriever()
        )
    else:
        retreiver = (
            VectorstoreIndexCreator().from_loaders([loader]).vectorstore.as_retriever()
        )


conn = sqlite3.connect("persist/chat_history.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT type, message, timestamp FROM message_store WHERE session_id = ? ORDER BY timestamp ASC LIMIT 20;",
    session_id,
)

conversation = [
    (type, message, timestamp) for type, message, timestamp in cursor.fetchall()
]


llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.7)

messages = []
messages.append(
    SystemMessage(
        content="Your name is EnsetAI, a chatbot that knows everything about ENSET Mohammedia. Use the conversation history as context. If the question is too vague, respond by asking for clarification. For information tied to time, use the tool web-search to search for the most recent information possible."
    )
)
for message in conversation:
    if message[0] == "human":
        messages.append(HumanMessage(content=message[1]))
    else:
        messages.append(AIMessage(content=message[1]))


memory = ConversationBufferMemory(return_messages=True)

question_generator = LLMChain(
    llm=ChatOpenAI(
        temperature=0,
        streaming=True,
    ),
    prompt=CONDENSE_QUESTION_PROMPT,
)
doc_chain = load_qa_chain(
    llm=ChatOpenAI(
        temperature=0,
        streaming=True,
    ),
    chain_type="stuff",
)


enset_chain = RetrievalQA(
    retriever=retreiver,
    combine_documents_chain=doc_chain,
    verbose=True,
    output_key="output",
)

general_chain = ConversationChain(llm=llm)

google_search = GoogleSearchAPIWrapper(google_cse_id=GOOGLE_CSE_ID_WEB)
enset_search = GoogleSearchAPIWrapper(google_cse_id=GOOGLE_CSE_ID_ENSET)
web_search = TavilySearchResults(max_results=5)


tools = [
    Tool(
        name="qa-enset",
        func=enset_chain.invoke,
        description="Useful when you need to answer ENSET-related questions",
    ),
    Tool(
        name="enset-search",
        func=web_search.invoke,
        description="Useful for when you need to look up ENSET-related questions, use only after trying with qa-enset first",
    ),
    Tool(
        name="qa-general",
        func=general_chain.invoke,
        description="Useful when you need to answer non-ENSET-related questions, or when qa-enset or enset-search don't prove useful",
    ),
    Tool(
        name="web-search",
        func=web_search.run,
        description="Useful for when you need to look up the web, get up-to-date information, or when the other tool don't prove useful.",
    ),
]


def ask(input: str) -> str:
    result = ""
    try:
        print(messages)
        result = agent_executor.invoke(
            {
                "input": input,
                "chat_history": messages,
            }
        )
    except Exception as e:
        response = str(e)
        if response.startswith("Could not parse LLM output: `"):
            response = response.removeprefix(
                "Could not parse LLM output: `"
            ).removesuffix("`")
            return response
        else:
            raise Exception(str(e))
    return result


prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_execution_time=30,
    memory=memory,
    max_iterations=6,
    early_stopping_method="generate",
)

result = ask(query)
print(result["output"])
cursor.execute(
    "INSERT INTO message_store (session_id, message, type, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP), (?, ?, ?, CURRENT_TIMESTAMP)",
    [session_id, query, "human", session_id, result["output"], "ai"],
)
conn.commit()
conn.close()
