import time
import re
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- CONFIG ---
OUTPUT_FILE = "snapdeal.task1.csv"
TARGET_PER_SECTION = 100
SECTIONS = {
    "Accessories": "https://www.snapdeal.com/search?keyword=accessories",
    "Footwear": "https://www.snapdeal.com/search?keyword=footwear",
    "Kids Fashion": "https://www.snapdeal.com/search?keyword=kids%20fashion",
    "Men Clothing": "https://www.snapdeal.com/search?keyword=men%20clothing",
    "Women Clothing": "https://www.snapdeal.com/search?keyword=women%20clothing"
}

options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)


def get_num(text):
    return int(re.sub(r'[^\d]', '', text)) if text else 0


all_data = []

print(f"--- 🚀 STATUS: WEBSITE SCRAPPING STARTING FOR TASK 1 ---")

for section, url in SECTIONS.items():
    driver.get(url)
    time.sleep(3)

    # Infinite Scroll Logic
    last_count = 0
    while len(driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")) < TARGET_PER_SECTION:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        current = len(driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing"))
        print(f"   > Scrapping {section}... Items loaded: {current}")
        if current == last_count: break
        last_count = current

    products = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")
    for item in products[:TARGET_PER_SECTION]:
        try:
            p_raw = item.find_element(By.CSS_SELECTOR, "span.product-price").text
            m_raw = item.find_element(By.CSS_SELECTOR, "span.product-desc-price").text
            p, m = get_num(p_raw), get_num(m_raw)
            disc = round(((m - p) / m) * 100, 2) if m > 0 else 0

            all_data.append({
                "Product Name": item.find_element(By.CSS_SELECTOR, "p.product-title").text,
                "Section": section,
                "Price": p,
                "Discount": disc,
                "Rating": item.get_attribute("data-rating") or "0"
            })
        except:
            continue

pd.DataFrame(all_data).to_csv(OUTPUT_FILE, index=False)
print(f"--- ✅ SUCCESS: WEBSITE SCRAPPING FINISHED. OUTPUT SAVED AS {OUTPUT_FILE} ---")
driver.quit()