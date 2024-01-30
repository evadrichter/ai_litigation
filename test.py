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


df = pd.read_csv("litigation_ext.csv")

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

# Apply the function to create the new 'Place' column
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

fig.show()