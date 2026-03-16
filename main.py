import streamlit as st
import os
from heart_rate import plot_mean_heart_rate, HR_zones_per_group, plot_heart_rate_vs_activity_with_intensity, mean_HR_per_group_compared_to_id
from user_classification import classify_users
import pandas as pd
import sqlite3
from heart_rate import plot_hr_zones
from weather import plot_weather_vs_activity, plot_weather_vs_activity_per_id
from calories_regression import plot_regression_calories
from minutes_distribution import distribution_activity_minutes_for_id
# from activity_logs import plot_global_activity_4_weeks, plot_user_activity_4_weeks, get_5_best_days, plot_user_activity_4_weeks, get_5_best_users
from sleep_activity import individual_sleep_activity_corr
from calories import plot_user_vs_global_calories
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

#Connect to database
connection = sqlite3.connect("fitbit_database.db")

@st.cache_data
def load_hr_data():
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate)
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Id"] = heart_rate_df["Id"].astype(str)
    heart_rate_df["Value"] = pd.to_numeric(heart_rate_df["Value"])
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"], format= "%m/%d/%Y %I:%M:%S %p")
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
    daily_activity_df["ActivityDate"] = pd.to_datetime(daily_activity_df["ActivityDate"])
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
    hourly_activity_df["ActivityHour"] = pd.to_datetime(hourly_activity_df["ActivityHour"])
    return hourly_activity_df

@st.cache_data
def load_hourly_intensity():
    query_intensity = f"SELECT Id, ActivityHour, AverageIntensity FROM hourly_intensity"
    cursor_intensity = connection.cursor()
    cursor_intensity.execute(query_intensity)
    rows_intensity = cursor_intensity.fetchall()
    intensity_df = pd.DataFrame(rows_intensity, columns=[x[0] for x in cursor_intensity.description]).copy()
    intensity_df["Id"] = intensity_df["Id"].astype(str)
    intensity_df["ActivityHour"] = pd.to_datetime(intensity_df["ActivityHour"])
    return intensity_df

@st.cache_data
def load_weather_data():
    full_weather_data = pd.read_csv("weather_data/chicago_weather_march_april.csv")
    weather = full_weather_data[["datetime", "temp", "precip"]].copy()
    weather["datetime"] = pd.to_datetime(weather["datetime"])
    return weather

@st.cache_data
def load_activity_minutes_data():
    query_daily_activity = (f"SELECT Id, ActivityDate, VeryActiveMinutes, FairlyActiveMinutes, "
                            f"LightlyActiveMinutes, SedentaryMinutes FROM daily_activity")
    cursor = connection.cursor()
    cursor.execute(query_daily_activity)
    rows = cursor.fetchall()
    activity_minutes_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    activity_minutes_df["Id"] = activity_minutes_df["Id"].astype(str)
    return activity_minutes_df


heart_rate_df = load_hr_data()
daily_activity_df = load_daily_activity_data()
hourly_activity_df = load_hourly_activity()
intensity_df = load_hourly_intensity()
weather_df = load_weather_data()
activity_minutes_df = load_activity_minutes_data()

general_tab, id_tab = st.tabs(["General", "Id"])


with general_tab:
    m1, m2, m3, m4 = st.columns(4)
    st.markdown("""
        <style>
        [data-testid="stMetricLabel"] p {
            font-weight: bold ; 
        }
        [data-testid="stMetricValue"] {
            font-size: 20px;
        }
        </style>
    """, unsafe_allow_html=True)


    m1.metric("Number of users", f"{len(load_unique_id())}")
    m2.metric("Average activity", f"{daily_activity_df['TotalSteps'].mean():.0f} steps")
    m3.metric("Date range", f"{daily_activity_df.sort_values(by= 'ActivityDate')['ActivityDate'].iloc[0]}"
                            f" - {daily_activity_df.sort_values(by= 'ActivityDate')['ActivityDate'].iloc[-1]} ")
    m4.metric("Average sleep", f"Aimee")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.write("plot_global_activity_4_weeks(connection)") #Aimee
    with row1_col2:
        st.write("Ten thousand steps (Eva)")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        plot_steps_by_block_general()
    with row2_col2:
        st.write("Print 5 best users, or whatever you like (Eva)")

    row3_col1, row3_col2 = st.columns(2)
    with row3_col2:
        choose = st.radio("Choose", ["Precipitation", "Temperature"], horizontal = True, key = "weather_general")

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        HR_zones_per_group(heart_rate_df)
    with row4_col2:
        plot_weather_vs_activity(weather_df, daily_activity_df, choose)

