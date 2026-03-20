import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


#grouping and averages
def get_hourly_avg(intensity_df):
    """Average intensity across all users by hour of day."""
    return intensity_df.groupby("Hour")[["TotalIntensity", "AverageIntensity"]].mean().round(2)


def get_dow_avg(intensity_df):
    """Average intensity by day of week."""
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return intensity_df.groupby("Day of Week")["AverageIntensity"].mean().reindex(dow_order).round(2)


def get_steps_intensity_merged(intensity_df, hourly_steps_df):
    """Merge intensity with steps on Id + ActivityHour for scatter plot."""
    return intensity_df.merge(hourly_steps_df, on=["Id", "ActivityHour"], how="inner")

#plot functions for all the users
def plot_avg_intensity_per_hour(intensity_df):
    """Line chart — average intensity for each hour of the day (all users)."""
    hourly_avg = get_hourly_avg(intensity_df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly_avg.index,
        y=hourly_avg["AverageIntensity"],
        mode="lines+markers",
        marker=dict(color=px.colors.sequential.Blues[7]),
        line=dict(color=px.colors.sequential.Blues[7]),
        name="Avg Intensity"
    ))
    fig.update_layout(
        title="Avg Intensity by Hour of Day",
        xaxis_title="Hour",
        yaxis_title="Average Intensity",
        xaxis=dict(tickvals=list(range(0, 24)))
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_avg_intensity_by_dow(intensity_df):
    """Bar chart — average intensity by day of week (all users)."""
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_avg = intensity_df.groupby("Day of Week")["AverageIntensity"].mean().reindex(dow_order).round(2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dow_avg.index.tolist(),
        y=dow_avg.values,
        marker_color="royalblue"
    ))
    fig.update_layout(
        title="Average intensity by Day of Week (All Users)",
        xaxis_title="Day of Week",
        yaxis_title="Average Intensity"
    )
    st.plotly_chart(fig, use_container_width=True)

#plot functions per user

def plot_steps_vs_intensity(intensity_df, hourly_steps_df, user_id):
    """Scatter plot — steps vs average intensity (all users)."""
    merged = intensity_df.merge(hourly_steps_df, on=["Id", "ActivityHour"], how="inner")
    merged  = merged[merged["Id"] == user_id]
    if merged.empty:
        st.info("No data available for this user")

    fig = px.scatter(
        merged,
        x="StepTotal",
        y="AverageIntensity",
        opacity=0.4,
        color_discrete_sequence=[px.colors.sequential.Blues[7]],
        title=f"Steps vs average intensity for user {user_id}",
        labels={"StepTotal": "Steps", "AverageIntensity": "Avg Intensity"}
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_intensity_by_hour_for_id(intensity_df, user_id):
    """Line chart — average intensity by hour of day for a single user."""
    df_id = intensity_df[intensity_df["Id"] == user_id]
    if df_id.empty:
        st.info("No data available for this user")
        return
    hourly_avg = df_id.groupby("Hour")["AverageIntensity"].mean().round(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly_avg.index,
        y=hourly_avg.values,
        mode="lines+markers",
        marker=dict(color=px.colors.sequential.Blues[7]),
        line=dict(color=px.colors.sequential.Blues[7]),
        name=f"User {user_id}"
    ))
    fig.update_layout(
        title=f"Average intensity by hour — User {user_id}",
        xaxis_title="Hour",
        yaxis_title="Average Intensity",
        xaxis=dict(tickvals=list(range(0, 24)))
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_intensity_by_dow_for_id(intensity_df, user_id):
    """Bar chart — average intensity by day of week for a single user."""
    df_id = intensity_df[intensity_df["Id"] == user_id]
    if df_id.empty:
        st.info("No data available for this user")
        return

    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_avg = df_id.groupby("Day of Week")["AverageIntensity"].mean().reindex(dow_order).round(2)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dow_avg.index.tolist(),
        y=dow_avg.values,
        marker_color= px.colors.sequential.Blues[7]
    ))
    fig.update_layout(
        title=f"Average intensity by day of week — User {user_id}",
        xaxis_title="Day of Week",
        yaxis_title="Average Intensity"
    )
    st.plotly_chart(fig, use_container_width=True)