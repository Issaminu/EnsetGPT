import os
import sys
from langchain import hub
from langchain_community.document_loaders import DirectoryLoader
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
    create_openai_tools_agent,
)
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

PERSIST = True

query = sys.argv[1:][0]

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


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

messages = []
messages.append(
    SystemMessage(
        content="Your name is EnsetGPT, a chatbot that knows everything about ENSET Mohammedia. Use the conversation history as context. If the question is too vague, respond by asking for clarification. For information tied to time, use the tool web-search to search for the most recent information possible."
    )
)


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
web_search = TavilySearchResults(max_results=5)


tools = [
    Tool(
        name="qa-enset",
        func=enset_chain.invoke,
        description="Useful when you need to answer ENSET-related questions",
    ),
    Tool(
        name="web-search",
        func=web_search.run,
        description="Useful for when you need to look up the web, get up-to-date information, or when qa-enset doesn't prove useful.",
    ),
    Tool(
        name="qa-general",
        func=general_chain.invoke,
        description="Useful when you need to answer general, non-ENSET-related questions.",
    ),
]


def ask(input: str) -> str:
    result = ""
    try:
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
