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
def extract_data_from_links(links, cellnumbers):
    extracted = {num: [] for num in cellnumbers}

    for link in links:
        try:
            driver.get(link)
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            for num in cellnumbers:
                class_id = f"cbFormBlock{num}_"
                divs = soup.find_all('div', class_=lambda val: val and class_id in val)

                if divs:
                    text = divs[0].get_text(strip=True)
                else:
                    text = ""

                extracted[num].append(text)

        except Exception as e:
            print(f"⚠️ Error loading {link}: {e}")
            for num in cellnumbers:
                extracted[num].append("")

    return extracted

# Fields to extract
cellnumbers = [14, 1, 2, 22]
extracted = extract_data_from_links(df_full["Link"], cellnumbers)

# Clean and assign to DataFrame
df_full['Status'] = extracted[14]
df_full['Case_Title'] = extracted[1]
df_full['Summary_of_Significance'] = [
    txt if txt.startswith("Summary") else "" for txt in extracted[2]
]
df_full['Recent_Activity'] = extracted[22]

# Export to CSV
df_full.to_csv("ai_litigation_full.csv", index=False, encoding='utf-8')
print("✅ Done! Saved to 'ai_litigation_full.csv'.")

driver.quit()
