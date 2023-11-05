import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PERSIST = True

query = None
if len(sys.argv) > 1:
    query = sys.argv[1]

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

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 4}),
)

chat_history = []
while True:
    if not query:
        query = input("Prompt: ")
    if query in ["quit", "q", "exit"]:
        sys.exit()
    result = chain({"question": query, "chat_history": chat_history})
    print(result["answer"])

    chat_history.append((query, result["answer"]))
    query = None
