import os
import sys
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores.chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.schema import HumanMessage, AIMessage
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents.types import AgentType
from langchain.agents import initialize_agent
from langchain.chains.question_answering import load_qa_chain
import sqlite3
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PERSIST = True

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
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
    "SELECT type, message FROM message_store WHERE session_id = ?", session_id
)

conversation = [(type, message) for type, message in cursor.fetchall()]


llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo-1106")

messages = []
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


chain = RetrievalQA(
    retriever=retreiver,
    combine_documents_chain=doc_chain,
    verbose=True,
    output_key="output",
)
system_message = (
    "Your name is EnsetAI, a chatbot that knows everything about ENSET Mohammedia."
)
tools = [
    Tool(
        name="qa-enset",
        func=chain.run,
        description="Useful when you need to answer ENSET-related questions",
    )
]


def ask(input: str) -> str:
    result = ""
    try:
        result = agent.run({"input": input, "chat_history": messages})
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


agent = initialize_agent(
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    agent_kwargs={"system_message": system_message},
    verbose=True,
    max_execution_time=30,
    memory=memory,
    max_iterations=6,
    handle_parsing_errors=True,
    early_stopping_method="generate",
    stop=["\nObservation:"],
)


result = ask(query)

cursor.execute(
    "INSERT INTO message_store (session_id, message, type, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP), (?, ?, ?, CURRENT_TIMESTAMP)",
    [session_id, query, "human", session_id, result, "ai"],
)
conn.commit()
conn.close()
