"""

This script provides functions for activity analysis and visualization.

The file contains the following functions:

    get_gobal_activity
        Returns a cleaned dataframe of the the total # of activity minutes each user had. 
        Keeps track of total, very, fairly and light active minutes.

    get_user_activity
        Returns a cleaned dataframe of the # of active minutes a user has per day
        Keeps track of total, very, fairly and light active minutes.

    get_daily_activity_all_users
        Returns a cleaned dataframe of the # of active minute each user has had for each day
        Keeps track of total, very, fairly and light active minutes.

    bar_average_activity_week
        plots the average activity of a user per day of the week against the global average activity

    plot_global_activity_4_weeks
        Plots the total active minutes of all the users over the last 4 weeks
        Keeps track and can be viewed by total, very, fairly and light active minutes.

    plot_user_activity_4_weeks
        Plots the activity over the last 4 weeks of the user
        Keeps track and can be viewed by total, very, fairly and light active minutes.

    get_5_best_days
        returns the top 5 days where the user has had the most activity

"""


import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import plotly.express as px
import scipy.stats as stats
from datetime import datetime
import matplotlib.dates as mdates
import streamlit as st

def get_global_activity(activity_all_users_df):
    df = activity_all_users_df
    return df.groupby('Id').agg(
        activity_day_count=('ActivityDate', 'nunique'),
        total_active_minutes=('daily_active_minutes', 'sum')
    ).reset_index()

def get_user_activity(user_id, activity_induvidual_df):
    df = activity_induvidual_df
    return df[df['Id'] == str(user_id)].copy()

def get_daily_activity_all_users(activity_all_users_df):
    return activity_all_users_df

def bar_average_activity_week(Id, activity_all_users_df):

    df_all = get_daily_activity_all_users(activity_all_users_df)
    df_all['ActivityDate'] = pd.to_datetime(df_all['ActivityDate'])
    df_all['DayOfWeek'] = df_all['ActivityDate'].dt.day_name()

    df_ind = df_all[df_all['Id'] == str(Id)].copy()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    global_avg = df_all.groupby('DayOfWeek')['daily_active_minutes'].mean().reindex(day_order).reset_index()

    user_avg = df_ind.groupby('DayOfWeek')['daily_active_minutes'].mean().reindex(day_order).reset_index()

    fig = px.bar(user_avg, x='DayOfWeek', y='daily_active_minutes', 
                 title=f'Your Avg Activity vs Global Average for User: {Id}',
                 labels={'daily_active_minutes': 'Avg Active Minutes'}
                 )
    
    fig.update_traces(marker_color="#2c7da0", name="Average User Activity", showlegend=True, marker_line_color="white", marker_line_width=1)

    line = px.line(global_avg, x='DayOfWeek', y='daily_active_minutes')
    line_trace = line.data[0]
    line_trace.update(name='Global Average Activity',
                  line=dict(color="#3C27C6", width=4), showlegend=True)

    fig.add_trace(line_trace)

    fig.update_layout(height = 400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Day of the Week",
                      yaxis_title="Number of Active Minutes",
                      font_color="black")

    st.plotly_chart(fig)

def plot_global_activity_4_weeks(activity_all_users_df, view_by):
        
    df = get_daily_activity_all_users(activity_all_users_df)
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
    
    last_day = df['ActivityDate'].max()
    first_day = last_day - pd.Timedelta(days=28)
    df_recent = df[df['ActivityDate'] >= first_day]

    daily_summary = None
    activity = ""
    title = ""
    xlabel = "Date"

    view_by = view_by.strip()

    if view_by == "Total activity":
        activity = 'daily_active_minutes'
        daily_summary = df_recent.groupby('ActivityDate')['daily_active_minutes'].sum().reset_index()
        title = f"Total activity minutes over the last 4 weeks"

    elif view_by == "Very active activity":
        activity = 'VeryActiveMinutes'
        daily_summary = df_recent.groupby('ActivityDate')['VeryActiveMinutes'].sum().reset_index()
        title = f"Very active activity Minutes over the last 4 weeks"
        
    elif view_by == "Fairly active activity":
        activity = 'FairlyActiveMinutes'
        daily_summary = df_recent.groupby('ActivityDate')['FairlyActiveMinutes'].sum().reset_index()
        title = f"Fairly active activity Minutes over the last 4 weeks"

    elif view_by == "Light Activity":
        activity = 'LightlyActiveMinutes'
        daily_summary = df_recent.groupby('ActivityDate')['LightlyActiveMinutes'].sum().reset_index()
        title = f"Light active activity Minutes over the last 4 weeks"

    fig = px.line(daily_summary, x='ActivityDate', y=activity, title=title, markers=True)
    
    fig.update_traces(line=dict(color="#3557d4", width=2), fill='tozeroy', fillcolor="rgba(53, 87, 212, 0.6)")

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title= xlabel,
                      yaxis_title= "Activity minutes",
                      font_color="Black")
    
    st.plotly_chart(fig)

