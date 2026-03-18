"""
This script provides functions for heart rate analysis and visualization.

The file contains functions to plot mean heart rate by day/hour, visualize the relationship between heart
rate and activity/intensity, visualize time spent in heart rate zones per user/class, and to compare the mean
heart rate of a user to different classes.

"""

import pandas as pd
from user_classification import classify_users
import streamlit as st
import plotly.express as px


def plot_mean_heart_rate(df, Id, view_by):
    """
       Plot mean heart rate per day or hour for selected user.

       Args:
           df: heart rate dataframe containing "Id", "Time", and "Value"
           Id: The Id of the user to analyze
           view_by: Determines whether to view by hour or day

       Returns:
            plotly figure object
       """

    # Filter the data for given Id
    heart_rate_df = df[df["Id"] == Id].copy()

    if heart_rate_df.empty:
        st.write("No heart rate data available for this user")
        return

    # Convert time to either hour or day, depending on the view by
    if view_by == "Hour":
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.hour
        xlabel = "Hour of day"
        title = f"Mean heart rate per hour for user {Id}"
    else:
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.date
        xlabel = "Date"
        title = f"Mean heart rate per day for user {Id}"

    # Convert value column to numeric
    # heart_rate_df["Value"] = pd.to_numeric(heart_rate_df["Value"])

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
                      yaxis_title="Mean heart rate",
                      font_color="white"
                      )

    st.plotly_chart(fig)



def plot_heart_rate_vs_activity_with_intensity(df1, df2, df3, Id):
    """
         Plot mean heart rate per hour vs hourly activity, colored by the hourly average intensity.

         Args:
             df1: heart rate dataframe containing "Id", "Time", and "Value"
             df2: activity dataframe containing "Id", "ActivityHour", and StepTotal
             df3: intensity dataframe containing "Id", "ActivityHour", and "AverageIntensity"
             Id: The Id of the user to analyze

         Returns:
              plotly figure object
         """


    # Filter heart rate data for given Id
    heart_rate_df = df1[df1["Id"] == Id].copy()

    if heart_rate_df.empty:
        st.write("No heart rate data available for this user")
        return

    # Compute mean heart rate for each hour of each date
    heart_rate_df["Hour"] = heart_rate_df["Time"].dt.floor("H")
    means_heart_rate = heart_rate_df.groupby("Hour")["Value"].mean().reset_index()

    # Filter activity data for given Id
    hourly_activity_df = df2[df2["Id"] == Id].copy()
    hourly_activity_df["ActivityHour"] = hourly_activity_df["ActivityHour"].dt.floor("H")

    if hourly_activity_df.empty:
        st.write("No activity data available for this user")
        return

    # Filter intensity data for given Id
    intensity_df = df3[df3["Id"] == Id].copy()
    intensity_df["ActivityHour"] = intensity_df["ActivityHour"].dt.floor("H")

    if intensity_df.empty:
        st.write("No intensity data available for this user")
        return

    # Merge mean heart rate into activity by Hour
    hourly_activity_df = hourly_activity_df.merge(means_heart_rate, left_on="ActivityHour", right_on="Hour")

    # Then merge also Intensity on Id and Hour
    hourly_activity_df = hourly_activity_df.merge(intensity_df, on = ["Id", "ActivityHour"], how = "left")

    # Scatterplot of Total Steps vs Heart Rate, colored by the Average Intensity
    fig = px.scatter(hourly_activity_df,
                     x= "StepTotal",
                     y= "Value",
                     color ="AverageIntensity",
                     title = f"Total steps vs mean heart rate per hour colored by the average intensity <br> for user {Id}",
                     color_continuous_scale= "Blues",
                     )

    fig.update_layout(height = 470,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Total Steps",
                      yaxis_title="Mean heart rate",
                      font_color="white")

    fig.update_coloraxes(colorbar_title = "Average Intensity")

    st.plotly_chart(fig)



