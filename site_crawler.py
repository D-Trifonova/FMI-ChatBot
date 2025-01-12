import requests
from bs4 import BeautifulSoup
import time
import json

# Base URL for the website
base_url = 'https://www.fmi-plovdiv.org'

# Set to track visited URLs and avoid revisiting the same pages
visited_urls = set()

# List to store all scraped data
dataset = []


# Function to fetch and parse a page
def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


# Function to extract title and content from a page
def scrape_page(url):
    soup = fetch_page(url)
    if not soup:
        return None

    # Extract the title
    title = soup.find('td', class_='pagetitle')
    title = title.get_text(strip=True) if title else "No title"

    # Extract the content
    content = soup.find('div', class_='contentx')
    content = content.get_text(strip=True) if content else "No content"

    return {'url': url, 'title': title, 'content': content}


# Function to find all internal links on a page
def find_internal_links(soup, base_url):
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']

        # Skip external links, mailto links, and anchors
        if href.startswith('mailto:') or href.startswith('#'):
            continue

        # Skip external links
        if href.startswith('http') and not href.startswith(base_url):
            continue

        # Handle relative links
        if href.startswith('/'):
            full_url = f"{base_url}{href}"
        elif not href.startswith('http'):
            full_url = f"{base_url}/{href}"
        else:
            full_url = href

        # Skip links that point to archived news - they are in a separate dataset
        if 'archive=1' in full_url:
            continue

        links.append(full_url)
    return list(set(links))  # Remove duplicates


# Recursive crawler function
def crawl(url):
    # Skip already visited URLs
    if url in visited_urls:
        return

    print(f"Crawling: {url}")
    visited_urls.add(url)

    # Scrape the page and save the data
    page_data = scrape_page(url)
    if page_data:
        dataset.append(page_data)

    # Find and follow internal links
    soup = fetch_page(url)
    if not soup:
        return

    internal_links = find_internal_links(soup, base_url)
    for link in internal_links:
        if link not in visited_urls:
            time.sleep(1)  # crawling with a delay
            crawl(link)


# Main function to start the crawl
def main():
    try:
        # Start from the homepage
        start_url = base_url
        crawl(start_url)
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user. Saving progress...")

    # Save the dataset to a JSON file
    output_file = 'fmi_full_site.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)

    print(f"Scraping complete. Data saved to '{output_file}'.")


if __name__ == '__main__':
    main()
