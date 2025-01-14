import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin, urlparse
import re


# Base URL for Snowflake documentation
base_url = "https://docs.snowflake.com/en/"


# Directory to save JSON files
os.makedirs("snowflake_docs", exist_ok=True)


# Track visited URLs
visited_urls = set()
# Queue of URLs to crawl
url_queue = [base_url]


# Function to check if a URL is within the Snowflake documentation domain
def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc == "docs.snowflake.com" and parsed_url.path.startswith("/en/")


# Function to sanitize filename
def sanitize_filename(title):
    # Remove invalid filename characters and limit length
    title = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", title)
    return title[:50] if title else "untitled"


while url_queue:
    url = url_queue.pop(0)
    if url in visited_urls:
        continue  # Skip if already visited


    try:
        # Fetch the page
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
       
        # Mark as visited
        visited_urls.add(url)


        # Extract relevant data
        page_title = soup.find("title").text.strip() if soup.find("title") else "Untitled"
        sanitized_title = sanitize_filename(page_title)
        page_content = soup.prettify()


        # Structure data as JSON
        data = {
            "url": url,
            "title": page_title,
            "html": page_content,
        }


        # Save JSON file with sanitized title and .json suffix
        filename = f"snowflake_docs/{sanitized_title}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Saved {filename}")


        # Find all internal links and add them to the queue
        for link in soup.find_all("a", href=True):
            link_url = urljoin(base_url, link["href"])  # Resolve relative URLs
            if is_valid_url(link_url) and link_url not in visited_urls:
                url_queue.append(link_url)


        # Rate limiting to avoid overwhelming the server
        time.sleep(1)  # Adjust as needed


    except Exception as e:
        print(f"Error fetching {url}: {e}")

