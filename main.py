
import streamlit as st
import os
from heart_rate import mean_heart_rate_per_day, HR_zones_per_group, heart_rate_vs_activity, mean_HR_per_group_compared_to_id
from user_classification import classify_users
import pandas as pd
import sqlite3
from heart_rate import HR_zones
from calories_regression import regression_calories
from step import (
    plot_steps_by_block_general,
    plot_steps_by_block_per_id,
    plot_sleep_sedentary_correlation,
    plot_sleep_by_block_per_id,
    plot_calories_by_block_per_id
)

st.set_page_config(
page_title = "Fitbit Dashboard",
layout = "wide",
initial_sidebar_state = "expanded"
)

#Connect to data base
connection = sqlite3.connect("fitbit_database.db")

@st.cache_data
def load_hr_data():
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate)
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Id"] = heart_rate_df["Id"].astype(str)
    return heart_rate_df

@st.cache_data
def load_unique_id():
    return classify_users()["Id"].astype(str)

@st.cache_data
def load_daily_activity_data():
    query_daily_activity = f"SELECT Id, ActivityDate, TotalSteps, Calories FROM daily_activity"
    cursor = connection.cursor()
    cursor.execute(query_daily_activity)
    rows = cursor.fetchall()
    daily_activity_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    daily_activity_df["Id"] = daily_activity_df["Id"].astype(str)
    return daily_activity_df

@st.cache_data
def load_hourly_activity():
    query_activity = f"SELECT Id, ActivityHour, StepTotal FROM hourly_steps"
    cursor_activity = connection.cursor()
    cursor_activity.execute(query_activity)
    rows_activity = cursor_activity.fetchall()
    hourly_activity_df = pd.DataFrame(rows_activity, columns=[x[0] for x in cursor_activity.description]).copy()
    hourly_activity_df["Id"] = hourly_activity_df["Id"].astype(str)
    return hourly_activity_df

@st.cache_data
def load_hourly_intensity():
    query_intensity = f"SELECT Id, ActivityHour, AverageIntensity FROM hourly_intensity"
    cursor_intensity = connection.cursor()
    cursor_intensity.execute(query_intensity)
    rows_intensity = cursor_intensity.fetchall()
    intensity_df = pd.DataFrame(rows_intensity, columns=[x[0] for x in cursor_intensity.description]).copy()
    intensity_df["Id"] = intensity_df["Id"].astype(str)
    return intensity_df


heart_rate_df = load_hr_data()
daily_activity_df = load_daily_activity_data()
hourly_activity_df = load_hourly_activity()
intensity_df = load_hourly_intensity()

general_tab, id_tab = st.tabs(["General", "Id"])


with general_tab:
    col1, col2 = st.columns(2)
    with col1:
        HR_zones_per_group(heart_rate_df)
    with col2:
        plot_steps_by_block_general()

with id_tab:
    col1, col2 = st.columns([1,6])
    with col1:
        Id = st.selectbox("Select user", options=sorted(load_unique_id()))
        section = st.radio("Section", ["General", "Activity", "Sleep", "Heart rate", "Calories"])

    with col2:
        if section == "General":
            st.write("General data here")
        if section == "Activity":
            plot_steps_by_block_per_id(Id)
        if section == "Sleep":
            plot_sleep_sedentary_correlation(Id)
            plot_sleep_by_block_per_id(Id)
        if section == "Heart rate":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Sample size", f"{len(heart_rate_df[heart_rate_df['Id']== Id])} records")
            m2.metric("Median HR", f"{heart_rate_df[heart_rate_df['Id']== Id]['Value'].median()} bpm")
            m3.metric("Max HR", f"{heart_rate_df[heart_rate_df['Id']== Id]['Value'].max()} bpm")
            m4.metric("HR variability",f"{heart_rate_df[heart_rate_df['Id']== Id]['Value'].std():.0f} bpm" )

            col1, col2 = st.columns(2)
            with col1:
                mean_heart_rate_per_day(heart_rate_df, Id)
                HR_zones(heart_rate_df, Id)
            with col2:
                #st.radio("", ["", ""], horizontal=True, key="placeholder", index=1, label_visibility = "hidden")
                for i in range(5):
                    st.write("")
                heart_rate_vs_activity(heart_rate_df, hourly_activity_df, intensity_df, Id)
                mean_HR_per_group_compared_to_id(heart_rate_df, Id)

        if section == "Calories":
            col1, col2 = st.columns(2)
            with col1:
                regression_calories(daily_activity_df, Id)
            with col2:
                plot_calories_by_block_per_id(Id)

