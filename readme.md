# Ecommerce Product Scraper

## Description
This project is an Ecommerce Product Scraper that extracts product information from specified ecommerce websites. It's designed to collect data such as product names, prices, descriptions, and images from multiple product collections especially for ai/ml model training.

## Features
- Scrapes product data from multiple collection URLs
- Handles timeouts and retries for robust scraping
- Saves product information in JSON format
- Downloads and saves product images
- Respects website's robots.txt and implements rate limiting

## Requirements
- Python 3.6+
- Required packages are listed in `requirements.txt`

## Installation
1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Configure the `BASE_URL` and `COLLECTIONS_URLS` in `main.py`
2. Run the script:
   ```
   python main.py
   ```
3. Scraped data will be saved in the `ecommerce_data` directory

## Configuration
- `BASE_URL`: The base URL of the ecommerce website
- `COLLECTIONS_URLS`: List of collection URLs to scrape
- `OUTPUT_DIR`: Directory to save scraped data (default: `ecommerce_data`)
- `IMAGES_DIR`: Directory to save downloaded images (default: `ecommerce_data/images`)

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer
This scraper is for educational purposes only. Always respect the website's robots.txt file and terms of service when scraping.
