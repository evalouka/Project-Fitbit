"""
This script provides functions for heart rate analysis and visualization.

The file contains functions to plot mean heart rate by day/hour, visualize the relationship between heart
rate and activity/intensity, visualize time spent in heart rate zones per user/class, and to compare the mean
heart rate of a user to different classes. In addition, it provides a visualization of the intensity and heart rate when performing
an exercise on a certain time and date. 

"""

import pandas as pd
from user_classification import classify_users
import streamlit as st
import plotly.express as px
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_mean_heart_rate(df, user_id, view_by):
    """
       Plot mean heart rate per day or hour for selected user.

       Args:
           df: heart rate dataframe containing "Id", "Time", and "Value"
           user_id: The Id of the user to analyze
           view_by: Determines whether to view by hour or day

       """

    # Filter the data for given Id
    heart_rate_df = df[df["Id"] == user_id].copy()

    if heart_rate_df.empty:
        st.info("No heart rate data available for this user")
        return

    # Convert time to either hour or day, depending on the view by
    if view_by == "Hour":
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.hour
        xlabel = "Hour of day"
        title = f"Average heart rate per hour for user {user_id}"
    else:
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.date
        xlabel = "Date"
        title = f"Average heart rate per day for user {user_id}"

    # Compute mean heart rate per hour or day
    means_heart_rate = heart_rate_df.groupby("Time")["Value"].mean().reset_index()

    # Plot heart rate means
    fig = px.line(means_heart_rate,
                  x= "Time",
                  y= "Value",
                  title = title,
                  markers = True,
                  color_discrete_sequence=[px.colors.sequential.Blues[4]]
                  )

    fig.update_layout(height = 450,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=xlabel,
                      yaxis_title="Mean heart rate (bpm)",
                      font_color="white"
                      )

    st.plotly_chart(fig)



def plot_heart_rate_vs_activity_with_intensity(hr_data, activity_data, intensity_data, user_id):
    """
         Plot mean heart rate per hour vs hourly activity, colored by the hourly average intensity.

         Args:
             hr_data: heart rate dataframe containing "Id", "Time", and "Value"
             activity_data: activity dataframe containing "Id", "ActivityHour", and StepTotal
             intensity_data: intensity dataframe containing "Id", "ActivityHour", and "AverageIntensity"
             user_id: The Id of the user to analyze

         """

    # Filter heart rate data for given user_id
    heart_rate_df = hr_data[hr_data["Id"] == user_id].copy()

    if heart_rate_df.empty:
        st.info("No heart rate data available for this user")
        return

    # Compute mean heart rate for each hour of each date
    heart_rate_df["Hour"] = heart_rate_df["Time"].dt.floor("H")
    means_heart_rate = heart_rate_df.groupby("Hour")["Value"].mean().reset_index()

    # Filter activity data for given user_id
    hourly_activity_df = activity_data[activity_data["Id"] == user_id].copy()
    if hourly_activity_df.empty:
        st.info("No activity data available for this user")
        return

    hourly_activity_df["ActivityHour"] = hourly_activity_df["ActivityHour"].dt.floor("H")

    # Filter intensity data for given user_id
    intensity_df = intensity_data[intensity_data["Id"] == user_id].copy()
    if intensity_df.empty:
        st.info("No intensity data available for this user")
        return

    intensity_df["ActivityHour"] = intensity_df["ActivityHour"].dt.floor("H")


    # Merge mean heart rate into activity by Hour
    hourly_activity_df = hourly_activity_df.merge(means_heart_rate, left_on="ActivityHour", right_on="Hour")

    # Then merge also Intensity on Id and Hour
    hourly_activity_df = hourly_activity_df.merge(intensity_df, on = ["Id", "ActivityHour"], how = "left")

    if hourly_activity_df.empty:
        st.info("No data available for this user")
        return

    # Scatterplot of Total Steps vs Heart Rate, colored by the Average Intensity
    fig = px.scatter(hourly_activity_df,
                     x= "StepTotal",
                     y= "Value",
                     color ="AverageIntensity",
                     title = f"Total steps vs mean heart rate per hour colored by the average intensity <br> for user {user_id}",
                     color_continuous_scale= "Blues",
                     )

    fig.update_layout(height = 470,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Total steps per hour",
                      yaxis_title="Mean heart rate (bpm)",
                      font_color="white")

    fig.update_coloraxes(colorbar_title = "Average Intensity")

    st.plotly_chart(fig)



