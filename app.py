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
import altair as alt
import folium


df = pd.read_csv("litigation_ext.csv")

st.title("AI Litigation Tracker")

st.write("With this tool, you will be able to track all past and ongoing AI litigation, including litigation against machine learning algorithms. The data was obtained from Georgetown Law’s AI Litigation Database (https://blogs.gwu.edu/law-eti/ai-litigation-database-search/).")

with st.sidebar:
    st.title("Track AI Litigation")
    pages = ["Track AI Litigation", "Explore Issues", "Explore Active Cases" ,"Explore Settled Cases"]
    selected_page = st.sidebar.radio("Select Page", pages)
    #st.sidebar.text("AI Litigation Database – Search. \n URL: https://blogs.gwu.edu/law-eti/ai-litigation-database-search/. \n Last accessed on 1/30/2024")
    citation_html = """
    <div style="position: fixed; top: 60px; left: 20px;">
    AI Litigation Database  </div>

"""
    feedback_html = """
<div style="position: fixed; bottom: 20px; left: 20px;">
    <a href="mailto:evarichter@hks.harvard.edu" style="text-decoration: none;">
        <button style="background-color: #6200ff; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
            Got any feedback?
        </button>
    </a>
</div>
"""
    st.sidebar.markdown(citation_html, unsafe_allow_html=True)
    st.sidebar.markdown(feedback_html, unsafe_allow_html=True)

# Create content for each page
if selected_page == "Track AI Litigation":

    # Add content for Page 1

    st.header('When have cases against AI been filed?', divider='gray')

    # Preprocessing: getting year
    df['Date Action Filed'] = pd.to_datetime(df['Date Action Filed'], errors='coerce')
    df['Year Filed'] = df['Date Action Filed'].dt.year

    def num_cases(column):
        counts = column.value_counts()
        freq = counts.reset_index()
        freq.columns = ["Year", "Frequency"]
        freq = freq.sort_values(by='Year', ascending=True)
        freq = freq.reset_index(drop=True)
        return freq

    year_freq_df = num_cases(df['Year Filed'])

    st.bar_chart(data = year_freq_df, x= "Year", y="Frequency", color="#6200ff")

    st.header('Which algorithms have been sued?', divider='gray')

    algorithm = df['Algorithm'].str.split(', ')
    algorithm = algorithm.dropna()
    algo_list = [keyword.strip() for sublist in algorithm for keyword in sublist]

    algo_list = pd.Series(algo_list)

    value_counts = algo_list.value_counts()
    # Identify values that occur only once
    single_occurrences = value_counts[value_counts == 1].index
    # Replace these values with 'Other' in the original DataFrame
    algo_list = algo_list.replace(single_occurrences, 'Other')

    # Recalculate value counts
    counts = algo_list.value_counts()
    freq = counts.reset_index()
    freq.columns = ["Algorithm", "Frequency"]
    freq = freq.reset_index(drop=True)
    freq = freq.sort_values(by='Algorithm', ascending=False)
    #st.bar_chart(data = freq, x= "Algorithm", y="Frequency", color="#6200ff")



    chart = alt.Chart(freq).mark_bar(color='#6200ff').encode(
            x=alt.X('Algorithm', sort='-y'),
            y='Frequency'
        )

        # Display the chart in the Streamlit app
    st.altair_chart(chart, use_container_width=True)


        # Create a Pie Chart

        # Create a Pie Chart
    piechart = alt.Chart(freq).mark_arc().encode(
        theta=alt.Theta(field='Frequency', type='quantitative', stack = "normalize"),
        color=alt.Color(field='Algorithm', type='nominal', sort = "ascending"),
        order=alt.Order(field='Frequency', type= 'quantitative', sort = "ascending"), 
        tooltip=['Algorithm', 'Frequency']
    )

    # Display the Layered Chart in the Streamlit app
    st.altair_chart(piechart, use_container_width=True)

    st.header('How have cases been resolved?', divider='gray')

    counts = df["Status"].value_counts()
    freq = counts.reset_index()
    freq.columns = ["Status", "Frequency"]
    freq = freq.sort_values(by='Status', ascending=True)
    freq = freq.reset_index(drop=True)


    chart = alt.Chart(freq).mark_bar(color='#6200ff').encode(
            y=alt.Y('Status:N', axis=alt.Axis(title='Status', labelAngle=0)),
            x='Frequency:Q' # Quantitative data for x-axis
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            labelFontSize=12,  # Adjust label font size as needed
            titleFontSize=12
        ).configure_axisLeft(
            labelPadding=10  # Increase padding for the y-axis labels
        )


        # Display the chart in the Streamlit app
    st.altair_chart(chart, use_container_width=True)


    # Radio button for selection

    

    

