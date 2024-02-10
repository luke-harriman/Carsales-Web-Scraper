from playwright.sync_api import sync_playwright
import json
import time 
import random
import logging
import requests
from mlscraper.html import Page
from mlscraper.samples import Sample, TrainingSet
from mlscraper.training import train_scraper
from datetime import datetime
from playwright_stealth import stealth_sync
import pprint as pp
import regex as re 
from datetime import datetime
import zlib

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.88 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.88 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/73.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; SM-G950F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.0; SM-G930F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 4.4; en-us; Nexus 5 Build/KRT16M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.4 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; CrOS x86_64 13099.110.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.136 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
]

def load_auth():
    # Load the proxy configuration from auth.json
    with open("auth.json", "r") as f:
        return json.load(f)
    
def log_message(message):
    # Custom logging for detailed debugging information
    print(f"{datetime.now()} - {message}")

def fetch_page_with_playwright(url):
    cred = load_auth()
    proxy_details = {
        "server": f'http://{cred["host"]}',
        "username": cred["username"],
        "password": cred["password"]
    }
    user_agent = random.choice(user_agents)


    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--user-agent={}'.format(user_agent),
            ],
        )

        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': random.randint(1280, 1920), 'height': random.randint(720, 1080)},
            geolocation={'latitude': -27.470125, 'longitude': 153.021072},
            permissions=['geolocation'],
            proxy=proxy_details
        )
        page = browser.new_page()
        stealth_sync(page)

        page.on('response', lambda response: log_message(f'Response: {response.url} - {response.status}'))


        page.add_init_script("""
        const Plugins = [
            {
                name: 'PDF Viewer',
                filename: 'pdf_viewer_plugin',
                description: 'Handle PDF files',
                length: 1,
            },
            {
                name: 'Flash Player',
                filename: 'flash_player_plugin',
                description: 'Legacy web video player',
                length: 1,
            },
        ];
        Object.defineProperty(navigator, 'plugins', { get: () => Plugins });

        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : originalQuery(parameters)
        );
        """)

        log_message("Navigating to URL")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(random.uniform(1, 3))
        page.mouse.move(random.randint(100, 500), random.randint(100, 500))


        time.sleep(random.uniform(1, 3))
        page.reload(wait_until="domcontentloaded", timeout=60000)

        time.sleep(random.uniform(1, 3))
        print(page.content())


        card_body_elements = page.query_selector_all('.card-body')
        
        detailed_listings = []
        for element in card_body_elements:
            details = {}
            title_element = element.query_selector('h3 a')
            title = title_element.text_content().strip() if title_element else "Title not found"
            details['title'] = title

            price_element = element.query_selector('.item-price .price a')
            price = price_element.text_content().strip() if price_element else "Price not found"
            details['price'] = price

            for detail in element.query_selector_all('.key-details__value'):
                detail_type = detail.get_attribute('data-type')
                detail_value = detail.text_content().strip()
                details[detail_type] = detail_value
            
            if details['title'] == "Title not found":
                continue
            elif details['price'] == "Price not found":
                continue
            else: 
                detailed_listings.append(details)

        


        # Close the browser after scraping
        browser.close()
        
        return detailed_listings

def extract_year_brand_model(title):
    match = re.match(r'^(\d{4})\s+([\w\-]+)\s+(.*)', title)
    if match:
        year, brand, rest = match.groups()
        model = rest.split()[0]  # Assuming the model is the first word after brand
        return year, brand, model
    return None, None, None

def parse_fuel_type(engine_description, title):
    if 'Electric' in engine_description or 'Electric' in title:
        return 'Electric'
    elif 'Diesel' in engine_description or 'Diesel' in title:
        return 'Diesel'
    elif 'Hybrid' in engine_description or 'Hybrid' in title:
        return 'Hybrid'
    elif 'Petrol' in engine_description or 'Petrol' in title:
        return 'Petrol'
    else:
        return None

