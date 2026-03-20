import streamlit as st
import os
from scipy.constants import minute
from heart_rate import plot_mean_heart_rate, HR_zones_per_group, plot_heart_rate_vs_activity_with_intensity, \
    mean_HR_per_group_compared_to_id
from user_classification import classify_users
import pandas as pd
import sqlite3
from heart_rate import plot_hr_zones
from weather import plot_weather_vs_activity, plot_weather_vs_activity_per_id
from calories_regression import plot_regression_calories
from minutes_distribution import distribution_activity_minutes_for_id
# from activity_logs import plot_global_activity_4_weeks, plot_user_activity_4_weeks, get_5_best_days, plot_user_activity_4_weeks, get_5_best_users
#from sleep_activity import individual_sleep_activity_corr
#from calories import plot_user_vs_global_calories
from step import (
    plot_steps_by_block_general,
    plot_steps_by_block_per_id,
    plot_sleep_sedentary_correlation,
    plot_sleep_by_block_per_id,
    plot_calories_by_block_per_id
)

from intensity import (
    plot_avg_intensity_per_hour,
    plot_avg_intensity_by_dow,
    plot_steps_vs_intensity,
    plot_intensity_by_hour_for_id,
    plot_intensity_by_dow_for_id
)

st.set_page_config(
    page_title="Fitbit Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Connect to database
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
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"], format="%m/%d/%Y %I:%M:%S %p")
    return heart_rate_df


@st.cache_data
def load_unique_id():
    return classify_users()["Id"].astype(str)


@st.cache_data
def load_daily_activity_data():
    query_daily_activity = f"SELECT Id, ActivityDate, TotalSteps, Calories, SedentaryMinutes FROM daily_activity"
    cursor = connection.cursor()
    cursor.execute(query_daily_activity)
    rows = cursor.fetchall()
    daily_activity_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    daily_activity_df["ActivityDate"] = pd.to_datetime(daily_activity_df["ActivityDate"])
    daily_activity_df["Id"] = daily_activity_df["Id"].astype(str)
    return daily_activity_df


@st.cache_data
def load_hourly_activity():
    bins = [0, 4, 8, 12, 16, 20, 24]
    labels = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]
    query_activity = f"SELECT Id, ActivityHour, StepTotal FROM hourly_steps"
    cursor_activity = connection.cursor()
    cursor_activity.execute(query_activity)
    rows_activity = cursor_activity.fetchall()
    hourly_activity_df = pd.DataFrame(rows_activity, columns=[x[0] for x in cursor_activity.description]).copy()
    hourly_activity_df["Id"] = hourly_activity_df["Id"].astype(str)
    hourly_activity_df["ActivityHour"] = pd.to_datetime(hourly_activity_df["ActivityHour"])
    hourly_activity_df["Date"] = hourly_activity_df["ActivityHour"].dt.date
    hourly_activity_df["Hour"] = hourly_activity_df["ActivityHour"].dt.hour
    hourly_activity_df["Block"] = pd.cut(hourly_activity_df["Hour"], bins=bins, labels=labels, right=False)
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

@st.cache_data
def get_calories_metrics(daily_activity_df, user_id):
    """Return per-user and global calorie stats from daily_activity."""
    id_df      = daily_activity_df[daily_activity_df["Id"] == user_id]["Calories"]
    global_df  = daily_activity_df["Calories"]
    avg_cal    = id_df.mean()
    max_cal    = id_df.max()
    global_avg = global_df.mean()
    vs_avg_pct = (avg_cal - global_avg) / global_avg * 100 if global_avg else 0
    return avg_cal, max_cal, global_avg, vs_avg_pct


@st.cache_data
def load_intensity_data():
    query = "Select Id, ActivityHour, TotalIntensity, AverageIntensity FROM hourly_intensity"
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    df["Id"] = df["Id"].astype(str)
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"])
    df["date"] = df["ActivityHour"].dt.date
    df["Hour"] = df["ActivityHour"].dt.hour
    df["Day of Week"] = df["ActivityHour"].dt.day_name()
    df["IsWeekend"] = df["ActivityHour"].dt.dayofweek >= 5
    return df


