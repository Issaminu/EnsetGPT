import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not os.path.exists("processed"):
    os.mkdir("processed")

loader = DirectoryLoader("text/www.enset-media.ac.ma")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embedding_function = OpenAIEmbeddings(model="text-embedding-3-large", chunk_size=1024)

vector_store = VectorstoreIndexCreator(
    vectorstore_kwargs={"persist_directory": "persist"}
).from_loaders([loader])
