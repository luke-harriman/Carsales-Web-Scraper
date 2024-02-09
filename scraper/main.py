from playwright.sync_api import sync_playwright
import json
import time 
import random
import logging
import requests
from mlscraper.html import Page
from mlscraper.samples import Sample, TrainingSet
from mlscraper.training import train_scraper



def load_auth():
    # Load the proxy configuration from auth.json
    with open("auth.json", "r") as f:
        return json.load(f)
    
def fetch_page_with_playwright(url):
    cred = load_auth()
    proxy_details = {
        "server": f'http://{cred["host"]}',
        "username": cred["username"],
        "password": cred["password"]
    }
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(proxy=proxy_details, user_agent=user_agent)
        page = browser.new_page()
        # Navigate to the initial URL
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        # Wait for a random time between 2 and 5 seconds
        time.sleep(random.uniform(2, 5))
        # Refresh the page to potentially get the dynamic content
        page.reload(wait_until="domcontentloaded", timeout=60000)
        # Wait again for a random time to mimic human behavior
        time.sleep(random.uniform(2, 5))
        print(page.content())
        json_data_elements = page.query_selector_all('script[type="application/ld+json"]')

        # Extract the JSON content from each script tag
        json_data_list = []
        for element in json_data_elements:
            content = element.inner_text()
            # Parse the JSON data and append it to a list
            try:
                json_data = json.loads(content)
                json_data_list.append(json_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

        browser.close()

        return json_data_list

# The URL you want to scrape
url = 'https://www.carsales.com.au/cars/?q=(And.Service.carsales._.(C.State.Queensland._.Region.Brisbane.)_.(C.CertifiedInspected.Certified._.SubCertifiedInspected.Nissan%20Certified%20Pre-Owned.))'
page_content = fetch_page_with_playwright(url)
print(page_content)
# Create a Page object
