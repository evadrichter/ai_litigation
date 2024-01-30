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
from collections import Counter



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

df['link'] = links_new



st.title("AI litigation tracker")

#st.subheader('Raw data')
st.write(df)

st.subheader('Number of cases filed per year')

df['Date Action Filed'] = pd.to_datetime(df['Date Action Filed'], errors='coerce')
df['Year Filed'] = df['Date Action Filed'].dt.year

year_counts = df['Year Filed'].value_counts()

# Convert the Series to a DataFrame and reset index
year_freq_df = year_counts.reset_index()

# Rename columns to 'Year' and 'Frequency'
year_freq_df.columns = ['Year', 'Frequency']

# Sort the DataFrame by year in ascending order
year_freq_df = year_freq_df.sort_values(by='Year', ascending=True)

# Reset index if you want a clean index
year_freq_df = year_freq_df.reset_index(drop=True)

st.subheader("Cases filed per year")
st.bar_chart(data = year_freq_df, x= "Year", y="Frequency")

# # Splitting the keywords and counting their frequency
# keyword_series = df['Application Aresa'].str.split(', ')
# keyword_list = [keyword.strip() for sublist in keyword_series for keyword in sublist]
# keyword_counts = Counter(keyword_list)

# # Creating a bar plot
# fig, ax = plt.subplots()
# ax.bar(keyword_counts.keys(), keyword_counts.values())
# ax.set_xlabel('Keywords')
# ax.set_ylabel('Frequency')
# ax.set_title('Frequency of Keywords in Application Area')
# plt.xticks(rotation=45)

# # Display the plot in the Streamlit app
# st.pyplot(fig)