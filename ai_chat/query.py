import os
import sys
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores.chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.tools import Tool
from langchain.agents.types import AgentType
from langchain.agents import initialize_agent
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PERSIST = True

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

if PERSIST and os.path.exists("persist"):
    vectorstore = Chroma(
        persist_directory="persist", embedding_function=OpenAIEmbeddings()
    )
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
    # loader = TextLoader("combined.txt")
    loader = DirectoryLoader("text/www.enset-media.ac.ma")
    if PERSIST:
        index = VectorstoreIndexCreator(
            vectorstore_kwargs={"persist_directory": "persist"}
        ).from_loaders([loader])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader])


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo-1106")

chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 4}),
    condense_question_llm=llm,
    memory=memory,
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
        result = executor({"input": input})
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


chat_history = []
executor = initialize_agent(
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    memory=memory,
    agent_kwargs={"system_message": system_message},
    verbose=False,
    max_execution_time=30,
    max_iterations=6,
    handle_parsing_errors=True,
    early_stopping_method="generate",
    stop=["\nObservation:"],
)


if query in ["quit", "q", "exit"]:
    sys.exit()
# result = chain({"question": query, "chat_history": chat_history})
result = ask(query)
# print(memory)
print(result["output"])

# chat_history.append((query, result["answer"]))