def plot_hr_zones(df, user_id, view_by):
    """
          Plot proportion of observations spent in different heart rate zones per day or
          per hour for a selected user.

          Args:
              df: heart rate dataframe containing "Id", "Time", and "Value"
              user_id: The Id of the user to analyze
              view_by: Determines whether to view by hour or day

          """

    # Filter heart rate data for given Id
    heart_rate_df = df[df["Id"] == user_id].copy()

    if heart_rate_df.empty:
        st.info("No heart rate data available for this user")
        return

    # Convert time to either hour or day, depending on the view by
    if view_by == "Hour":
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.hour
        xlabel = "Hour of day"
        title = f"Heart rate zones distribution per hour for user {user_id}"
    else:
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.date
        xlabel = "Date"
        title = f"Heart rate zones distribution per day for user {user_id}"

    # Compute max heart rate
    max_hr = heart_rate_df["Value"].max()

    # Create bins and labels for HR zones
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    labels = ["Rest", "Very Light", "Light", "Moderate", "Heavy", "Maximum"]

    # Assign a zone to each record for the Id, based on the percentage of the max heart rate
    heart_rate_df["Zone"] = pd.cut(heart_rate_df["Value"]/max_hr, bins= bins, labels= labels)

    # Count observations in heart rate zones
    zones_df = heart_rate_df.groupby(["Time", "Zone"]).size().unstack()
    zones_df = zones_df.reindex(columns = labels, fill_value=0)

    # Convert to percentages
    zones_df["Total"] = zones_df[labels].sum(axis=1)
    for zone in labels:
        zones_df[zone] = zones_df[zone] / zones_df["Total"]

    zones_df = zones_df.reset_index()

    # Stacked bar chart of HR zones per day/hour
    fig = px.bar(zones_df,
                 x="Time",
                 y= labels,
                 title=title,
                 color_discrete_sequence=px.colors.sequential.Blues_r)

    fig.update_layout(barmode="stack",
                      height=450,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=xlabel,
                      yaxis_title="Proportion",
                      font_color="white",
                      legend=dict(yanchor="top", y=1, xanchor="left", x=1.02),
                      )

    st.plotly_chart(fig)
    st.caption("Heart rate zones are based on the user's observed maximum heart rate")



def mean_HR_per_group_compared_to_id(df, user_id, selected):
    """
           Plots the mean heart rate per hour of a selected user and compares it to the mean heart rate per hour
           of selected user classes.

           Args:
               df: Heart rate dataframe containing "Id", "Time", and "Value"
               user_id: The Id of the user to analyze
               selected: Determines which classes to compare to

           """

    # Get report to know the class of each Id
    report = classify_users()
    report["Id"] = report["Id"].astype('int64').astype(str)
    heart_rate_df = df.copy()
    heart_rate_df["Hour"] = heart_rate_df["Time"].dt.hour

    # Calculate mean heart rate per user for each hour of the day
    hourly_mean_HR_per_user = heart_rate_df.groupby(["Id", "Hour"])["Value"].mean().reset_index()

    # Merge heart rate dataframe with report on Id
    hourly_mean_HR_per_user = hourly_mean_HR_per_user.merge(report, on = "Id", how= "inner")

    # Calculate the hourly mean for each class
    hourly_mean_HR = hourly_mean_HR_per_user.groupby(["Class", "Hour"])["Value"].mean().reset_index()

    # Compute hourly mean heart rate for given Id
    id_mean = hourly_mean_HR_per_user[hourly_mean_HR_per_user["Id"] == user_id].copy()
    if id_mean.empty:
        st.info("No heart rate data available for this user")
        return
    id_mean["Class"] = "Id"

    selected_df = hourly_mean_HR[hourly_mean_HR["Class"].isin(selected)]
    selected_df = pd.concat([selected_df, id_mean])

    colors = {"Light": px.colors.sequential.Blues[1], "Moderate": px.colors.sequential.Blues[3],
              "Heavy": px.colors.sequential.Blues[5], "Id": px.colors.sequential.Blues[7]}

    fig = px.line(selected_df,
                  height = 470,
                  x = "Hour",
                  y = "Value",
                  color = "Class",
                  markers = True,
                  title = f"Average heart rate per hour compared to selected classes for <br> user {user_id}",
                  color_discrete_map=colors
    )

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Hour",
                      yaxis_title="Average heart rate (bpm)",
                      font_color="white",)

    st.plotly_chart(fig)
    # Compute the number of light, moderate, and heavy users for caption
    unique_id = hourly_mean_HR_per_user[["Id", "Class"]].drop_duplicates()
    heavy_count = (unique_id["Class"] == "Heavy").sum()
    moderate_count = (unique_id["Class"] == "Moderate").sum()
    light_count = (unique_id["Class"] == "Light").sum()
    st.caption(
        f"Based on {heavy_count} heavy user(s), {moderate_count} moderate user(s), and {light_count} "
        f"light user(s)")




