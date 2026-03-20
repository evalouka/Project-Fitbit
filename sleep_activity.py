"""

This script provides functions for analyzing the relationship between sleep and activity.

The file contains the following functions:

    individual_sleep_activity_corr
        Plots a scatter plot of the sleep minutes vs active minutes for a user.
        Includes a trendline to show the relationship between sleep and activity.

    print_sleep_activity_corr
        Returns the correlation coefficient, a label and advice based on the 
        correlation between sleep and activity for a user.
        Labels range from strong positive to strong negative relationship.

"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
from sleep import get_global_sleep_minutes, get_users_sleep_minutes
from activity_logs import get_global_activity, get_user_activity
import plotly.express as px
import streamlit as st

def individual_sleep_activity_corr(user_id, activity_induvidual_df, sleep_df):

    df_sleep = get_users_sleep_minutes(user_id, sleep_df)
    df_active = get_user_activity(user_id, activity_induvidual_df)

    user_id_str = str(user_id)
    
    df_sleep['get_date'] = pd.to_datetime(df_sleep['clean_date'])
    df_active['get_date'] = pd.to_datetime(df_active['ActivityDate'])

    df_combined = pd.merge(df_sleep, df_active, on="get_date")

    if df_combined.empty:
        print(f"No matching dates found for user {user_id_str}.")
        return None

    fig = px.scatter(df_combined, x='duration_minutes', y='active_minutes', 
        title=f"Activity vs Sleep for {user_id_str}",
        trendline="ols")

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Sleep minutes",
                      yaxis_title="Active minutes",
                      font_color="Black",
                      height = 475)
    
    fig.update_traces(
        marker=dict(color=px.colors.sequential.Blues[8], size=10, symbol='circle'),
        selector=dict(mode='markers'))
    
    fig.update_traces(
        line=dict(color=px.colors.sequential.Blues[6], width=3),
        selector=dict(mode='lines'))

    st.plotly_chart(fig)

    return 

def print_sleep_activity_corr(user_id, activity_induvidual_df, sleep_df):
    df_sleep = get_users_sleep_minutes(user_id, sleep_df)
    df_active = get_user_activity(user_id, activity_induvidual_df)
    
    df_sleep['get_date'] = pd.to_datetime(df_sleep['clean_date'])
    df_active['get_date'] = pd.to_datetime(df_active['ActivityDate'])
    
    df_combined = pd.merge(df_sleep, df_active, on="get_date")
    
    if df_sleep.empty or df_active.empty:
        return "N/A", "No data available", "No sleep or activity data found for this user."

    if df_combined.empty:
        return "N/A", "No data available", "No overlapping dates found for sleep and activity data."
    
    correlation = df_combined['active_minutes'].corr(df_combined['duration_minutes'])

    if correlation > 0.7:
        label = "Strong positive relationship"
        advice = "Sleep and activity are strongly linked for you, keep prioritizing your sleep to maintain your activity levels!"
    elif correlation > 0.3:
        label = "Moderate positive relationship"
        advice = "More sleep tends to mean more activity for you, try to improve your sleep routine to boost activity."
    elif correlation > -0.3:
        label = "Weak or no relationship"
        advice = "Sleep does not seem to strongly affect your activity levels, focus on other factors to improve activity."
    elif correlation > -0.7:
        label = "Moderate negative relationship"
        advice = "More sleep seems to reduce your activity, try to find a balance between rest and staying active."
    else:
        label = "Strong negative relationship"
        advice = "Your activity is significantly lower on days with more sleep, consider adjusting your sleep schedule to stay active."
    
    return correlation, label, advice


