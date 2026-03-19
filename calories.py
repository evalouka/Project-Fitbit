"""

This script provides functions for activity analysis and visualization.

The file contains the following functions:
    plot_user_vs_global_calories
        Plots the 

"""

import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import streamlit as st

def plot_user_vs_global_calories(Id, calories_df, view_by):

    user_df = calories_df[calories_df['Id'] == str(Id)].copy()
    global_df = calories_df.groupby('ActivityDate')['Calories'].mean().reset_index()
    global_df.rename(columns={'Calories': 'average_calories'}, inplace=True)

    if user_df.empty:
        print(f"No data found for ID: {Id}")
        return

    user_df = user_df.sort_values('ActivityDate')
    global_df = global_df.sort_values('ActivityDate')

    filtered_user = None
    filtered_global = None
    title = ""

    view_by = view_by.strip()

    if view_by == "Last week":
        end_date = user_df['ActivityDate'].max()
        start_date = end_date - pd.Timedelta(days=7)
        filtered_user = user_df[user_df['ActivityDate'] >= start_date]
        filtered_global = global_df[(global_df['ActivityDate'] >= start_date) & (global_df['ActivityDate'] <= end_date)]
        title = f"Calories burned by user {Id} - last week"

    elif view_by == "All data":
        filtered_user = user_df
        start_date = user_df['ActivityDate'].min()
        end_date = user_df['ActivityDate'].max()
        filtered_global = global_df[(global_df['ActivityDate'] >= start_date) & (global_df['ActivityDate'] <= end_date)]
        title = f"Calories burned by user {Id} - all available data"

    fig = px.bar(filtered_user, x='ActivityDate', y='Calories', title=title)
    fig.update_traces(marker_color="#2c7da0", name="User Calories", showlegend=True)

    line = px.line(filtered_global, x='ActivityDate', y='average_calories')
    line_trace = line.data[0]
    line_trace.update(name='Global Average',
                  line=dict(color="#3C27C6", width=4), showlegend=True)

    fig.add_trace(line_trace)

    fig.update_layout(height=400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Activity Dates",
                      yaxis_title="Calories burned",
                      font_color="white")

    st.plotly_chart(fig, key="user_vs_global_calories")
