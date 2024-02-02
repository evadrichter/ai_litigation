import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import numpy as np
from wordcloud import WordCloud
import altair as alt
import us

import plotly.express as px
import json


df = pd.read_csv("data/litigation_ext.csv")

data = pd.read_csv("data/status_fr.csv")
data['Status_Cat'] = data['Status_Cat'].apply(lambda x: x + " cases")

# issue = df['Issues'].str.split(', ')
# issue = issue.dropna()
# issue_list = [keyword.strip() for sublist in issue for keyword in sublist]

# print(issue_list)

# counts = pd.Series(issue_list).value_counts()
# issues = counts.reset_index()
# issues.columns = ["Issue", "Frequency"]

custom_color_scheme = ["#008B76", "#6200FF", "#DF0000", "#B0A8B9", "#FF7343", "#FFBE38", "#6C9EB4", "#FD9BFF"]



fig = px.treemap(data, 
                 path=['Status_Cat'], 
                 values='count',
                 color_discrete_sequence=custom_color_scheme)

# Customize the layout
fig.update_layout(
    #title='Status Category Treemap',
    margin=dict(t=50, b=0, r=0, l=0)
)

# Show the plot
fig.show()

