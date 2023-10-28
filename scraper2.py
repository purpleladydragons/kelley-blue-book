import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json

import time
import json


def scrape_car_data(model, hybrid=False):
    base_url = "https://www.kbb.com/cars-for-sale/all/"
    if hybrid:
        base_url += "hybrid/"
    else:
        base_url += "gasoline/"
    base_url += f"{model}/los-angeles-ca?endYear=2022&isNewSearch=true&numRecords=100&startYear=2016&zip=90025"

    # Setting up undetected_chromedriver to prevent detection
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    browser = uc.Chrome(options=options)

    listings = []
    for i in range(3):  # To cover first 300 records
        issues = 0
        print('onto page', i)
        current_url = base_url + f"&firstRecord={i * 100}"
        browser.get(current_url)
        time.sleep(5)  # Wait for the page to load

        results = browser.find_elements(By.CSS_SELECTOR, ".item-card-body")
        print('found', len(results), 'results')
        for result in results:
            listing_data = {}
            # Extract the required information
            try:
                listing_data['title'] = result.find_element(By.CSS_SELECTOR, "h3[data-cmp='subheading']").text
                listing_data['link'] = result.find_element(By.CSS_SELECTOR, "a[data-cmp='link']").get_attribute('href')
                listing_data['mileage'] = result.find_element(By.CSS_SELECTOR, ".item-card-specifications .text-bold").text
                listing_data['price_text'] = result.find_element(By.CSS_SELECTOR, "span[data-cmp='firstPrice']").text
                listing_data["price"] = int(listing_data['price_text'].replace("$", "").replace(",", ""))
                listing_data["model"] = model.split("/")[1]
                listing_data["year"] = int(listing_data["title"].split(" ")[1])  # Extracting year from title
                listing_data["miles"] = int(listing_data['mileage'].replace(',', '').replace(' miles', ''))

                # Add the hybrid field
                listing_data['hybrid'] = hybrid
                listings.append(listing_data)
            except Exception as e:
                issues += 1
                # For this example, we'll simply print the error and continue
                print(f"Error processing a listing ({issues}): {e}")

    print('scraped', len(listings), 'so far')

    browser.quit()
    return listings


# Scrape data
models = ["honda/accord", "honda/cr-v", "toyota/rav4", "toyota/camry"]
all_data = []

for model in models:
    print('scraping', model)
    # Fetch non-hybrid data
    all_data.extend(scrape_car_data(model, hybrid=False))

    # Fetch hybrid data
    all_data.extend(scrape_car_data(model, hybrid=True))

# Saving to a single JSON file
with open("all_car_listings.json", "w") as f:
    json.dump(all_data, f)

print("Scraping complete!")