def plot_user_activity_4_weeks(user_id, activity_all_users_df, view_by):
    df = get_daily_activity_all_users(activity_all_users_df)

    df['Id'] = df['Id'].astype(str).str.strip()
    get_id = str(user_id).strip()

    user_df = df[df['Id'] == get_id].copy()
    if user_df.empty:
        print(f"Error: User {get_id} can not be found in the availible dataset.")
        return
    
    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    last_day = df['ActivityDate'].max()
    first_day = last_day - pd.Timedelta(days=28)

    complete_df = user_df[user_df['ActivityDate'] >= first_day].sort_values('ActivityDate')
    
    daily_summary = None
    activity = ""
    title = ""
    xlabel = "Date"

    view_by = view_by.strip()

    if complete_df.empty:
        print(f"There was no activity from user {user_id} in the last 4 weeks.")
        return

    if view_by == "Total activity":
        activity = 'daily_active_minutes'
        daily_summary = complete_df.groupby('ActivityDate')['daily_active_minutes'].sum().reset_index()
        title = f"Total activity minutes over the last 4 weeks of user {user_id}"

    elif view_by == "Very active activity":
        activity = 'VeryActiveMinutes'
        daily_summary = complete_df.groupby('ActivityDate')['VeryActiveMinutes'].sum().reset_index()
        title = f"Very Active Minutes over the last 4 weeks of user {user_id}"
        
    elif view_by == "Fairly active activity":
        activity = 'FairlyActiveMinutes'
        daily_summary = complete_df.groupby('ActivityDate')['FairlyActiveMinutes'].sum().reset_index()
        title = f"Fairly Active Minutes over the last 4 weeks of user {user_id}"

    elif view_by == "Light Activity":
        activity = 'LightlyActiveMinutes'
        daily_summary = complete_df.groupby('ActivityDate')['LightlyActiveMinutes'].sum().reset_index()
        title = f"Light Active Minutes over the last 4 weeks of user {user_id}"
    
    # DEBUG: cant find data
    else:
        print(f"CRITICAL: view_by '{view_by}' matched nothing!")
        return

    if daily_summary is None or daily_summary.empty:
        print("CRITICAL: daily_summary is empty. Check your date range or database.")
        return


    fig = px.line(daily_summary, x='ActivityDate', y=activity, title=title, markers=True)

    fig.update_traces(line=dict(color="#3557d4", width=2), fill='tozeroy', fillcolor="rgba(53, 87, 212, 0.6)")

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title= xlabel,
                      yaxis_title= "Activity minutes",
                      font_color="Black")
    
    st.plotly_chart(fig)

def get_5_best_days(user_id, activity_induvidual_df):

    st.subheader("Top 5 best days")

    df_active = get_user_activity(user_id, activity_induvidual_df)
    df_best_days = df_active.sort_values(by='active_minutes', ascending=False)
    df_top_5 = df_best_days[['ActivityDate', 'active_minutes']].head(5).reset_index(drop=True)
    df_top_5.index = range(1, 6)
    df_top_5.columns = ['Date of activity', 'Active minutes']

    final_df = df_top_5.style.background_gradient(cmap='Blues') \
                           .format({'Active minutes': '{:.0f} min'})

    st.table(final_df)
