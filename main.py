import streamlit as st
import os
from heart_rate import mean_heart_rate_per_day, HR_zones_per_group, heart_rate_vs_activity, mean_HR_per_group_compared_to_id
from user_classification import classify_users
import pandas as pd
import sqlite3
from heart_rate import HR_zones
from weather import scatterplot_means
from calories_regression import regression_calories
from activity_logs import plot_global_activity_4_weeks, plot_user_activity_4_weeks, get_5_best_days, plot_user_activity_4_weeks, get_5_best_users
from sleep_activity import individual_sleep_activity_corr
from calories import plot_user_vs_global_calories

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

@st.cache_data
def load_weather_data():
    # Read data
    full_weather_data = pd.read_csv("weather_data/chicago_weather_march_april.csv")
    # Create weather dataframe with all needed data
    weather = full_weather_data[["datetime", "temp", "precip", ]].copy()
    # Convert the datetime column to date objects
    weather["datetime"] = pd.to_datetime(weather["datetime"])
    return weather


heart_rate_df = load_hr_data()
daily_activity_df = load_daily_activity_data()
hourly_activity_df = load_hourly_activity()
intensity_df = load_hourly_intensity()
weather_df = load_weather_data()

general_tab, id_tab = st.tabs(["General", "Id"])


with general_tab:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Metric1", f"Something")
    m2.metric("Metric2", f"Something")
    m3.metric("Metric3", f"Something")
    m4.metric("3", f"Something")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.write(plot_global_activity_4_weeks(connection)) #Aimee
    with row1_col2:
        st.write("Pie Chart with light, heavy, moderate (Aimee)")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.write("Plot steps over day by blocks of four (Rojin)")
    with row2_col2:
        st.write("Print 5 best users, or whatever you like (Eva)")

    row3_col1, row3_col2 = st.columns(2)
    with row3_col2:
        choose = st.radio("Choose", ["Precipitation", "Temperature"], horizontal = True)


    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        HR_zones_per_group(heart_rate_df)
    with row4_col2:
        scatterplot_means(weather_df, daily_activity_df, choose)
        st.write("Other plots here")

with id_tab:
    col1, col2 = st.columns([1,6])
    with col1:
        Id = st.selectbox("Select user", options=sorted(load_unique_id()))
        section = st.radio("Section", ["General", "Activity", "Sleep", "Heart rate", "Calories", "Intensity"])

    with col2:
        if section == "General":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("You are", f" light/heavy/moderate user")
            m2.metric("Metric2", f"Something")
            m3.metric("Metric3", f"Something")
            m4.metric("3", f"Something")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write(plot_user_activity_4_weeks(Id, connection)) #Aimee
            with row1_col2:
                st.write(individual_sleep_activity_corr(Id, connection)) #Aimee

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Median heart rate by hour/day (Naomi)")
            with row2_col2:
                st.write(get_5_best_days(Id, connection)) #Aimee

        if section == "Activity":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something")
            m2.metric("Metric2", f"Something")
            m3.metric("Metric3", f"Something")
            m4.metric("3", f"Something")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write(plot_user_activity_4_weeks(Id, connection)) #Aimee
            with row1_col2:
                st.write("Activity steps per blocks of hours (Rojin)")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Plot total activity per day of the week compared to general (Aimee)")
            with row2_col2:
                st.write("Something with veryactive, lightlyactive, etc. minutes (Naomi)")


        if section == "Sleep":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something")
            m2.metric("Metric2", f"Something")
            m3.metric("Metric3", f"Something")
            m4.metric("3", f"Something")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                individual_sleep_activity_corr(Id, connection) #Aimee
            with row1_col2:
                st.write("Sleep activity sedentary minutes correlation (Rojin)")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Sleep per block (Rojin)")
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
                mean_heart_rate_per_day(heart_rate_df, Id, view_by)
            with row1_col2:
                heart_rate_vs_activity(heart_rate_df, hourly_activity_df, intensity_df, Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                view_by = st.radio("View by", ["Hour", "Day"], horizontal=True, key="hr_zones", index=1)
            with row2_col2:
                selected = st.multiselect("Compare to", ["Light", "Moderate", "Heavy"], default="Heavy")

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                HR_zones(heart_rate_df, Id, view_by)
            with row3_col2:
                mean_HR_per_group_compared_to_id(heart_rate_df, Id, selected)

            row4_col1, row4_col2, st.colums(2)
            with row4_col1:
                st.write("Average hear rate of the day vs sleep of that day (Aimee)")

        if section == "Calories":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something")
            m2.metric("Metric2", f"Something")
            m3.metric("Metric3", f"Something")
            m4.metric("3", f"Something")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                regression_calories(daily_activity_df, Id)
            with row2_col1:
                st.write("Calories per block (Rojin)")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Eva do you have something about calories?")

            with row2_col2:
                plot_user_vs_global_calories(Id, connection) #Aimee

        if section == "Intensity":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Metric1", f"Something")
            m2.metric("Metric2", f"Something")
            m3.metric("Metric3", f"Something")
            m4.metric("3", f"Something")

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
        







