
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from wordcloud import WordCloud
import altair as alt
import us
import plotly.express as px
import json

st.set_option('deprecation.showPyplotGlobalUse', False)


df = pd.read_csv("litigation_ext.csv")

st.title("AI Litigation Tracker")

st.write("With this tool, you will be able to track all past and ongoing AI litigation, including litigation against machine learning algorithms. The data was obtained from Georgetown Law’s AI Litigation Database (https://blogs.gwu.edu/law-eti/ai-litigation-database-search/).")

with st.sidebar:
    st.title("Track AI Litigation")
    pages = ["Track AI Litigation","Most recent activity" , "Explore Issues","Explore Settled Cases", "Explore Locations"]
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

    st.header('AI Disputes Reached Record Levels in 2023', divider='gray')

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

    st.header('Clearview AI and ChatGPT Top the List of Most-Sued Algorithms', divider='gray')

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

    st.header('Most cases are still ongoing', divider='gray')
    df['Status'] = df['Status'].fillna("")
    def categorize_status(status):
        if status == "Active":
            return 'Active'
        if "Settle" in status:
            return "Settled"
        elif 'Inactive' in status:
            return 'Inactive'
        elif 'Withdrawn' in status:
            return 'Withdrawn'
        elif 'Closed' in status:
            return 'Closed'
        elif "Active" in status:
            return "Active"
        elif status == "":
            return "Not specified"
        else:
            return 'Unknown'  # Handle other cases if needed

    # Apply the categorize_status function to create the "Status_Cat" column
    df['Status_Cat'] = df['Status'].apply(categorize_status)

    # Radio button for selection
    #st.write(df)
        
    # Calculate the value counts of each category
    value_counts = df['Status_Cat'].value_counts().reset_index()
    value_counts.columns = ['Status', 'Count']
    # Create a pie chart using Vega-Lite
    piechart2 = alt.Chart(value_counts).mark_arc().encode(
        theta=alt.Theta(field='Count', type='quantitative', stack = "normalize"),
        color=alt.Color(field='Status', type='nominal', sort = "ascending"),
        order=alt.Order(field='Count', type= 'quantitative', sort = "ascending"), 
        tooltip=['Status', 'Count']
    )

    # Display the pie chart using Altair
    st.altair_chart(piechart2, use_container_width=True)



elif selected_page == "Explore Issues":
    st.header("What issues are at stake?")
    df["Issues"] = df["Issues"].fillna("")
    expressions = df["Issues"].str.lower().str.split(', ')
    all_expressions = ' '.join([expression for expressions_list in expressions for expression in expressions_list])
    wordcloud = WordCloud(font_path="AbhayaLibre-Regular.ttf", width=800, height=400, background_color="white", colormap="magma").generate(all_expressions)

    # Display the word cloud using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud)
    plt.axis("off")

    
    st.pyplot()

    issues = df['Issues'].str.split(', ')
    issue_list = [keyword.strip() for sublist in issues for keyword in sublist]
    
    unique_issues = set(issue_list)
    unique_issues = sorted(unique_issues)
    # Create a multiselect widget to select issues
    st.subheader("Explore cases by issue:")
    selected_issue = st.selectbox("Filter by issue",unique_issues,index=1)
    
    # Filter the DataFrame based on selected issues
    filtered_df = df[df['Issues'].str.contains(selected_issue, case=False, na=False)]



    
    # Display the filtered DataFrame
    st.subheader("Explore selected cases in table form:")
    st.write(filtered_df[["Caption", "Brief Description", "Algorithm", "Jurisdiction", "Application Areas", "Cause of Action", "Date Action Filed", "Link", "Status"]])

    st.subheader("Explore selected cases in more detail:")
    # Display each row as Markdown
    for index, row in filtered_df.iterrows():
        st.write(f"## {row['Caption']}")
        st.write(f"**Brief Description:** {row['Brief Description']}")
        st.write(f"**Algorithm:** {row['Algorithm']}")
        st.write(f"**Jurisdiction:** {row['Jurisdiction']}")
        st.write(f"**Application Areas:** {row['Application Areas']}")
        st.write(f"**Cause of Action:** {row['Cause of Action']}")
        st.write(f"**Date Action Filed:** {row['Date Action Filed']}")
        st.write(f"**Find out more:** {row['Link']}")
        st.write(f"**Status:** {row['Status']}")
        st.markdown("---")  # Add a horizontal line between rows

elif selected_page == "Most recent activity":
    st.header('Explore cases with the most recent activity', divider='gray')
    df["Algorithm"] = df["Algorithm"].fillna("N/A")
    df['New Activity'] = pd.to_datetime(df['New Activity'], errors='coerce')
    df_sorted = df.sort_values(by='New Activity', ascending=False)
    top_10_cases = df_sorted.head(10)
    for index, row in top_10_cases.iterrows():
        st.write(f"### **New Activity:** {row['New Activity'].strftime('%B %dth %Y')}")
        st.write(f"### {row['Caption']}")
        st.write(f"**Brief Description:** {row['Brief Description']}")
        st.write(f"**Algorithm:** {row['Algorithm']}")
        st.write(f"**Jurisdiction:** {row['Jurisdiction']}")
        st.write(f"**Application Areas:** {row['Application Areas']}")
        st.write(f"**Cause of Action:** {row['Cause of Action']}")
        st.write(f"**Date Action Filed:** {row['Date Action Filed']}")
        st.write(f"**Find out more:** {row['Link']}")
        st.write(f"**Status:** {row['Status']}")
        st.markdown("---") 



elif selected_page == "Explore Settled Cases":
    st.header('Explore settled cases', divider='gray')

    df['Status'] = df['Status'].fillna('')
    df['Settled'] = df['Status'].apply(lambda x: 1 if 'settle' in x.lower() else 0)

    filtered_df = df[df['Settled'] == 1]
    filtered_df = filtered_df[["Caption", "Brief Description", "Algorithm", "Jurisdiction", "Application Areas", "Cause of Action", "Issues", "Link"]]

    #st.write(filtered_df)

        # Create a list of captions for the table of contents

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

elif selected_page == "Explore Locations":
    st.header('Where have cases been filed (only includes US locations)?', divider='gray')
# Function to classify the place based on the jurisdiction
    def classify_place(jurisdiction):
        if 'international' in jurisdiction.lower():
            return 'International'
        elif "cook county" in jurisdiction.lower():
            return "Illinois"
        elif "ca." in jurisdiction.lower() or "cal" in jurisdiction.lower():
            return "California"
        elif "n.y." in jurisdiction.lower():
            return "New York"
        elif "ga." in jurisdiction.lower():
            return "Georgia"
        elif "del." in jurisdiction.lower():
            return "Delaware"
        elif "Tenn." in jurisdiction.lower():
            return "Tennessee"
        else:
            # Check against state names and abbreviations
            for state in us.states.STATES:
                if state.name in jurisdiction or state.abbr in jurisdiction:
                    return state.name
            return 'Other'

    df['NAME'] = df['Jurisdiction'].apply(classify_place)

    frequency = df['NAME'].value_counts()

    # Convert the frequency Series to a DataFrame
    frequency_df = frequency.reset_index()
    frequency_df.columns = ['NAME', 'Frequency']

    with open("us-states.json") as geo:
        states_geojson = json.load(geo)

    # Create the choropleth map
    fig = px.choropleth(frequency_df, 
                        geojson=states_geojson, 
                        locations='NAME', 
                        featureidkey="properties.NAME",
                        color='Frequency',
                        color_continuous_scale="ylorrd",
                        scope="usa",
                        hover_name="NAME")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


    st.plotly_chart(fig)
