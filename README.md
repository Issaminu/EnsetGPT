# EnsetGPT: The ENSET AI Chatbot

![thumbnail](https://raw.githubusercontent.com/Issaminu/EnsetGPT/main/EnsetGPT.png)

An AI-powered chatbot CLI application designed to provide information and answer questions about ENSET Mohammedia. Leveraging the power of advanced natural language processing and machine learning, EnsetGPT is here to make finding information about the school as easy as chatting with a friend.

## Features

- **AI-Powered Conversations**: Engage in natural, human-like conversations with EnsetGPT to get your questions answered.
- **ENSET-Specific Knowledge**: Whether it's details about courses, admissions, or events, EnsetGPT is trained to provide accurate information about ENSET Mohammedia.
- **Web Crawling for Up-to-Date Information**: Thanks to its integrated web crawler, EnsetGPT stays updated with the latest information directly from the ENSET Mohammedia website.
- **PDF and OCR Support**: EnsetGPT can read and extract information from PDF documents, ensuring that no source of information is left untapped.
- **Multi-Threaded Crawling**: The web crawler utilizes multi-threading to efficiently gather data, ensuring a vast knowledge base.
- **Conversational Memory**: EnsetGPT remembers the context of the conversation, allowing for a coherent and continuous interaction.

## Getting Started

>[!WARNING]
> You need to use Python 3.11 for this project, as currently the LangChain dependency doesn't run on newer versions, see [this issue](https://github.com/langchain-ai/langchain/issues/11479) for more info.

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Issaminu/EnsetGPT.git
   ```
2. Navigate to the project directory:
   ```
   cd EnsetGPT
   ```
3. Install the required Python packages:
   ```
   pip3.11 install -r requirements.txt
   ```

### Running EnsetGPT

#### Running from scratch

1. First, you need to crawl the ENSET Mohammedia website and prepare the knowledge base. Run:
   ```
   python3.11 web_crawler.py
   ```
2. Next, create the vector database for efficient querying:
   ```
   python3.11 create_vector_db.py
   ```
3. Finally, start chatting with EnsetGPT:
   ```
   python3.11 query.py
   ```

#### Using pre-made vector database
   
   This repository comes with the ENSET website already crawled, if you're ok with using a slightly out of date information database, then feel free to directly use the provided `text/www.enset-media.ac.ma/` for the raw TXT files, or the `persist/chroma.sqlite3` vector database for the ready-to-use embedding database.
   Simply run the following command to start chatting with EnsetGPT:
   ```
   python3.11 query.py
   ```

## How It Works

EnsetGPT leverages a combination of web crawling, natural language processing (NLP), and vector space modeling to provide a conversational interface that can answer questions about ENSET Mohammedia. Here's a detailed breakdown of its components and how they work together:

### 1. Web Crawling

- **Purpose**: The primary goal of the web crawler, implemented in `web_crawler.py`, is to systematically browse the ENSET Mohammedia website and collect information that will form the knowledge base for EnsetGPT. This includes text from web pages and PDF documents.

- **Process**:
  - The crawler starts from a predefined URL that serves as the entry point.
  - It then looks for hyperlinks on this page and follows them, ensuring only to visit pages within the specified domain to avoid crawling external sites.
  - Special attention is given to PDF files, which are downloaded and processed separately. Text from PDFs is extracted either directly or through OCR (Optical Character Recognition) if the document contains scanned images.
  - The crawler is designed to be multi-threaded, allowing it to process multiple pages in parallel, significantly speeding up the data collection process.
  - Pages and documents that do not contribute valuable information (e.g., user login pages, images) are skipped based on predefined rules.

### 2. Vector Database Creation

- **Purpose**: After collecting the data, `create_vector_db.py` processes and transforms the text into a format suitable for efficient querying. This involves creating a vector database where documents are represented as vectors in a high-dimensional space.

- **Process**:
  - Text documents are first split into manageable chunks. This is crucial for handling large documents and improving the accuracy of the vector representations.
  - Each chunk is then converted into a vector using OpenAI's embeddings. These embeddings capture the semantic meaning of the text, allowing for queries based on the meaning rather than exact keyword matches.
  - The vectors are stored in a database, with each vector associated with the corresponding text chunk. This database supports efficient similarity searches, enabling the retrieval of the most relevant documents for a given query.

### 3. Querying and Chatting

- **Purpose**: `query.py` serves as the interface between the user and EnsetGPT. It allows users to input questions and retrieves answers based on the knowledge base.

- **Process**:
  - When a user inputs a question, the system first converts the question into a vector using the same embedding model used for the database creation.
  - It then searches the vector database for the most similar vectors, which correspond to the chunks of text most relevant to the user's query.
  - The retrieved text chunks are then processed to generate a coherent and contextually appropriate answer. This may involve summarizing information or generating new text based on the context provided by the retrieved chunks.
  - Throughout the conversation, EnsetGPT maintains a history of the interaction, allowing it to provide contextually relevant and coherent responses over the course of the chat session.

By integrating these components, EnsetGPT offers a powerful tool for accessing and interacting with information about ENSET Mohammedia in a conversational manner. This approach combines the latest advancements in web crawling, information retrieval, and natural language processing to create a user-friendly interface for querying school-specific information.

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/Issaminu/EnsetGPT/blob/main/LICENSE) for more information.

## Acknowledgments

- ENSET Mohammedia for providing permition to crawl the website.
- OpenAI for the `gpt-3.5-turbo` and `text-embedding-3-large` models.
- The Python community for the invaluable libraries and tools.

---

**Note**: This project is a school project and is not officially affiliated with ENSET Mohammedia.
