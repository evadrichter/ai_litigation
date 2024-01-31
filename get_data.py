from selenium import webdriver
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import time # beware sometimes time and datetime get confused
import numpy as np
from wordcloud import WordCloud
import requests


#AI litigation database
URL = "https://blogs.gwu.edu/law-eti/ai-litigation-database-search/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

time.sleep(2)  
page_source = driver.page_source # Get page html code
soup = BeautifulSoup(page_source, 'html.parser') # parse HTML code
table = soup.find('table', title='Data table') # find data table

links = [a['href'] for a in table.find_all('a')]
links_new = [item for item in links if item != "javascript:void(0);"]

df = pd.read_html(str(table))[0] 

df['Link'] = links_new

def extract_data_from_links(df, column_name, cellnumbers):
    extracted_data = {cellnumber: [] for cellnumber in cellnumbers}

    for link in df[column_name]:
        try:
            driver.get(link)
            # Fetch HTML content from the link
            page_source = driver.page_source 

            # Parse the HTML content
            soup = BeautifulSoup(page_source, 'html.parser')

            for cellnumber in cellnumbers:
                id = "cbFormBlock" + str(cellnumber) +"_"
                # Find all divs with class containing the specific ID
                divs = soup.find_all('div', class_=lambda value: value and id in value)

                # Extract text from each div and add to the respective list
                for div in divs:
                    extracted_data[cellnumber].append(div.get_text(strip=True))

        except requests.RequestException as e:
            print(f"Error fetching {link}: {e}")

    return extracted_data

# Define the cell numbers you want to scrape
cellnumbers = [14, 1, 2, 22]

# Scrape data with the modified function
extracted_data = extract_data_from_links(df, 'Link', cellnumbers)

# Now, extracted_data is a dictionary with keys being cell numbers 
# and values being lists of extracted texts for each cell number.
status = extracted_data[14]
ext_summary = extracted_data[1]

# Data cleaning:
ext_summary = [entry for entry in ext_summary if entry.startswith("Summary")]
sig_summary = extracted_data[2]
recent_activity = extracted_data[22]

df['Status'] = status
df["sig_summary"] = sig_summary
df["ext_summary"] = ext_summary
df["recent_activity"] = recent_activity

df.to_csv("data/litigation_ext.csv", encoding='utf-8')