@st.cache_data
def load_minute_sleep():
    bins = [0, 4, 8, 12, 16, 20, 24]
    labels = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]
    df = pd.read_sql_query("SELECT Id, date, value FROM minute_sleep", connection)
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M:%S %p")
    df["Hour"] = df["date"].dt.hour
    df["Date"] = df["date"].dt.date
    df["Block"] = pd.cut(df["Hour"], bins=bins, labels=labels, right=False)
    df["Id"] = df["Id"].astype(str)
    return df


@st.cache_data
def load_hourly_calories():
    bins = [0, 4, 8, 12, 16, 20, 24]
    labels = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]
    df = pd.read_sql_query("SELECT Id, ActivityHour, Calories FROM hourly_calories", connection)
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df["Hour"] = df["ActivityHour"].dt.hour
    df["Date"] = df["ActivityHour"].dt.date
    df["Block"] = pd.cut(df["Hour"], bins=bins, labels=labels, right=False)
    df["Id"] = df["Id"].astype(str)
    return df

@st.cache_data
def load_daily_sleep_data():
    query = "SELECT Id, date, value FROM minute_sleep"
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    df["Id"] = df["Id"].astype(str)
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M:%S %p")
    df["SleepDay"] = df["date"].dt.date
    # count minutes where value == 1 (asleep) per user per day
    daily_sleep = (df[df["value"] == 1]
                   .groupby(["Id", "SleepDay"])
                   .size()
                   .reset_index(name="TotalMinutesAsleep"))
    daily_sleep["SleepDay"] = pd.to_datetime(daily_sleep["SleepDay"])
    return daily_sleep

heart_rate_df = load_hr_data()
daily_activity_df = load_daily_activity_data()
hourly_activity_df = load_hourly_activity()
hourly_intensity_df = load_hourly_intensity()
weather_df = load_weather_data()
activity_minutes_df = load_activity_minutes_data()
intensity_df = load_intensity_data()
minutes_sleep_df = load_minute_sleep()
hourly_calories_df = load_hourly_calories()
daily_sleep_df = load_daily_sleep_data()

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
    m3.metric("Date range",
              f"{daily_activity_df.sort_values(by='ActivityDate')['ActivityDate'].iloc[0].strftime('%m/%d/%Y')}"
              f" - {daily_activity_df.sort_values(by='ActivityDate')['ActivityDate'].iloc[-1].strftime('%m/%d/%Y')} ")
    m4.metric("Average sleep", f"Aimee")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.write("plot_global_activity_4_weeks(connection)")  # Aimee
    with row1_col2:
        st.write("Ten thousand steps (Eva)")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        plot_steps_by_block_general(hourly_activity_df)
    with row2_col2:
        st.write("Print 5 best users, or whatever you like (Eva)")

    row3_col1, row3_col2 = st.columns(2)
    with row3_col2:
        choose = st.radio("Choose", ["Precipitation", "Temperature"], horizontal=True, key="weather_general")

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        HR_zones_per_group(heart_rate_df)
    with row4_col2:
        plot_weather_vs_activity(weather_df, daily_activity_df, choose)

