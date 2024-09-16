# Ecommerce Product Scraper
# Copyright (c) 2023 Your Name
# Licensed under the MIT License

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
from pathlib import Path
import os
from requests.exceptions import RequestException, Timeout
import time
import re

# Configuration
BASE_URL = "https://example-ecommerce-site.com"
COLLECTIONS_URLS = [
    f"{BASE_URL}/collections/category1",
    f"{BASE_URL}/collections/category2",
    f"{BASE_URL}/collections/category3",
    # Add more collection URLs here
]
OUTPUT_DIR = Path("ecommerce_data")
IMAGES_DIR = OUTPUT_DIR / "images"

def setup_directories():
    """Create necessary directories for storing scraped data and images."""
    print("Setting up directories...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    print(f"Created directories: {OUTPUT_DIR} and {IMAGES_DIR}")

def get_product_urls(url, max_retries=3, timeout=10):
    """Fetch product URLs from a collection page."""
    print(f"Fetching product URLs from {url}...")
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            product_links = soup.find_all('a', class_='product-link')
            urls = list(set([urljoin(BASE_URL, link['href']) for link in product_links if '/products/' in link.get('href', '')]))
            print(f"Found {len(urls)} unique product URLs.")
            return urls
        except Timeout:
            print(f"Timeout occurred. Attempt {attempt + 1} of {max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2)
        except RequestException as e:
            print(f"Error fetching product URLs: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                time.sleep(2)
            else:
                print("Max retries reached. Unable to fetch product URLs.")
                return []
    
    print("Failed to fetch product URLs after multiple attempts.")
    return []

def download_image(url, product_name, max_retries=3, timeout=10):
    """Download and save product image."""
    print(f"Downloading image for {product_name} from {url}")
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            file_extension = os.path.splitext(url.split('?')[0])[1] or '.jpg'
            safe_name = ''.join(c if c.isalnum() else '_' for c in product_name)
            filename = IMAGES_DIR / f"{safe_name}{file_extension}"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"Successfully downloaded image: {filename}")
            return str(filename.relative_to(OUTPUT_DIR))
        except Timeout:
            print(f"Timeout occurred. Attempt {attempt + 1} of {max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                time.sleep(1)
            else:
                print("Max retries reached. Unable to download image.")
                return None
    
    print("Failed to download image after multiple attempts.")
    return None

def extract_text_or_none(soup, selector):
    """Extract text from a BeautifulSoup element or return None if not found."""
    element = soup.select_one(selector)
    return element.get_text(strip=True) if element else None

def extract_product_info(url):
    """Extract product information from a product page."""
    print(f"Extracting product info from {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        product_name = soup.find('meta', property='og:title')['content']
        product_image = soup.find('meta', property='og:image')['content']
        product_description = soup.find('meta', property='og:description')['content']
        price = extract_text_or_none(soup, 'span.price')
        
        product = {
            'name': product_name,
            'image_url': product_image,
            'description': product_description,
            'price': price if price else "Price not available",
            'url': url
        }

        return product
    except Exception as e:
        print(f"Error extracting product info from {url}: {e}")
        return None

def main():
    """Main function to orchestrate the scraping process."""
    setup_directories()
    
    all_products = []
    for collection_url in COLLECTIONS_URLS:
        print(f"\nProcessing collection: {collection_url}")
        max_retries = 3
        timeout = 10
        for attempt in range(max_retries):
            try:
                product_urls = get_product_urls(collection_url, max_retries, timeout)
                if product_urls:
                    break
            except Timeout:
                print(f"Timeout occurred. Attempt {attempt + 1} of {max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2)
            except RequestException as e:
                print(f"Error fetching collection URLs: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying... Attempt {attempt + 2} of {max_retries}")
                    time.sleep(2)
                else:
                    print("Max retries reached. Unable to fetch collection URLs.")
                    continue
        
        if not product_urls:
            print(f"Failed to fetch product URLs for collection: {collection_url}")
            continue
        
        for url in product_urls:
            product = extract_product_info(url)
            if product:
                # Download the image
                local_image_path = download_image(product['image_url'], product['name'])
                product['local_image_path'] = local_image_path
                all_products.append(product)
    
    print(f"\nSuccessfully scraped {len(all_products)} products from all collections.")
    
    # Save scraped data to JSON file
    json_file_path = OUTPUT_DIR / 'ecommerce_products.json'
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_products, json_file, indent=2, ensure_ascii=False)
    print(f"Data saved to {json_file_path}")

    # Print summary of scraped data
    print("\nSummary of scraped data:")
    print(f"Total products: {len(all_products)}")
    print(f"Products with images downloaded: {sum(1 for p in all_products if p.get('local_image_path'))}")
    if any(p.get('price') for p in all_products):
        prices = [float(p['price'].replace('$', '').strip()) for p in all_products if p.get('price') and p['price'] != "Price not available"]
        if prices:
            print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        else:
            print("No valid prices found.")
    else:
        print("No price information available.")
        
if __name__ == "__main__":
    main()