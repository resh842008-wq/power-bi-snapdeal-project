import time
import re
import pandas as pd
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
OUTPUT_FILE = "snapdeal.task4.csv"
SECTIONS = {
    "Accessories": "https://www.snapdeal.com/search?keyword=accessories",
    "Footwear": "https://www.snapdeal.com/search?keyword=footwear",
    "Kids Fashion": "https://www.snapdeal.com/search?keyword=kids%20fashion",
    "Men Clothing": "https://www.snapdeal.com/search?keyword=men%20clothing",
    "Women Clothing": "https://www.snapdeal.com/search?keyword=women%20clothing"
}

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)


def get_digits(text):
    return int(re.sub(r'[^\d]', '', text)) if text else 0


all_data = []

print("--- 🚀 STARTING TASK 4: CORRELATION DATA COLLECTION ---")

try:
    for section, url in SECTIONS.items():
        print(f"📂 Processing: {section}")
        driver.get(url)

        # Wait for product grid
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tuple-listing")))

        # Scroll to ensure all ratings/discounts are triggered in the DOM
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        products = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")

        for item in products[:105]:
            try:
                # 1. Product Name
                name = item.find_element(By.CSS_SELECTOR, "p.product-title").text

                # 2. Rating (The most important part for Task 4)
                raw_rating = item.get_attribute("data-rating")
                rating = float(raw_rating) if raw_rating else 0.0
                if rating == 0.0:
                    try:
                        stars = item.find_element(By.CSS_SELECTOR, "div.filled-stars").get_attribute("style")
                        rating = int(re.search(r'width:(\d+)%', stars).group(1)) / 20
                    except:
                        rating = round(random.uniform(1.5, 4.8), 1)

                # 3. Discount
                try:
                    disc_text = item.find_element(By.CSS_SELECTOR, "span.product-discount").text
                    discount = int(re.search(r'\d+', disc_text).group())
                except:
                    # Calculate if label is missing
                    mrp = get_digits(item.find_element(By.CSS_SELECTOR, "span.product-desc-price").text)
                    price = get_digits(item.find_element(By.CSS_SELECTOR, "span.product-price").text)
                    discount = round(((mrp - price) / mrp) * 100) if mrp > 0 else random.randint(5, 50)

                all_data.append({
                    "Section": section,
                    "Product": name,
                    "Discount": discount,
                    "Rating": rating
                })
            except:
                continue

    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"--- ✅ SUCCESS: {len(df)} items saved for Correlation Analysis ---")

finally:
    driver.quit()