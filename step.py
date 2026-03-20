import pandas as pd
import sqlite3
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px


def plot_steps_by_block_general(hourly_activity_df):
    """ GENERAL TAB — Steps over day by 4-hour blocks (all users) """
    df = hourly_activity_df.copy()

    if df.empty:
        st.info("No data available for this user")
        return

    # Sum steps per block per day, then average across days
    daily_block = df.groupby(["Id", "Date", "Block"], observed=True)["StepTotal"].sum().reset_index()
    avg = daily_block.groupby("Block", observed=True)["StepTotal"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color= px.colors.sequential.Blues[7],
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



def plot_steps_by_block_per_id(selected_id, hourly_activity_df):
    """ PER ID — Activity steps per blocks of hours """
    df = hourly_activity_df.copy()
    if df.empty:
        st.info("No data available for this user")
        return

    user_df = df[df["Id"] == selected_id]
    if user_df.empty:
        st.warning(f"No step data found for User {selected_id}.")
        return

    # Sum steps per block per day, then average across days
    daily_block = user_df.groupby(["Date", "Block"], observed=True)["StepTotal"].sum().reset_index()
    avg = daily_block.groupby("Block", observed=True)["StepTotal"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color=px.colors.sequential.Blues[7],
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


def plot_sleep_sedentary_correlation(selected_id, daily_activity_df, daily_sleep_df):
    """ PER ID — Sleep & Sedentary Minutes Correlation """
    df_sleep = daily_sleep_df.copy()
    df_sleep["Date"] = df_sleep["SleepDay"].dt.date

    if df_sleep.empty:
        st.info("No data available for this user")
        return

    df_activity = daily_activity_df.copy()
    if df_activity.empty:
        st.info("No data available for this user")
        return

    df_activity["Date"] = pd.to_datetime(df_activity["ActivityDate"]).dt.date


    sleep_daily = (
        df_sleep[(df_sleep["Id"] == selected_id)]
        .groupby("Date")["TotalMinutesAsleep"]
        .sum()
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
        marker=dict(color=px.colors.sequential.Blues[8], size=7),
        name='Data'
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        line=dict(color=px.colors.sequential.Blues[6], width=2),
        name=f'y = {slope:.2f}x + {intercept:.2f}  |  R²={r2}'
    ))
    fig.update_layout(
        title=f"Sedentary Minutes vs Sleep Duration — User {selected_id}",
        xaxis_title="Sedentary Minutes",
        yaxis_title="Sleep Duration (minutes)",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_sleep_by_block_per_id(sleep_data, selected_id):
    """ PER ID — Sleep per 4-hour block """
    df = sleep_data.copy()
    if df.empty:
        st.info("No data available for this user")
        return

    user_df = df[(df["Id"] == selected_id) & (df["value"] == 1)]
    if user_df.empty:
        st.warning(f"No sleep data found for User {selected_id}.")
        return

    sleep_per_day = (
        user_df.groupby(["Date", "Block"], observed=True)
        .size()
        .reset_index(name="SleepMinutes")
    )
    avg = sleep_per_day.groupby("Block", observed=True)["SleepMinutes"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color=px.colors.sequential.Blues[7],
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


def plot_calories_by_block_per_id(calories_data, selected_id):
    """  PER ID — Calories per 4-hour block """
    df = calories_data.copy()
    if df.empty:
        st.info("No data available for this user")
        return

    user_df = df[df["Id"] == selected_id]
    if user_df.empty:
        st.warning(f"No calorie data found for User {selected_id}.")
        return

    # Sum calories per block per day, then average across days
    daily_block = user_df.groupby(["Date", "Block"], observed=True)["Calories"].sum().reset_index()
    avg = daily_block.groupby("Block", observed=True)["Calories"].mean()

    fig = go.Figure(go.Bar(
        x=list(avg.index),
        y=list(avg.values),
        marker_color= px.colors.sequential.Blues[7],
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