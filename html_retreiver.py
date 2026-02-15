import time
import re
from datetime import datetime
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ===================== CONFIG =====================
OUTPUT_CSV = "snapdeal_products.csv"
HEADLESS = True
WAIT_TIME = 10
MAX_PRODUCTS_PER_SUBCAT = 10

BASE_SECTIONS = {
    "Accessories": "https://www.snapdeal.com/search?keyword=accessories&sort=rlvncy",
    "Footwear": "https://www.snapdeal.com/search?keyword=footwear&sort=rlvncy",
    "Kids Fashion": "https://www.snapdeal.com/search?keyword=kids%20fashion&sort=rlvncy",
    "Men Clothing": "https://www.snapdeal.com/search?keyword=men%20clothing&sort=rlvncy",
    "Women Clothing": "https://www.snapdeal.com/search?keyword=women%20clothing&sort=rlvncy",
}
# ==================================================


# ---------- DRIVER SETUP ----------
def create_driver():
    chrome_opts = Options()

    if HEADLESS:
        chrome_opts.add_argument("--headless=new")

    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")

    chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_opts)
    driver.set_page_load_timeout(30)
    return driver


driver = create_driver()
wait = WebDriverWait(driver, WAIT_TIME)


# ---------- HELPER FUNCTIONS ----------
def clean_int(text):
    if not text:
        return 0
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else 0


def parse_rating_from_style(style):
    if not style:
        return ""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", style)
    if not m:
        return ""
    pct = float(m.group(1))
    return round(pct / 20, 1)


def safe_find(parent, selector, attr=None):
    try:
        el = parent.find_element(By.CSS_SELECTOR, selector)
        return el.get_attribute(attr) if attr else el.text.strip()
    except:
        return ""


# ---------- SAFE PAGE LOAD ----------
def safe_get(url):
    global driver
    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
    except Exception as e:
        print("⚠ Browser crashed. Restarting driver...")
        try:
            driver.quit()
        except:
            pass
        driver = create_driver()
        driver.get(url)
        time.sleep(3)


# ---------- SCRAPE PRODUCTS ----------
def scrape_listing(section, subcat):
    rows = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")

    for card in cards[:MAX_PRODUCTS_PER_SUBCAT]:
        name = safe_find(card, "p.product-title")
        price = safe_find(card, "span.product-price")
        rating_style = safe_find(card, ".filled-stars", "style")
        rating = parse_rating_from_style(rating_style)
        img = safe_find(card, "img", "src")
        url = safe_find(card, "a", "href")

        rows.append({
            "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Section": section,
            "Subcategory": subcat,
            "Product Name": name,
            "Price": price,
            "Rating": rating,
            "Image URL": img,
            "Product URL": url
        })

    return rows


# ===================== MAIN =====================
all_rows = []

for section, url in BASE_SECTIONS.items():
    print(f"\n=== Scraping {section} ===")
    safe_get(url)

    rows = scrape_listing(section, section)
    all_rows.extend(rows)


# ---------- SAVE CSV ----------
df = pd.DataFrame(all_rows)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"\n✅ DONE! File saved as: {OUTPUT_CSV}")

driver.quit()