def HR_zones_per_group(df):
    """
           Plot average proportion of observations spent in different heart rate zones per user class

           Args:
               df: heart rate dataframe containing "Id", "Time", and "Value"
           """

    # Get report to know the class of each Id
    report = classify_users()
    report["Id"] = report["Id"].astype('int64').astype(str)

    heart_rate_df = df.copy()

    # Merge heart rate dataframe with report
    heart_rate_df = heart_rate_df.merge(report, on = "Id", how = "left")

    # Add column Max HR to the dataframe containing the max heart rate
    heart_rate_df["Max HR"] = heart_rate_df.groupby("Id")["Value"].transform("max")

    # Create bins and labels for HR zones
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    labels = ["Rest", "Very Light", "Light", "Moderate", "Heavy", "Maximum"]

    #  Assign a zone to each record for the Id, based on the percentage of the max heart rate
    heart_rate_df["Zone"] = pd.cut(heart_rate_df["Value"] / heart_rate_df["Max HR"], bins=bins, labels=labels)

    # Count observations in heart rate zones spent in each zone
    zones_df = heart_rate_df.groupby(["Id", "Class", "Zone"]).size().unstack()
    zones_df = zones_df.reindex(columns=labels, fill_value=0)

    # Convert to percentages
    zones_df["Total"] = zones_df[labels].sum(axis=1)
    for zone in labels:
        zones_df[zone] = zones_df[zone] / zones_df["Total"]

    # Calculate mean percentage of each class in each zone
    zones_df = zones_df.groupby("Class").mean()

    # Reindex the columns to go from light to heavy
    zones_df = zones_df.reindex(["Light", "Moderate", "Heavy"])

    zones_df = zones_df.reset_index()

    # Stacked bar chart of HR zones per class
    fig = px.bar(zones_df,
                 x="Class",
                 y=labels,
                 title="Heart rate zone distribution per class",
                 color_discrete_sequence=px.colors.sequential.Blues_r)

    fig.update_layout(barmode="stack",
                      height=450,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Class",
                      yaxis_title="Proportion",
                      font_color="white",
                      legend=dict(yanchor="top", y=1, xanchor="left", x=1.02),

                      )

    st.plotly_chart(fig)

    # Compute the number of light, moderate, and heavy users for caption
    unique_id = heart_rate_df[["Id", "Class"]].drop_duplicates()
    heavy_count = (unique_id["Class"] == "Heavy").sum()
    moderate_count = (unique_id["Class"] == "Moderate").sum()
    light_count = (unique_id["Class"] == "Light").sum()
    st.caption(
        f"Based on {heavy_count} heavy user(s), {moderate_count} moderate user(s), and {light_count} "
        f"light user(s)")
    st.caption("Heart rate zones are based on the user's observed maximum heart rate")





def plot_user_data(user_id):
    # Connect to database
    conn = sqlite3.connect("fitbit_database.db")
    
    # --- Query heart rate ---
    heart_query = f"""
    SELECT Time, Value
    FROM heart_rate
    WHERE Id = {float(user_id)}
    """
    
    heart_df = pd.read_sql_query(heart_query, conn)
    
    # --- Query intensity ---
    intensity_query = f"""
    SELECT ActivityHour, TotalIntensity
    FROM hourly_intensity
    WHERE Id = {float(user_id)}
    """
    
    intensity_df = pd.read_sql_query(intensity_query, conn)
    
    conn.close()
    
    # --- Convert to datetime ---
    heart_df['Time'] = pd.to_datetime(heart_df['Time'], format='%m/%d/%Y %I:%M:%S %p')
    intensity_df['ActivityHour'] = pd.to_datetime(intensity_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p')
    
    # --- Create plot ---
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_yaxes(title_text="Heart Rate (bpm)", secondary_y=False)
    fig.update_yaxes(title_text="Total Intensity", secondary_y=True)

    fig.add_trace(go.Scatter(x=heart_df['Time'], y=heart_df['Value'],
              mode='lines', name='Heart Rate (bpm)',
              hovertemplate="Time: %{x}<br>Heart Rate: %{y} bpm<extra></extra>"), 
              secondary_y=False)
    fig.add_trace(go.Scatter(x=intensity_df['ActivityHour'], y=intensity_df['TotalIntensity'],
              mode='lines', name='Total Intensity',
              hovertemplate="Time: %{x}<br>Intensity: %{y}<extra></extra>"), 
              secondary_y=True)
    
    fig.update_layout(title=f"Heart Rate vs Exercise Intensity for User {user_id}")
    
    return fig