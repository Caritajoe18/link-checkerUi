import requests
import csv
from concurrent.futures import ThreadPoolExecutor


def url_response(url):
    """Send a HEAD request and print the status code."""
    try:
        print(
            f"({requests.head(url, allow_redirects=True, timeout=10).status_code}) {url}")
    except requests.RequestException:
        print(f"(Not found) {url}")


# Extract URLs from CSV file
with open("Task 2 - Intern.csv", encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # to skip the header
    urls = [row[0] for row in reader if row]

# Process URLs concurrently
with ThreadPoolExecutor() as executor:
    executor.map(url_response, urls)