with id_tab:
    col1, col2 = st.columns([1,6])
    with col1:
        Id = st.selectbox("Select user", options=sorted(load_unique_id()))
        section = st.radio("Section", ["General", "Activity", "Sleep", "Heart rate", "Calories", "Intensity"])

    with col2:
        if section == "General":
            m1, m2, m3, m4 = st.columns(4)
            id_class = classify_users()[classify_users()['Id'].astype(str) == Id]['Class'].values[0]
            id_daily_activity = daily_activity_df[daily_activity_df['Id']== Id]
            m1.metric("You are a", id_class+ " user")
            m2.metric("Average activity", f"{id_daily_activity['TotalSteps'].mean():.0f} steps")
            m3.metric("Date range", f"{id_daily_activity.sort_values(by= 'ActivityDate')['ActivityDate'].iloc[0].strftime('%Y/%m/%d')}"
                            f" - {id_daily_activity.sort_values(by= 'ActivityDate')['ActivityDate'].iloc[-1].strftime('%Y/%m/%d')} ")
            m4.metric("Average sleep", f"Aimee")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write("plot_user_activity_4_weeks(Id, connection)") #Aimee
            with row1_col2:
                st.write("individual_sleep_activity_corr(Id, connection)") #Aimee

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                view_by = st.radio("View by", ["Hour", "Day"], horizontal=True, key="hr_mean_general_tab", index=1)
                st.write("Median heart rate by hour/day (Naomi)")
             
            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                plot_mean_heart_rate(heart_rate_df, Id, view_by)
            with row3_col2:
                st.write("Top 5 best activity dates (Aimee)")
                

        if section == "Activity":
            m1, m2, m3, m4 = st.columns(4)
            id_activity = daily_activity_df[daily_activity_df['Id']== Id]

            id_activity_hourly = hourly_activity_df[hourly_activity_df['Id'] == Id]
            id_activity_hourly["Hour"] = id_activity_hourly["ActivityHour"].dt.hour
            most_active_hour = id_activity_hourly.groupby("Hour")["StepTotal"].mean().idxmax()

            m1.metric("Average activity", f"{id_activity['TotalSteps'].mean():.0f} steps")
            m2.metric("Variability", f"{id_activity['TotalSteps'].std():.0f} steps")
            m3.metric("Percentage of days reaching 10,000 steps",
                      f"{(id_activity['TotalSteps'] >= 10000).mean() * 100:.2f}")
            m4.metric("Most active hour", f"{most_active_hour}")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write("plot_user_activity_4_weeks(Id, connection)") #Aimee
            with row1_col2:
                plot_steps_by_block_per_id(Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Plot total activity per day of the week compared to general (Aimee)")
            with row2_col2:
                distribution_activity_minutes_for_id(activity_minutes_df, Id)


        if section == "Sleep":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something (Aimee)")
            m2.metric("Metric2", f"Something (Aimee)")
            m3.metric("Metric3", f"Something (Aimee)")
            m4.metric("3", f"Something (Aimee)")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write("individual_sleep_activity_corr(Id, connection)") #Aimee
            with row1_col2:
                plot_sleep_sedentary_correlation(Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                plot_sleep_by_block_per_id(Id)
            with row2_col2:
                st.write("Average sleep per day/week (Aimee)") #Aimee
            
            row3_col1, row3_col2 = st.columns(2)
            with row3_col2:
                view_by = st.radio("View by", ["Day", "Week"], horizontal=True, key="sleep_min", index=1)


        if section == "Heart rate":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Sample size", f"{len(heart_rate_df[heart_rate_df['Id']== Id])} records")
            m2.metric("Median HR", f"{heart_rate_df[heart_rate_df['Id']== Id]['Value'].median()} bpm")
            m3.metric("Max HR", f"{heart_rate_df[heart_rate_df['Id']== Id]['Value'].max()} bpm")
            m4.metric("HR variability",f"{heart_rate_df[heart_rate_df['Id']== Id]['Value'].std():.0f} bpm" )

            view_by = st.radio("View by", ["Hour", "Day"], horizontal=True, key="hr_mean", index=1)

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                plot_mean_heart_rate(heart_rate_df, Id, view_by)
            with row1_col2:
                plot_heart_rate_vs_activity_with_intensity(heart_rate_df, hourly_activity_df, intensity_df, Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                view_by = st.radio("View by", ["Hour", "Day"], horizontal=True, key="hr_zones", index=1)
            with row2_col2:
                selected = st.multiselect("Compare to", ["Light", "Moderate", "Heavy"], default="Heavy")

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                plot_hr_zones(heart_rate_df, Id, view_by)
            with row3_col2:
                mean_HR_per_group_compared_to_id(heart_rate_df, Id, selected)

            row4_col1, row4_col2 = st.columns(2)
            with row4_col1:
                st.write("Average hear rate of the day vs sleep of that day (Aimee)")

        if section == "Calories":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something (Rojin)")
            m2.metric("Metric2", f"Something (Rojin)")
            m3.metric("Metric3", f"Something (Rojin)")
            m4.metric("3", f"Something (Rojin)")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                plot_regression_calories(daily_activity_df, Id)
            with row2_col1:
                plot_calories_by_block_per_id(Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Eva do you have something about calories?")

            with row2_col2:
                st.write("plot_user_vs_global_calories(Id, connection)")#Aimee

        if section == "Intensity":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something (Rojin)")
            m2.metric("Metric2", f"Something (Rojin)")
            m3.metric("Metric3", f"Something (Rojin) ")
            m4.metric("3", f"Something (Rojin)")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write("Average intensity by hour (Rojin)")
            with row1_col2:
                st.write("Steps vs total intensity per user (Rojin)")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Heart rate vs intensity (Eva)")
            with row2_col2:
                st.write("Average intensity by day of week (Rojin)")

        if section == "Weight":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something")
            m2.metric("Metric2", f"Something")
            m3.metric("Metric3", f"Something")
            m4.metric("3", f"Something")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write("BMI for user (Eva)")
            with row1_col2:
                st.write("BMI compared to others/general (Eva)")
            
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Weight for user (in KG and in Pounds)(Eva)")
        







