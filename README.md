# EnsetGPT

EnsetGPT is an AI chatbot project developed as part of a Java course, focusing on providing information about ENSET. The chatbot utilizes OpenAI's language models, web scraping, and a vector database to answer user queries related to the.

## Project Structure

The project is divided into several parts:

### `ai_chat`

This is the main directory for the Python part of the project. It contains the following important files:

- **`web_crawler.py`:** This script is responsible for crawling the web and gathering data for the chatbot.

- **`query.py`:** This script is used to query the data gathered by the web crawler.

### `java_server`

This directory contains the Java server part of the project. The main file is:

- **`EnsetGPTServer.java`:** This is the main server file. It handles incoming requests and sends responses.

### `java_client`

This directory contains the Java client part of the project. The main file is:

- **`ChatController.java`:** This file is responsible for handling the user interface and user input.

## Overview

EnsetGPT integrates various components to deliver a seamless and informative chatbot experience. Below is an overview of each major aspect:

- **Web Scraping:** The `ai_chat` directory includes the `web_crawler.py` script, responsible for gathering data by crawling the web.

- **Java Server:** The `java_server` directory contains the `EnsetGPTServer.java` file, the main server handling incoming requests and responses.

- **Java Client:** The `java_client` directory hosts the `ChatController.java` file, responsible for managing the user interface and input.

- **Vector Database:** Data obtained from web scraping is processed into a vector database, enhancing the chatbot's ability to respond accurately and quickly.

- **Langchain Integration:** The chatbot leverages the Langchain framework to handle user queries, providing a conversational interface.

## Getting Started

Follow these steps to set up and run the EnsetGPT project:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/ensetgpt.git
   cd ensetgpt
   ```

2. **Set Up API Keys:**
   - You need to fill in `OPENAI_API_KEY` (for access to GPT-3.5-Turbo and text-embedding-ada-002) and `TAVILY_API_KEY` (for web search).

3. **Install Dependencies:**
   - Navigate to each submodule directory (`ai_chat/`, `java_server/`, `java_client/`) and follow the provided instructions to install dependencies.

4. **Run the Java Server:**
   - In the `java_server/` directory, run the Java server to start listening for user queries.

5. **Launch Java Client:**
   - Open the `java_client/` project and run the Java client application.

6. **Interact with the Chatbot:**
   - Access the application interface and start interacting with the EnsetGPT chatbot.

## Contributing

Contributions to EnsetGPT are welcome! Whether you want to report issues, submit pull requests, or provide feedback, your involvement is appreciated. Please follow our [Contribution Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.
