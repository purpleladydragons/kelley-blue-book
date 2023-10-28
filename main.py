import json
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc

FILE_NAME = "car_listings.json"

scraped_urls = set()

# If the file already exists, load the URLs into the set
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as file:
        for line in file:
            listing = json.loads(line.strip())
            scraped_urls.add(listing["url"])

chrome_options = Options()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
chrome_options.add_argument(f"user-agent={USER_AGENT}")
driver = uc.Chrome(options=chrome_options)

BASE_URL = "https://www.kbb.com/cars-for-sale/all/toyota/{}/los-angeles-ca?endYear=2022&firstRecord={}&isNewSearch=false&numRecords=100&startYear=2016&zip=90025"

MODELS = ["camry", "rav4"]
# MODELS = ["accord", "cr-v"]
YEARS = range(2016, 2022)


def slow_scroll_and_load_more(driver, scroll_pause_time=1):
    """
    Slowly scroll the page and click the "Load More Vehicles" button whenever it's available.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        print('scrolling')
        # Scroll down step by step
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(scroll_pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

results = []

for pg in (0, 5):
    for model in MODELS:
        driver.get(BASE_URL.format(model, pg*100))
        slow_scroll_and_load_more(driver)

        listings = driver.find_elements(By.CSS_SELECTOR, ".item-card-body")
        for listing in listings:
            try:
                title = listing.find_element(By.CSS_SELECTOR, "h3[data-cmp='subheading']").text
                link = listing.find_element(By.CSS_SELECTOR, "a[data-cmp='link']").get_attribute('href')
                mileage = listing.find_element(By.CSS_SELECTOR, ".item-card-specifications span.text-bold").text
                price = listing.find_element(By.CSS_SELECTOR, "span[data-cmp='firstPrice']").text

                results.append({
                    "Title": title,
                    "Link": link,
                    "Mileage": mileage,
                    "Price": price,
                })

                print(results[-1])

                miles_int = int("".join(filter(str.isdigit, mileage)))
                price_int = int("".join(filter(str.isdigit, price)))

                if link not in scraped_urls:
                    data = {
                        "url": link,
                        "title": title,
                        "model": model,
                        "miles": miles_int,
                        "price": price_int,
                    }

                    with open(FILE_NAME, "a") as file:
                        file.write(json.dumps(data) + "\n")

                scraped_urls.add(link)
            except Exception as e:
                print(f"Error while processing listing: {e}")

driver.close()

for result in results:
    print(result)