def plot_hr_zones(df, Id, view_by):
    """
          Plot proportion of observations spent in different heart rate zones per day or
          average proportion per hour for a selected user.

          Args:
              df: heart rate dataframe containing "Id", "Time", and "Value"
              Id: The Id of the user to analyze
              view_by: Determines whether to view by hour or day

          Returns:
               plotly figure object
          """

    # Filter heart rate data for given Id
    heart_rate_df = df[df["Id"] == Id].copy()

    if heart_rate_df.empty:
        st.write("No heart rate data available for this user")
        return

    # Convert time to either hour or day, depending on the view by
    if view_by == "Hour":
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.hour
        xlabel = "Hour of day"
        title = f"Average heart rate zones distribution per hour for user {Id}"
    else:
        heart_rate_df["Time"] = heart_rate_df["Time"].dt.date
        xlabel = "Date"
        title = f"Heart rate zones distribution per day for user {Id}"

    # Compute max heart rate
    max_hr = heart_rate_df["Value"].max()

    # Create bins and labels for HR zones
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    labels = ["Rest", "Very Light", "Light", "Moderate", "Heavy", "Maximum"]

    # Assign a zone to each record for the Id, based on the percentage of the max heart rate
    heart_rate_df["Zone"] = pd.cut(heart_rate_df["Value"]/max_hr, bins= bins, labels = labels)

    # Count observations in heart rate zone
    zones_df = heart_rate_df.groupby(["Time", "Zone"]).size().unstack()
    zones_df.columns = zones_df.columns.astype(str)
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
                      yaxis_title="Percentage",
                      font_color="white",
                      legend=dict(yanchor="top", y=1, xanchor="left", x=1.02),
                      )

    st.plotly_chart(fig)



def mean_HR_per_group_compared_to_id(df, Id, selected):
    """
           Plots the mean heart rate per hour of a selected user and compare to the mean heart rate per hour
           of selected user classes.

           Args:
               df: heart rate dataframe containing "Id", "Time", and "Value"
               Id: The Id of the user to analyze
               selected: Determines which classes to compare to

           Returns:
                plotly figure object
           """

    # Get report to know the class of each Id
    report = classify_users()
    report["Id"] = report["Id"].astype(str)

    heart_rate_df = df.copy()

    # Extract the hour of the dates
    heart_rate_df["Hour"] = heart_rate_df["Time"].dt.hour

    # Calculate mean heart rate per user for each hour of the day
    hourly_mean_HR_per_user = heart_rate_df.groupby(["Id", "Hour"]).mean().reset_index()

    # Merge heart rate dataframe with report on Id
    hourly_mean_HR_per_user = hourly_mean_HR_per_user.merge(report, on = "Id", how= "inner")

    # Calculate the hourly mean for each class
    hourly_mean_HR = hourly_mean_HR_per_user.groupby(["Class", "Hour"]).mean().reset_index()

    # Compute hourly mean heart rate for given Id
    id_mean = hourly_mean_HR_per_user[hourly_mean_HR_per_user["Id"] == str(Id)].copy()
    if id_mean.empty:
        st.write("No heart rate data available for this user")
        return
    id_mean["Class"] = "Id"

    # Create a dataframe containing only the selected groups
    selected_df = hourly_mean_HR[hourly_mean_HR["Class"].isin(selected)]
    selected_df = pd.concat([selected_df, id_mean])

    # Create colorscheme
    colors = {"Light": px.colors.sequential.Blues[1], "Moderate": px.colors.sequential.Blues[3],
              "Heavy": px.colors.sequential.Blues[5], "Id": px.colors.sequential.Blues[7]}

    # Line plot of heart rate means
    fig = px.line(selected_df,
                  height = 470,
                  x = "Hour",
                  y = "Value",
                  color = "Class",
                  markers = True,
                  title = f"Mean heart rate per hour compared to selected classes for user {Id}",
                  color_discrete_map=colors
    )

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Hour",
                      yaxis_title="Mean heart rate",
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

           Returns:
                plotly figure object
           """

    # Get report to know the class of each Id
    report = classify_users()
    report["Id"] = report["Id"].astype(str)

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

    # Calculate how many minutes are spent in each zone
    zones_df = heart_rate_df.groupby(["Time", "Class", "Zone"]).size().unstack()
    zones_df.columns = zones_df.columns.astype(str)
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
                      yaxis_title="Percentage",
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



