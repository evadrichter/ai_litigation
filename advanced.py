from selenium import webdriver
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import time # beware sometimes time and datetime get confused
import streamlit as st
import numpy as np
from wordcloud import WordCloud
import requests


#AI litigation database
URL = "https://blogs.gwu.edu/law-eti/ai-litigation-database-search/"

# @st.cache_data
# def load_data(url):
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

df = pd.read_html(str(table))[0] # parse html table to pandas table
    # return df

df['Link'] = links_new


def extract_text_from_links(df, column_name):
    extracted_texts = []

    for link in df[column_name]:
        try:
            driver.get(link)
            # Fetch HTML content from the link
            page_source = driver.page_source 

            # Parse the HTML content
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find all divs with class containing 'cbFormBlock14'
            divs = soup.find_all('div', class_=lambda value: value and 'cbFormBlock14' in value)

            # Extract text from each div and add to the list
            for div in divs:
                extracted_texts.append(div.get_text(strip=True))

        except requests.RequestException as e:
            print(f"Error fetching {link}: {e}")

    return extracted_texts

status = extract_text_from_links(df, 'Link')

df['Status'] = status

df.to_csv("litigation_ext.csv", encoding='utf-8')

#df = load_data(URL)

# print(df)

# st.title("AI litigation tracker")

# st.subheader('Raw data')
# st.write(df)

# st.subheader('Number of cases filed per year')

# df['Date Action Filed'] = pd.to_datetime(df['Date Action Filed'], errors='coerce')
# df['Year Filed'] = df['Date Action Filed'].dt.year

# year_counts = df['Year Filed'].value_counts()

# # Convert the Series to a DataFrame and reset index
# year_freq_df = year_counts.reset_index()

# # Rename columns to 'Year' and 'Frequency'
# year_freq_df.columns = ['Year', 'Frequency']

# # Sort the DataFrame by year in ascending order
# year_freq_df = year_freq_df.sort_values(by='Year', ascending=True)

# # Reset index if you want a clean index
# year_freq_df = year_freq_df.reset_index(drop=True)

# st.subheader("Cases filed per year")
# st.bar_chart(data = year_freq_df, x= "Year", y="Frequency")



