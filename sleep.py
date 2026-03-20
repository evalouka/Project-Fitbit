"""
This script provides functions for sleep analysis and visualization.

The file contains the following functions:

    get_users_sleep_minutes
        Return a dataframe of the cleaned sleep data for a specific user

    get_global_sleep_minutes
        Returns a cleaned dataframe of the global sleep data

    total_avg_sleep_per_night
        Filters the empty entries and returns the average sleep per night of a user

    get_average_sleep
        returns a bar plot of the average amount of sleep a user got. Eigher per day of the week or per week

    plot_sleep_vs_heartrate
        Returns the correlation between the sleepminutes of the user and there average heartrate of that day
    

"""

import pandas as pd
import plotly.express as px
import streamlit as st

def get_users_sleep_minutes(user_id, df_sleep):
    df_user = df_sleep[df_sleep['Id'] == str(user_id)].copy()
    df_user_sleep = df_user.groupby(['Id', 'clean_date']).size().reset_index(name='duration_minutes')
    return df_user_sleep

def get_global_sleep_minutes(df_sleep):
    df_global = df_sleep.groupby('Id').agg(
        sleep_minutes=('value', 'count'),
        sleep_day_count=('clean_date', 'nunique')
    ).reset_index()
    return df_global

def total_avg_sleep_per_night(sleep_df):
    df = get_global_sleep_minutes(sleep_df)
    df['avg_per_night'] = df['sleep_minutes'] / df['sleep_day_count']
    return df[df['sleep_day_count'] > 0]['avg_per_night'].mean()

def get_average_sleep(Id, sleep_df, view_by):
    data_df = get_users_sleep_minutes(Id, sleep_df)
    data_df["clean_date"] = pd.to_datetime(data_df["clean_date"])

    plot_df = None
    x_col = ""
    title = ""
    xlabel = ""

    view_by = view_by.strip()

    if view_by == "Day":
        data_df["DayOfWeek"] = data_df["clean_date"].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        plot_df = data_df.groupby("DayOfWeek")["duration_minutes"].mean().reindex(day_order).reset_index()
        x_col = "DayOfWeek"
        xlabel = "Day of the week"
        title = f"Average sleep per day of the week for user {Id}"

    elif view_by == "Week":
        data_df["Week"] = data_df["clean_date"].dt.isocalendar().week.astype(int)
        plot_df = data_df.groupby("Week")["duration_minutes"].mean().reset_index()
        x_col = "Week"
        xlabel = "Week number"
        title = f"Average sleep per week for user {Id}"

    fig = px.bar(plot_df, x=x_col, y='duration_minutes', title=title)

    fig.update_traces(marker_color="#6d62c4",marker_line_color="white", marker_line_width=1.5)

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=xlabel,
                      yaxis_title="Sleep minutes",
                      font_color="Black")
    
    st.plotly_chart(fig)

def plot_sleep_vs_heartrate(user_id, sleep_df, heart_rate_df):

    """
        Plots mean heartrate against the sleep of the user
    """
    
    df_sleep = get_users_sleep_minutes(user_id, sleep_df)
    df_sleep['clean_date'] = pd.to_datetime(df_sleep['clean_date'])

    df_hr = heart_rate_df[heart_rate_df['Id'] == str(user_id)].copy()
    df_hr['clean_date'] = df_hr['Time'].dt.date
    df_hr['clean_date'] = pd.to_datetime(df_hr['clean_date'])
    df_hr_daily = df_hr.groupby('clean_date')['Value'].mean().reset_index()
    df_hr_daily.rename(columns={'Value': 'avg_heart_rate'}, inplace=True)

    df_combined = pd.merge(df_sleep, df_hr_daily, on='clean_date')

    if df_combined.empty:
        st.write("No matching dates found for sleep and heart rate data.")
        return
    
    correlation = df_combined['duration_minutes'].corr(df_combined['avg_heart_rate'])
    
    if correlation > 0.7:
        label = "Strong positive relationship"
        advice = "More sleep strongly increases your heart rate, this could indicate your body needs more recovery time."
    elif correlation > 0.3:
        label = "Moderate positive relationship"
        advice = "More sleep tends to slightly raise your heart rate, monitor if this affects your overall health."
    elif correlation > -0.3:
        label = "Weak or no relationship"
        advice = "Sleep does not seem to strongly affect your heart rate, your heart rate is likely driven by other factors."
    elif correlation > -0.7:
        label = "Moderate negative relationship"
        advice = "More sleep tends to lower your heart rate, which is generally a good sign of recovery."
    else:
        label = "Strong negative relationship"
        advice = "More sleep strongly lowers your heart rate, great sign that sleep is helping your body recover well!"

    fig = px.scatter(df_combined, x='duration_minutes', y='avg_heart_rate',
                     title=f"Sleep vs Heart Rate for user {user_id}",
                     trendline="ols")

    fig.update_traces(marker=dict(color="#6d62c4", size=10),
                      selector=dict(mode='markers'))
    fig.update_traces(line=dict(color="#54b8fa", width=3),
                      selector=dict(mode='lines'))

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Sleep minutes",
                      yaxis_title="Average heart rate (bpm)",
                      font_color="Black")

    st.plotly_chart(fig, key="sleep_vs_hr_chart")

    st.markdown(f"""
    <div style="background-color: rgba(109, 98, 196, 0.2); padding: 1rem; border-radius: 0.5rem;">
        <b style="color: #6d62c4;">{label}</b><br><br>{advice}
        <p style="text-align: right; margin: 0.5rem 0 0 0;"><small style="color: gray;">*Only dates with both heart rate and sleep data</small></p>
    </div>
    """, unsafe_allow_html=True)