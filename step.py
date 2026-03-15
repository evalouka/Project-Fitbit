import pandas as pd
import sqlite3
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
import streamlit as st

bins   = [0, 4, 8, 12, 16, 20, 24]
labels = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]


@st.cache_resource
def get_connection():
    return sqlite3.connect("fitbit_database.db", check_same_thread=False)


# ─────────────────────────────────────────────
# 1. GENERAL TAB — Steps over day by 4-hour blocks (all users)
# ─────────────────────────────────────────────

def plot_steps_by_block_general():
    df = pd.read_sql_query("SELECT ActivityHour, StepTotal FROM hourly_steps", get_connection())
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df["Hour"] = df["ActivityHour"].dt.hour
    df["Block"] = pd.cut(df["Hour"], bins=bins, labels=labels, right=False)

    avg = df.groupby("Block", observed=True)["StepTotal"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color="#4C9BE8",
        marker_line_color="white",
        marker_line_width=1.5
    ))
    fig.update_layout(
        title="Average Steps per 4-Hour Block (All Users)",
        xaxis_title="Time Block (hours)",
        yaxis_title="Average Steps",
        yaxis=dict(gridcolor="rgba(0,0,0,0.15)"),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 2. PER ID — Activity steps per blocks of hours
# ─────────────────────────────────────────────

def plot_steps_by_block_per_id(selected_id):
    df = pd.read_sql_query("SELECT Id, ActivityHour, StepTotal FROM hourly_steps", get_connection())
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df["Hour"] = df["ActivityHour"].dt.hour
    df["Block"] = pd.cut(df["Hour"], bins=bins, labels=labels, right=False)
    df["Id"] = df["Id"].astype(str)

    user_df = df[df["Id"] == selected_id]
    avg = user_df.groupby("Block", observed=True)["StepTotal"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color="#4C9BE8",
        marker_line_color="white",
        marker_line_width=1.5
    ))
    fig.update_layout(
        title=f"Average Steps per 4-Hour Block — User {selected_id}",
        xaxis_title="Time Block (hours)",
        yaxis_title="Average Steps",
        yaxis=dict(gridcolor="rgba(0,0,0,0.15)"),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 3. PER ID — Sleep & Sedentary Minutes Correlation
# ─────────────────────────────────────────────

def plot_sleep_sedentary_correlation(selected_id):
    conn = get_connection()
    df_sleep = pd.read_sql_query("SELECT Id, date, value FROM minute_sleep", conn)
    df_sleep["date"] = pd.to_datetime(df_sleep["date"], format="%m/%d/%Y %I:%M:%S %p")
    df_sleep["Date"] = df_sleep["date"].dt.date
    df_sleep["Id"] = df_sleep["Id"].astype(str)

    df_activity = pd.read_sql_query("SELECT Id, ActivityDate, SedentaryMinutes FROM daily_activity", conn)
    df_activity["ActivityDate"] = pd.to_datetime(df_activity["ActivityDate"]).dt.date
    df_activity["Id"] = df_activity["Id"].astype(str)
    df_activity = df_activity.rename(columns={"ActivityDate": "Date"})

    sleep_daily = (
        df_sleep[(df_sleep["Id"] == selected_id) & (df_sleep["value"] == 1)]
        .groupby("Date")
        .size()
        .reset_index(name="SleepMinutes")
    )
    user_activity = df_activity[df_activity["Id"] == selected_id][["Date", "SedentaryMinutes"]]

    sleep_daily = sleep_daily.set_index("Date")
    user_activity = user_activity.set_index("Date")
    combined = sleep_daily.join(user_activity, how="inner").dropna().reset_index()

    if len(combined) < 2:
        st.warning(f"Not enough data for User {selected_id} to plot correlation.")
        return

    X = combined["SedentaryMinutes"].values
    y = combined["SleepMinutes"].values
    slope, intercept = np.polyfit(X, y, 1)
    x_line = np.linspace(X.min(), X.max(), 100)
    y_line = slope * x_line + intercept

    residuals = y - (slope * X + intercept)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = round(1 - ss_res / ss_tot, 4) if ss_tot != 0 else 0

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=X, y=y,
        mode='markers',
        marker=dict(color='steelblue', opacity=0.5, size=7),
        name='Data'
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        line=dict(color='red', width=2),
        name=f'y = {slope:.2f}x + {intercept:.2f}  |  R²={r2}'
    ))
    fig.update_layout(
        title=f"Sedentary Minutes vs Sleep Duration — User {selected_id}",
        xaxis_title="Sedentary Minutes",
        yaxis_title="Sleep Duration (minutes)",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 4. PER ID — Sleep per 4-hour block
# ─────────────────────────────────────────────

def plot_sleep_by_block_per_id(selected_id):
    df = pd.read_sql_query("SELECT Id, date, value FROM minute_sleep", get_connection())
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M:%S %p")
    df["Hour"] = df["date"].dt.hour
    df["Date"] = df["date"].dt.date
    df["Block"] = pd.cut(df["Hour"], bins=bins, labels=labels, right=False)
    df["Id"] = df["Id"].astype(str)

    user_df = df[(df["Id"] == selected_id) & (df["value"] == 1)]
    sleep_per_day = (
        user_df.groupby(["Date", "Block"], observed=True)
        .size()
        .reset_index(name="SleepMinutes")
    )
    avg = sleep_per_day.groupby("Block", observed=True)["SleepMinutes"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color="#9B4CE8",
        marker_line_color="white",
        marker_line_width=1.5
    ))
    fig.update_layout(
        title=f"Average Sleep Minutes per 4-Hour Block — User {selected_id}",
        xaxis_title="Time Block (hours)",
        yaxis_title="Average Minutes Asleep",
        yaxis=dict(gridcolor="rgba(0,0,0,0.15)"),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 5. PER ID — Calories per 4-hour block
# ─────────────────────────────────────────────

def plot_calories_by_block_per_id(selected_id):
    df = pd.read_sql_query("SELECT Id, ActivityHour, Calories FROM hourly_calories", get_connection())
    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df["Hour"] = df["ActivityHour"].dt.hour
    df["Block"] = pd.cut(df["Hour"], bins=bins, labels=labels, right=False)
    df["Id"] = df["Id"].astype(str)

    user_df = df[df["Id"] == selected_id]
    avg = user_df.groupby("Block", observed=True)["Calories"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color="#E8804C",
        marker_line_color="white",
        marker_line_width=1.5
    ))
    fig.update_layout(
        title=f"Average Calories per 4-Hour Block — User {selected_id}",
        xaxis_title="Time Block (hours)",
        yaxis_title="Average Calories",
        yaxis=dict(gridcolor="rgba(0,0,0,0.15)"),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)


