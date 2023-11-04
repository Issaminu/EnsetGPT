import requests
import re
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import PyPDF2
import io
import pytesseract
from pdf2image import convert_from_bytes
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


domain = "enset-media.ac.ma"  # <-  domain to be crawled
full_url = "https://www.enset-media.ac.ma/formations/initiales/diplome"  # <- put your domain to be crawled with https or http

MAX_WORKERS = 6  # <- number of threads to be used for crawling


# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]*://.+"
# Define ANSI escape codes for text colors
GREEN = "\033[92m"  # Green text
RESET = "\033[0m"  # Reset to default text color


# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])


# Function to get the hyperlinks from a URL
def get_hyperlinks(response):
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        # If the response is not HTML, return an empty list
        if not response.headers.get("Content-Type").startswith("text/html"):
            return []

        # Get the HTML
        html = response.text
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, response):
    clean_links = []
    for link in set(get_hyperlinks(response)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([])

    # Create a directory to store the text files
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/" + local_domain + "/"):
        os.mkdir("text/" + local_domain + "/")

    futures = []
    # Use ThreadPoolExecutor for multi-threading
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # While the queue is not empty, continue crawling
        while queue:
            url = queue.pop()
            if url not in seen:
                seen.add(url)
                futures.append(
                    executor.submit(process_url, url, queue, seen, local_domain)
                )
                if queue.__len__() == 0:
                    concurrent.futures.wait(futures)

    print("Congrats! Done crawling ", domain)


def process_url(url, queue, seen, local_domain):
    if url.startswith("https://" + local_domain + "/utilisateur/") or url.startswith(
        "https://" + local_domain + "/user"
    ):
        print(
            "⏩ Skipping page: "
            + url
            + " ( URL pattern matches '/utilisateur' or '/user' )"
        )
        return
    if "?" in url and not "page=" in url.split("?")[-1]:
        print(
            "⏩ Skipping page: " + url + " ( URL pattern contains '?' but not '?page=' )"
        )
        return
    if ".xml" in url:
        print("⏩ Skipping page: " + url + " ( URL pattern matches '.xml' )")
        return
    if "liste" in url:
        print("⏩ Skipping page: " + url + " ( URL pattern matches 'liste' )")
        return
    if "attente" in url:
        print("⏩ Skipping page: " + url + " ( URL pattern matches 'attente' )")
        return
    if "selection" in url:
        print("⏩ Skipping page: " + url + " ( URL pattern matches 'selection' )")
        return
    if "recrutement" in url:
        print("⏩ Skipping page: " + url + " ( URL pattern matches 'recrutement' )")
        return
    if "resultat" in url:
        print("⏩ Skipping page: " + url + " ( URL pattern matches 'recrutement' )")
        return
    print(f"{GREEN}🔍 {url}{RESET}")  # for debugging and to see the progress

    if url.endswith(".pdf"):  # If the URL is a PDF, handle it differently
        handle_pdf(url, local_domain)
        return

    # Save text from the url to a <url>.txt file
    with open(
        "text/" + local_domain + "/" + url[8:].replace("/", "_") + ".txt",
        "w",
        encoding="UTF-8",
    ) as f:
        response = requests.get(url)
        # Get the text from the URL using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Get the main-content div, if it exists. Otherwise, get everything from the page
        # Find the title element
        title_element = soup.find("h1", class_="title")
        # Find the content element
        main_content_element = soup.find("div", id="main-content")

        if title_element and main_content_element:
            text = title_element.get_text() + main_content_element.get_text()
        else:
            text = soup.get_text()

        # If the crawler gets to a page that requires JavaScript, it will stop the crawl
        if "You need to enable JavaScript to run this app." in text:
            print("Unable to parse page " + url + " due to JavaScript being required")

        # Otherwise, write the text to the file in the text directory
        f.write(text)

    # Get the hyperlinks from the URL and add them to the queue
    for link in get_domain_hyperlinks(local_domain, response):
        if link not in seen:
            if not (
                link.endswith(".jpg")
                or link.endswith(".png")
                or link.endswith(".jpeg")
                or link.endswith(".doc")
                or link.endswith(".docx")
                or link.endswith(".gif")
            ):
                queue.append(link)


def handle_pdf(url, local_domain):
    if "arab" in url:
        print("⏩ Skipping PDF: " + url + " ( URL pattern matches 'arab' )")
    pdf_content = download_pdf(url, local_domain)
    print("Extracting text from PDF...")
    # Attempt to extract text from the PDF
    extracted_text = save_pdf_text(pdf_content, url, local_domain)
    if not extracted_text.strip():  # Check if the extracted text is empty
        print("PDF appears to be scanned, using OCR instead...")
        ocr_scanned_pdf(pdf_content, url, local_domain)
    print("Done processing PDF:", url)


def save_pdf_text(pdf_content, url, local_domain):
    if pdf_content:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text_content = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text()

            file_path = (
                "text/"
                + local_domain
                + "/"
                + url[8:].replace("/", "_").split("/")[-1]
                + ".txt"
            )
            with open(file_path, "w", encoding="UTF-8") as f:
                f.write(text_content)
            return text_content
        except Exception as e:
            print("Error while processing PDF:", url)
            print(e)
    return ""


def ocr_scanned_pdf(pdf_content, pdf_url, local_domain):
    if pdf_content:
        try:
            pages = convert_from_bytes(pdf_content)
            for pageNum, imgBlob in enumerate(pages):
                text = pytesseract.image_to_string(imgBlob, lang="eng")
                file_path = (
                    "text/"
                    + local_domain
                    + "/"
                    + pdf_url[8:].replace("/", "_").split("/")[-1]
                    + "OCR.txt"
                )
                with open(file_path, "w", encoding="UTF-8") as file:
                    file.write(text)
        except Exception as e:
            print("Error during OCR:", e)


def download_pdf(url, local_domain):
    if not os.path.exists("PDFs/"):
        os.mkdir("PDFs/")

    if not os.path.exists("PDFs/" + local_domain + "/"):
        os.mkdir("PDFs/" + local_domain + "/")

    filename = Path("PDFs/" + local_domain + "/" + url[8:].replace("/", "_"))

    try:
        response = requests.get(url)

        if response.status_code == 200:
            filename.write_bytes(response.content)
            return response.content  # Return the PDF content
        else:
            print("Failed to download PDF:", url)
    except Exception as e:
        print("Error while downloading PDF:", e)

    return None


crawl(full_url)