with id_tab:
    col1, col2 = st.columns([1, 6])
    with col1:
        Id = st.selectbox("Select user", options=sorted(load_unique_id()))
        section = st.radio("Section", ["General", "Activity", "Sleep", "Heart rate", "Calories", "Intensity"])

    with col2:
        if section == "General":
            m1, m2, m3, m4 = st.columns(4)
            id_class = classify_users()[classify_users()['Id'].astype(str) == Id]['Class'].values[0]
            id_daily_activity = daily_activity_df[daily_activity_df['Id'] == Id]
            m1.metric("You are a", id_class + " user")
            m2.metric("Average activity", f"{id_daily_activity['TotalSteps'].mean():.0f} steps")
            m3.metric("Date range",
                      f"{id_daily_activity.sort_values(by='ActivityDate')['ActivityDate'].iloc[0].strftime('%m/%d/%Y')}"
                      f" - {id_daily_activity.sort_values(by='ActivityDate')['ActivityDate'].iloc[-1].strftime('%m/%d/%Y')} ")
            m4.metric("Average sleep", f"Aimee")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.write("plot_user_activity_4_weeks(Id, connection)")  # Aimee
            with row1_col2:
                st.write("individual_sleep_activity_corr(Id, connection)")  # Aimee

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                view_by = st.radio("View by", ["Hour", "Day"], horizontal=True, key="hr_mean_general_tab", index=1)

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                plot_mean_heart_rate(heart_rate_df, Id, view_by)
            with row3_col2:
                st.write("Top 5 best activity dates (Aimee)")

        if section == "Activity":
            m1, m2, m3, m4 = st.columns(4)
            id_activity = daily_activity_df[daily_activity_df['Id'] == Id]

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
                st.write("plot_user_activity_4_weeks(Id, connection)")  # Aimee
            with row1_col2:
                plot_steps_by_block_per_id(Id, hourly_activity_df)

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
                st.write("individual_sleep_activity_corr(Id, connection)")  # Aimee
            with row1_col2:
                plot_sleep_sedentary_correlation(Id, daily_activity_df, daily_sleep_df)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                plot_sleep_by_block_per_id(minutes_sleep_df, Id)
            with row2_col2:
                st.write("Average sleep per day/week (Aimee)")  # Aimee

            row3_col1, row3_col2 = st.columns(2)
            with row3_col2:
                view_by = st.radio("View by", ["Day", "Week"], horizontal=True, key="sleep_min", index=1)

        if section == "Heart rate":
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Sample size", f"{len(heart_rate_df[heart_rate_df['Id'] == Id])} records")
            m2.metric("Median HR", f"{heart_rate_df[heart_rate_df['Id'] == Id]['Value'].median()} bpm")
            m3.metric("Max HR", f"{heart_rate_df[heart_rate_df['Id'] == Id]['Value'].max()} bpm")
            m4.metric("HR variability", f"{heart_rate_df[heart_rate_df['Id'] == Id]['Value'].std():.0f} bpm")

            view_by = st.radio("View by", ["Hour", "Day"], horizontal=True, key="hr_mean", index=1)

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                plot_mean_heart_rate(heart_rate_df, Id, view_by)
            with row1_col2:
                plot_heart_rate_vs_activity_with_intensity(heart_rate_df, hourly_activity_df, hourly_intensity_df, Id)

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


        if section == "Calories":
            avg_cal, max_cal, global_avg, vs_avg_pct = get_calories_metrics(daily_activity_df, Id)

            if vs_avg_pct >= 15:
                cal_category = " High Burner"
            elif vs_avg_pct <= -15:
                cal_category = " Low Burner"
            else:
                cal_category = " Average Burner"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Avg Daily Calories", f"{avg_cal:.0f} kcal")
            m2.metric("Peak Day Calories", f"{max_cal:.0f} kcal")
            m3.metric("vs. All Users", f"{vs_avg_pct:+.1f}%",
                      help=f"Global average: {global_avg:.0f} kcal/day")
            m4.metric("Burner Category", cal_category)

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                plot_regression_calories(daily_activity_df, Id)
            with row1_col2:
                plot_calories_by_block_per_id(hourly_calories_df, Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Eva do you have something about calories?")

            with row2_col2:
                st.write("plot_user_vs_global_calories(Id, connection)")  # Aimee

        if section == "Intensity":
            df_id_intensity = intensity_df[intensity_df["Id"] == Id]

            avg_intensity = df_id_intensity["AverageIntensity"].mean()
            max_intensity = df_id_intensity["TotalIntensity"].max()
            most_active_h = (df_id_intensity.groupby("Hour")["AverageIntensity"]
                             .mean().idxmax() if not df_id_intensity.empty else "N/A")
            weekend_avg = df_id_intensity[df_id_intensity["IsWeekend"]]["AverageIntensity"].mean()
            weekday_avg = df_id_intensity[~df_id_intensity["IsWeekend"]]["AverageIntensity"].mean()
            wk_diff = ((weekend_avg - weekday_avg) / weekday_avg * 100
                       if weekday_avg and weekday_avg != 0 else 0)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Avg Intensity", f"{avg_intensity:.2f}")
            m2.metric("Peak Total Intensity", f"{max_intensity}")
            m3.metric("Most Intense Hour", f"{most_active_h}:00")
            m4.metric("Weekend vs Weekday", f"{wk_diff:+.1f}%",
                      help="Positive = more intense on weekends")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                plot_intensity_by_hour_for_id(intensity_df, Id)
            with row1_col2:
                plot_steps_vs_intensity(intensity_df, hourly_activity_df, Id)

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.write("Heart rate vs intensity (Eva)")
            with row2_col2:
                plot_intensity_by_dow_for_id(intensity_df, Id)

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