def engine_details(engine_description, transmission, fuel_type):
    # Initialize variables to None for clarity and to avoid reference before assignment.
    engine_cylinders = engine_capacity = turbo = electric_capacity_kw = electric_range = None

    if fuel_type == 'Electric':
        electric_capacity_kw_match = re.search(r'(\d+(\.\d+)?)kW', transmission)
        electric_range_match = re.search(r'(\d+(\.\d+)?) km', engine_description)
        electric_capacity_kw = float(electric_capacity_kw_match.group(1)) if electric_capacity_kw_match else None
        electric_range = float(electric_range_match.group(1)) if electric_range_match else None

    elif fuel_type in ['Diesel', 'Petrol']:
        engine_cylinders_match = re.search(r'(\d+(\.\d+)?)cyl', engine_description)
        engine_capacity_match = re.search(r'(\d+(\.\d+)?)L', engine_description)
        engine_cylinders = float(engine_cylinders_match.group(1)) if engine_cylinders_match else None
        engine_capacity = float(engine_capacity_match.group(1)) if engine_capacity_match else None
        turbo = 1 if 'Turbo' in engine_description else 0

    elif fuel_type == 'Hybrid':
        electric_capacity_kw_match = re.search(r'(\d+(\.\d+)?)kW', engine_description)
        electric_capacity_kw = float(electric_capacity_kw_match.group(1)) if electric_capacity_kw_match else None
        engine_capacity_match = re.search(r'^(\d+(\.\d+)?)[a-zA-Z]*/', engine_description)
        engine_capacity = float(engine_capacity_match.group(1)) if engine_capacity_match else None

    # Return a tuple with the extracted or computed values.
    return engine_cylinders, engine_capacity, turbo, electric_capacity_kw, electric_range


def transform_data_to_new_schema(original_data):
    transformed_data = []
    for item in original_data:
        year, brand, model = extract_year_brand_model(item['title'])
        fuel_type = parse_fuel_type(item.get('Engine', ''), item['title'])
        engine_cylinders, engine_capacity, turbo, electric_capacity_kw, electric_range = engine_details(item.get('Engine', ''), item.get('Transmission', ''), fuel_type)

        car_details_str = f"{year}{brand}{model}{item.get('Body Style', '')}{item.get('Odometer', '0 km')}{item.get('Transmission', '')}{fuel_type}{item.get('Engine', '')}{item.get('price', '$0')}"
        vehicle_id_hash = zlib.crc32(car_details_str.encode()) & 0xffffffff  # Ensure positive CRC32 values

        new_item = {
            "VehicleID": vehicle_id_hash,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "car_description": item['title'],
            "year": float(year) if year else None,
            "brand": brand,
            "model": model,
            "body_style": item.get('Body Style', ''),
            "odometer": float(item.get('Odometer', '0 km').split()[0].replace(',', '')),
            "transmission": 'Automatic' if fuel_type == 'Electric' or 'Auto' in item['title'] else item.get('Transmission', ''),
            "fuel_type": fuel_type,
            "engine_description": item.get('Transmission', '') if fuel_type == 'Electric' else item.get('Engine', ''),
            "price":  float(re.sub(r'[^\d.]+', '', (item.get('price', '$0').replace('$', '').replace(',', '')))),
            "engine_cylinders": engine_cylinders,
            "engine_capacity": engine_capacity,
            "turbo": turbo,
            "electric_capacity_kw": electric_capacity_kw,
            "electric_range": electric_range,
        }
        transformed_data.append(new_item)
    return transformed_data

# The URL you want to scrape
url = 'https://www.carsales.com.au/cars/dealer/queensland-state/brisbane-region/electric-fueltype/'
page_content = fetch_page_with_playwright(url)
pp.pprint(page_content)
transformed_data = transform_data_to_new_schema(page_content)
pp.pprint(transformed_data)