elif selected_page == "Explore Issues":
    df["Issues"] = df["Issues"].fillna("")
    expressions = df["Issues"].str.lower().str.split(', ')
    all_expressions = ' '.join([expression for expressions_list in expressions for expression in expressions_list])
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_expressions)

    # Display the word cloud using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Word Cloud")
    
    st.pyplot()

    issues = df['Issues'].str.split(', ')
    issue_list = [keyword.strip() for sublist in issues for keyword in sublist]
    
    unique_issues = set(issue_list)
    unique_issues = sorted(unique_issues)
    # Create a multiselect widget to select issues
    selected_issue = st.selectbox("Select Issues", unique_issues)
    
    # Filter the DataFrame based on selected issues
    filtered_df = df[df['Issues'].str.contains(selected_issue, case=False, na=False)]



    
    # Display the filtered DataFrame
    st.write("Filtered cases in a table:")
    st.write(filtered_df[["Caption", "Brief Description", "Algorithm", "Jurisdiction", "Application Areas", "Cause of Action", "Date Action Filed", "Link", "Status"]])

    st.write("More details on filtered cases: :")
    # Display each row as Markdown
    for index, row in filtered_df.iterrows():
        st.write(f"## {row['Caption']}")
        st.write(f"**Brief Description:** {row['Brief Description']}")
        st.write(f"**Algorithm:** {row['Algorithm']}")
        st.write(f"**Jurisdiction:** {row['Jurisdiction']}")
        st.write(f"**Application Areas:** {row['Application Areas']}")
        st.write(f"**Cause of Action:** {row['Cause of Action']}")
        st.write(f"**Date Action Filed:** {row['Date Action Filed']}")
        st.write(f"**Find our more:** {row['Link']}")
        st.write(f"**Status:** {row['Status']}")
        st.markdown("---")  # Add a horizontal line between rows

elif selected_page == "Explore Active Cases":
    st.header('Explore active cases only, sorted my most recent activity', divider='gray')

    status_selection = st.radio("Select Status", ('Active', 'Not Active'))

    # Filter DataFrame based on selection
    if status_selection == 'Active':
        filtered_df = df[df['Status'] == 'Active']
    else:
        filtered_df = df[df['Status'] != 'Active']

    # Display the filtered DataFrame
    st.write(filtered_df)

elif selected_page == "Explore Settled Cases":
    st.title("Explore settled cases")
    st.header('Explore settled cases', divider='gray')

    df['Status'] = df['Status'].fillna('')
    df['Settled'] = df['Status'].apply(lambda x: 1 if 'settle' in x.lower() else 0)

    filtered_df = df[df['Settled'] == 1]
    filtered_df = filtered_df[["Caption", "Brief Description", "Algorithm", "Jurisdiction", "Application Areas", "Cause of Action", "Issues", "Link"]]

    #st.write(filtered_df)

        # Create a list of captions for the table of contents
    captions = filtered_df['Caption'].tolist()

        # Display each row as a hyperlink in the table of contents
    for caption in captions:
        # Create a hyperlink with the caption as text and link to the corresponding section
        st.write(f"<a href='#{caption.replace(' ', '-')}'>{caption}</a>", unsafe_allow_html=True)

    st.write("---")  # Separator between table of contents and content

    # Display each row as Markdown text with caption as section anchor
    for index, row in filtered_df.iterrows():
        # Use Caption as the anchor for the section
        st.markdown(f"## {row['Caption']}")
        # Display other columns as text
        st.write(f"**Brief Description:** {row['Brief Description']}")
        st.write(f"**Algorithm:** {row['Algorithm']}")
        st.write(f"**Jurisdiction:** {row['Jurisdiction']}")
        st.write(f"**Application Areas:** {row['Application Areas']}")
        st.write(f"**Cause of Action:** {row['Cause of Action']}")
        st.write(f"**Issues:** {row['Issues']}")
        st.write(f"**Find out more:** {row['Link']}")
        st.write("---")  # Separator between entries

