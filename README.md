# EnsetGPT

This repository is a comprehensive Python codebase designed for web crawling and text processing, organized into distinct scripts. The project's primary objective is to systematically extract and process text content from websites.

This project was created for the Java mini project, under the GLSID curriculum at ENSET.

## 1. Web Scraping

### Crawler
- The `web_crawler.py` script is used to crawl a specified website (`enset-media.ac.ma` in this case) and extract text from its pages.
- It creates a local directory structure to save the crawled text files.
- It skips `.pdf` files, `.doc` files and some other unusable stuff.

### Text Processing
- After crawling, the text files are processed using the `text_processing.py` script.
- It extracts text from crawled HTML files and removes unnecessary characters.
- The processed text is then saved into a CSV file for further use.

## 2. Tokenization and Embeddings

### Tokenization
- Tokenization is performed using the `tiktoken` library to count the number of tokens in each text.

### Splitting Text
- If a text contains more tokens than the maximum allowed (500 in this case), it is split into smaller chunks while preserving the context.
- The resulting text chunks are also tokenized and visualized.

### Embeddings
- The `embeddings.py` script calculates embeddings for the text chunks using OpenAI's `text-embedding-ada-002` model.
- The embeddings are saved in a CSV file for later use.

## 3. Question Answering

### Context Creation
- The `question_answering.py` script defines functions to create context for a given question based on the most similar text chunks.
- The distance metric used is cosine similarity.

### Answering Questions
- The code interacts with the OpenAI GPT-3.5 Turbo model to answer user questions.
- It utilizes the previously generated context to provide answers based on the given question.



# Getting Started

This section serves as an entry point for users to initiate their interaction with the web crawling and text processing code in this repository.

## 1. Cloning the Repository

Getting started involves cloning this repository to your local machine, enabling you to access and manipulate the code. Execute the following command in your terminal:

```bash
git clone https://github.com/Issaminu/ai-chatbot-enset.git
```

## 2. Installing Dependencies

Smooth operation of the code hinges on the installation of essential Python dependencies. This can be accomplished using `pip` by executing the following command within the root directory of the repository:

```bash
pip install -r requirements.txt
```

This step ensures that all the necessary packages are installed and readily available for use.

## 3. Web Crawling

### Initiating Website Crawling

The web crawler module empowers users to embark on the journey of website crawling. To begin, open the `web_crawler.py` script and configure the `full_url` variable with the URL of your target website:

```python
domain = "example.com"  # <-  domain to be crawled
full_url = "https://www.example.com/"  # <- put your domain to be crawled with https or http
```

Having made this adjustment, execute the script as follows:

```bash
python web_crawler.py
```

The web crawler will embark on its journey from the specified URL, navigating through the website and systematically accumulating textual data from its web pages.

## 4. Text Processing

### Preprocessing Text Data

Once the web crawler has diligently gathered text data, the next step is to preprocess this data using the dedicated scripts. First, invoke the `text_processing.py` script to perform cleansing and formatting of the textual data:

```bash
python text_processing.py
```

This script's output is a CSV file named "scraped.csv," which houses the pristine, processed text data, prepared for subsequent analysis.

### (Optional) Auto-Cleaning of Text Data

Should further refinement and cleansing of text data be required, the optional `auto_clean.py` script can be employed. This script leverages the [Auto Clean package](https://pypi.org/project/py-AutoClean) to enhance the quality of the textual data:

```bash
python auto_clean.py
```

The result is the creation of a CSV file named "autocleaned.csv," containing the meticulously cleaned and finalized text data.

## 5. NLP Question Answering

The repository encompasses a script designed for NLP-based question answering. Users can actively engage with this script by posing questions and receiving contextually relevant answers, as derived from the processed text data. Here is how to harness this capability:

```bash
python main.py
```

This script harnesses the powerful OpenAI GPT-3.5 Turbo model and your prepared embedding data to offer insightful responses to your queries. Simply follow the prompts, input your questions, and anticipate receiving informative answers.
