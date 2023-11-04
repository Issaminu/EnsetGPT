import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import PyPDF2
import io
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pathlib import Path

# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]*://.+"

domain = "enset-media.ac.ma"  # <-  domain to be crawled
full_url = "https://www.enset-media.ac.ma/formations/initiales/17776/modules"  # <- put your domain to be crawled with https or http


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
def get_hyperlinks(url):
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:
            # If the response is not HTML, return an empty list
            if not response.info().get("Content-Type").startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode("utf-8")
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
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
    seen = set([url])

    # Create a directory to store the text files
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/" + local_domain + "/"):
        os.mkdir("text/" + local_domain + "/")

    # Create a directory to store the csv files
    if not os.path.exists("processed"):
        os.mkdir("processed")

    # While the queue is not empty, continue crawling
    while queue:
        # Get the next URL from the queue

        url = queue.pop()

        if url.startswith(
            "https://" + local_domain + "/utilisateur/"
        ) or url.startswith("https://" + local_domain + "/user"):
            print(
                "Skipping page: "
                + url
                + " ( URL pattern matches '/utilisateur' or '/user' )"
            )
            continue
        if ".xml" in url:
            print("Skipping page: " + url + " ( URL pattern matches '.xml' )")
            continue

        print(url)  # for debugging and to see the progress

        # Save text from the url to a <url>.txt file
        with open(
            "text/" + local_domain + "/" + url[8:].replace("/", "_") + ".txt",
            "w",
            encoding="UTF-8",
        ) as f:
            # Get the text from the URL using BeautifulSoup
            soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the main-content div, if it exists. Otherwise, get everything from the page
            main_content = soup.find("div", id="main-content")
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()

            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if "You need to enable JavaScript to run this app." in text:
                print(
                    "Unable to parse page " + url + " due to JavaScript being required"
                )

            # Otherwise, write the text to the file in the text directory
            f.write(text)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                if link.endswith(".pdf"):
                    handle_pdf(link, local_domain)
                elif not (
                    link.endswith(".jpg")
                    or link.endswith(".png")
                    or link.endswith(".jpeg")
                    or link.endswith(".doc")
                    or link.endswith(".docx")
                ):
                    queue.append(link)
                seen.add(link)


def handle_pdf(url, local_domain):
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/" + local_domain + "/"):
        os.mkdir("text/" + local_domain + "/")
    extracted_text = save_pdf_text(url, local_domain)
    if extracted_text.strip():  # Check if the extracted text is empty
        ocr_scanned_pdf(url, local_domain)  # Perform OCR on scanned PDF


def save_pdf_text(url, local_domain):
    try:
        # Open the PDF file using requests
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code == 200:
            # Create a PDF file reader
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(response.content))

            # Initialize a string to store the text content
            text_content = ""

            # Iterate through each page and extract the text
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text()

            # Save the text to a text file
            with open(
                "text/"
                + local_domain
                + "/"
                + url.split("/")[-1].replace(".pdf", ".txt"),
                "w",
                encoding="UTF-8",
            ) as f:
                f.write(text_content)
                return text_content
        else:
            print("Failed to download PDF:", url)
    except Exception as e:
        print("Error while processing PDF:", url)
        print(e)
    return ""


# OCR function
def ocr_scanned_pdf(pdf_url, local_domain):
    pdf_path = "PDFs/" + local_domain + "/" + pdf_url[8:].replace("/", "_")
    print(pdf_path)
    if not os.path.exists(pdf_path):
        download_pdf(pdf_url, local_domain)
    if not os.path.exists("text/"):
        os.mkdir("text/")
    if not os.path.exists("text/" + local_domain):
        os.mkdir("text/" + local_domain)

    pages = convert_from_path(pdf_path)
    for pageNum, imgBlob in enumerate(pages):
        text = pytesseract.image_to_string(imgBlob, lang="eng")
        with open(
            "text/"
            + local_domain
            + "/"
            + pdf_url[8:].replace("/", "_").split("/")[-1].replace(".pdf", ".txt"),
            "w",
            encoding="UTF-8",
        ) as file:
            file.write(text)


def download_pdf(url, local_domain):
    if not os.path.exists("PDFs/"):
        os.mkdir("PDFs/")
    if not os.path.exists("PDFs/" + local_domain + "/"):
        os.mkdir("PDFs/" + local_domain + "/")
    filename = Path("PDFs/" + local_domain + "/" + url[8:].replace("/", "_"))
    try:
        # Open the PDF file using requests
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code == 200:
            filename.write_bytes(response.content)
        else:
            print("Failed to download PDF:", url)
    except Exception as e:
        print("Error while processing PDF:", url)
        print(e)


crawl(full_url)
