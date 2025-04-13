from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup headless driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# Open the database search page
url = "https://blogs.gwu.edu/law-eti/ai-litigation-database-search/"
driver.get(url)
time.sleep(2)

# Initialize storage
all_rows = []
all_links = []

# Jump through pages 1 to 5 using input box
for page in range(1, 6):
    print(f"🔄 Scraping page {page}...")

    input_xpath = '//*[@id="JumpToInputBottom_406c23d378a43c"]'
    time.sleep(1)
    # Wait until input is present
    input_box = driver.find_element(
        By.CSS_SELECTOR,
        "input.cbResultSetJumpToTextField[id^='JumpToInputBottom']"
    )

    input_box.clear()
    input_box.send_keys(str(page))
    input_box.send_keys(Keys.RETURN)
    time.sleep(2)  # wait for page load

    # Parse table
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', title='Data table')

    if table:
        df_page = pd.read_html(str(table))[0]
        all_rows.append(df_page)

        links = [
            a['href'] for a in table.find_all('a')
            if a.get('href') and a['href'] != "javascript:void(0);"
        ]
        all_links.extend(links)

# Combine all pages
df_full = pd.concat(all_rows, ignore_index=True)
df_full["Link"] = all_links

# ----------------------------------------
# Extract additional data from each case
# ----------------------------------------


# Fields to extract


# Export to CSV
df_full.to_csv("ai_litigation_full.csv", index=False, encoding='utf-8')
print("✅ Done! Saved to 'ai_litigation_full.csv'.")

driver.quit()
