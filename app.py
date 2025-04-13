
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


df = pd.read_csv("data/litigation_ext.csv")
year_freq_df = pd.read_csv("data/year_fr.csv")
algo_fr = pd.read_csv("data/algo_fr.csv")

st.title("AI Litigation Tracker")

st.write("With this tool, you will be able to track all past and ongoing AI litigation, including litigation against machine learning algorithms. The data was obtained from George Washington University's 'Law AI Litigation Database' (https://blogs.gwu.edu/law-eti/ai-litigation-database-search/).")
st.write(":point_left: If on mobile, click on the arrow in the upper-left corner for more pages.")

with st.sidebar:
    st.title("Track AI Litigation")
    pages = ["Track AI Litigation","Most recent activity" , "Explore Issues", "Explore Locations"]
    selected_page = st.sidebar.radio("Select Page: ", pages)
    #st.sidebar.text("AI Litigation Database – Search. \n URL: https://blogs.gwu.edu/law-eti/ai-litigation-database-search/. \n Last accessed on 1/30/2024")
    citation_html = """
    <div style="position: fixed; top: 60px; left: 20px;">
    AI Litigation Database  </div>
    
"""

    feedback_html = """
<div style="position: fixed; bottom: 20px; left: 20px;">
    <a href="https://docs.google.com/forms/d/e/1FAIpQLScKkIfXNukPPMuPyp3cX_uKQ9az9uFPz_mHQEs9YR7Zl0nCmg/viewform" style="text-decoration: none;">
        <button style="background-color: #6200ff; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
            Got any feedback?
        </button>
    </a>
</div>
"""
    #st.write("AI Litigation Database. Washington DC: The George Washington University Law. 2024. https://blogs.gwu.edu/law-eti/ai-litigation-database/")

    st.sidebar.markdown(citation_html, unsafe_allow_html=True)
    st.sidebar.markdown(feedback_html, unsafe_allow_html=True)

# Create content for each page
if selected_page == "Track AI Litigation":
    n_lawsuits = df.shape[0]
    st.markdown(f"There are currently **{n_lawsuits}** past and ongoing lawsuits in the database.")

    st.subheader('Clearview AI and ChatGPT Top the List of Most-Sued Algorithms', divider='gray')

    chart = alt.Chart(algo_fr).mark_bar(color='#6200ff').encode(
            x=alt.X('Algorithm', sort='-y'),
            y='Frequency'
        )

        # Display the chart in the Streamlit app
    st.altair_chart(chart, use_container_width=True)

        # Create a Pie Chart
    piechart = alt.Chart(algo_fr).mark_arc().encode(
        theta=alt.Theta(field='Frequency', type='quantitative', stack = "normalize"),
        color=alt.Color(field='Algorithm', type='nominal', sort = "ascending"),
        order=alt.Order(field='Frequency', type= 'quantitative', sort = "ascending"), 
        tooltip=['Algorithm', 'Frequency']
    )

    st.subheader('AI Disputes Reached Record Levels in 2023', divider='gray')

    st.bar_chart(data = year_freq_df, x= "Year", y="Frequency", color="#6200ff")


    # Display the Layered Chart in the Streamlit app
    #st.altair_chart(piechart, use_container_width=True)



    # Display the pie chart using Altair
    #st.altair_chart(piechart2, use_container_width=True)


elif selected_page == "Explore Issues":
    st.header("What issues are at stake?")
    df["Algorithm"] = df["Algorithm"].fillna("N/A")
    df["Issues"] = df["Issues"].fillna("")
    expressions = df["Issues"].str.lower().str.split(', ')
    all_expressions = ' '.join([expression for expressions_list in expressions for expression in expressions_list])
    all_expressions = all_expressions.replace(" lack", "")
    all_expressions = all_expressions.replace(" use", "")
    wordcloud = WordCloud(font_path="data/AbhayaLibre-Regular.ttf", width=800, height=400, background_color="white", colormap="magma").generate(all_expressions)

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
    case_count = len(filtered_df)

    if case_count == 1:
        summary_text = f"There is {case_count} {selected_issue} case in the database. Learn more about it here:"        
    else:
        summary_text = f"There are {case_count} {selected_issue} cases in the database. Learn more about them here:"       
    st.markdown(summary_text)
    # Display the filtered DataFrame
    #st.subheader("Explore selected cases in table form:")
    #st.write(filtered_df[["Caption", "Brief Description", "Algorithm", "Jurisdiction", "Application Areas", "Cause of Action", "Date Action Filed", "Link"]])

    # Display each row as Markdown
    for index, row in filtered_df.iterrows():
        st.write(f"## {row['Caption']}")
        st.write(f"**Brief Description:** {row['Brief Description']}")
        st.write(f"**Algorithm:** {row['Algorithm']}")
        st.write(f"**Jurisdiction:** {row['Jurisdiction']}")
        st.write(f"**Application Areas:** {row['Application Areas']}")
        st.write(f"**Cause of Action:** {row['Cause of Action']}")
        st.write(f"**Date Action Filed:** {row['Date Action Filed']}")
        st.link_button("Find out more", row['Link'])
        st.markdown("---")  # Add a horizontal line between rows

elif selected_page == "Most recent activity":
    st.header('Explore cases with the most recent activity', divider='gray')
    df["Algorithm"] = df["Algorithm"].fillna("N/A")
    df['New Activity'] = pd.to_datetime(df['New Activity'], errors='coerce')
    df_sorted = df.sort_values(by='New Activity', ascending=False)
    top_10_cases = df_sorted.head(10)
    counter=0
    for index, row in top_10_cases.iterrows():
        st.write(f"#### {row['Caption']}")
        st.write(f" **Date Of New Activity:** {row['New Activity'].strftime('%B %dth %Y')}")
        on = st.toggle('Read more', key= counter)
        if on:
            st.write(f"**Brief Description:** {row['Brief Description']}")
            st.write(f"**Algorithm:** {row['Algorithm']}")
            st.write(f"**Jurisdiction:** {row['Jurisdiction']}")
            st.write(f"**Application Areas:** {row['Application Areas']}")
            st.write(f"**Cause of Action:** {row['Cause of Action']}")
            st.write(f"**Date Action Filed:** {row['Date Action Filed']}")
            st.link_button("Find out more", row['Link'])

        st.markdown("---") 
        counter +=1



elif selected_page == "Explore Locations":
    st.subheader('California is the US state with the most litigation filings', divider='gray')
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

    with open("data/us-states.json") as geo:
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
