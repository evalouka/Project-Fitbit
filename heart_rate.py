import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm
from user_classification import classify_users
import matplotlib.cm as cm
import streamlit as st
import plotly.express as px



def mean_heart_rate_per_day(df, Id, view_by):
    # Filter the data for given Id
    heart_rate_df = df[df["Id"] == Id].copy()

    if heart_rate_df.empty:
        st.write("No heart rate data available for this user")
        return

    # Convert time to either hour or day, depending on the view by
    if view_by == "Hour":
        heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"]).dt.hour
        xlabel = "Hour of day"
        title = f"Mean heart rate per hour for user {Id}"
    else:
        heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"]).dt.date
        xlabel = "Date"
        title = f"Mean heart rate per day for user {Id}"

    # Convert value column to numeric
    heart_rate_df["Value"] = pd.to_numeric(heart_rate_df["Value"])

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

    fig.update_layout(height = 400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=xlabel,
                      yaxis_title="Heart rate",
                      font_color="white"
                      )

    st.plotly_chart(fig)

    # Print summary
    # print(means_heart_rate["Value"].describe())


def heart_rate_vs_activity(df1, df2, df3, Id):
    # Filter heart rate data for given Id
    heart_rate_df = df1[df1["Id"] == Id].copy()

    if heart_rate_df.empty:
        st.write("No heart rate data available for this user")
        return

    # Compute mean heart rate for each hour of each date
    heart_rate_df["Hour"] = pd.to_datetime(heart_rate_df["Time"]).dt.floor("H")
    means_heart_rate = heart_rate_df.groupby("Hour")["Value"].mean().reset_index()

    # Filter activity data for given Id
    hourly_activity_df = df2[df2["Id"] == Id].copy()
    hourly_activity_df["ActivityHour"] = pd.to_datetime(hourly_activity_df["ActivityHour"]).dt.floor("H")

    # Filter intensity data for given Id
    intensity_df = df3[df3["Id"] == Id].copy()
    intensity_df["ActivityHour"] = pd.to_datetime(intensity_df["ActivityHour"]).dt.floor("H")

    # Merge means heart rate into activity on Hour
    hourly_activity_df = hourly_activity_df.merge(means_heart_rate, left_on="ActivityHour", right_on="Hour")

    # Then merge als Intensity on Id and Hour
    hourly_activity_df = hourly_activity_df.merge(intensity_df, on = ["Id", "ActivityHour"], how = "left")

    # Scatterplot of Total Steps vs Heart Rate, colored by the Average Intensity
    fig = px.scatter(hourly_activity_df,
                     x= "StepTotal",
                     y= "Value",
                     color ="AverageIntensity",
                     title = f"Step total vs heart rate colored by the average intensity for user {Id}",
                     color_continuous_scale= "Blues",
                     )

    fig.update_layout(height = 400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Total Steps",
                      yaxis_title="Heart rate",
                      font_color="white")

    fig.update_coloraxes(colorbar_title = "Average Intensity")

    st.plotly_chart(fig)


    #Compute correlation between StepTotal and heart rate
    corr_steps = hourly_activity_df["StepTotal"].corr(hourly_activity_df["Value"])

    #Compute correlation between AverageIntensity and heart rate
    corr_intensity = hourly_activity_df["StepTotal"].corr(hourly_activity_df["AverageIntensity"])

    #Print correlations
    # print("Correlation between heart rate and total steps: " + str(corr_steps))
    # print("Correlation between heart rate and average intensity " + str(corr_intensity))

    #Print summary
    # print(hourly_activity_df[["StepTotal", "Value", "AverageIntensity"]].describe())

def HR_zones(df, Id, view_by):
    # Filter heart rate data for given Id
    heart_rate_df = df[df["Id"] == Id].copy()

    if heart_rate_df.empty:
        st.write("No heart rate data available for this user")
        return

    # Convert time to either hour or day, depending on the view by
    if view_by == "Hour":
        heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"]).dt.hour
        xlabel = "Hour of day"
        title = f"HR zones per hour for user {Id}"
    else:
        heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"]).dt.date
        xlabel = "Date"
        title = f"HR zones per day for user {Id}"

    # Compute max heart rate
    max_hr = heart_rate_df["Value"].max()

    # Create bins and labels for HR zones
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    labels = ["Rest", "Very Light", "Light", "Moderate", "Heavy", "Maximum"]

    # Assign a zone to each record for the Id, based on the percentage of the max heart rate
    heart_rate_df["Zone"] = pd.cut(heart_rate_df["Value"]/max_hr, bins= bins, labels = labels)

    # Calculate how many minutes are spent in each zone
    heart_rate_df["Minutes"] = 5 / 60
    zones_df = heart_rate_df.groupby(["Time", "Zone"])["Minutes"].sum().unstack()
    zones_df.columns = zones_df.columns.astype(str)

    # Convert to percentages
    zones_df["Total Minutes"] = zones_df[labels].sum(axis=1)
    zones_df["Rest"] = zones_df["Rest"] / zones_df["Total Minutes"]
    zones_df["Very Light"] = zones_df["Very Light"] / zones_df["Total Minutes"]
    zones_df["Light"] = zones_df["Light"] / zones_df["Total Minutes"]
    zones_df["Moderate"] = zones_df["Moderate"] / zones_df["Total Minutes"]
    zones_df["Heavy"] = zones_df["Heavy"] / zones_df["Total Minutes"]
    zones_df["Maximum"] = zones_df["Maximum"] / zones_df["Total Minutes"]


    zones_df = zones_df.reset_index()

    # Stacked bar chart of HR zones per day/hour
    fig = px.bar(zones_df,
                 x="Time",
                 y= labels,
                 title=title,
                 color_discrete_sequence=px.colors.sequential.Blues_r)

    fig.update_layout(barmode="stack",
                      height=400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=xlabel,
                      yaxis_title="Percentage",
                      font_color="white",
                      legend=dict(yanchor="top", y=1, xanchor="left", x=1.02),
                      )

    st.plotly_chart(fig)
    # Print dataframe
    # print(zones_df)

    #Print summary
    # print(zones_df.describe())


def mean_HR_per_group_compared_to_id(df, Id, selected):
    # Get report to know the class of each Id
    report = classify_users()
    report["Id"] = report["Id"].astype(str)

    heart_rate_df = df.copy()

    # Extract the hour of the dates
    heart_rate_df["Hour"] = pd.to_datetime(heart_rate_df["Time"], format= "%m/%d/%Y %I:%M:%S %p").dt.hour

    # Calculate mean heart rate per user for each hour of the day
    hourly_mean_HR_per_user = heart_rate_df.groupby(["Id", "Hour"]).mean().reset_index()
    hourly_mean_HR_per_user["Id"] = hourly_mean_HR_per_user["Id"].astype(str)

    # Merge heart rate dataframe with report on Id
    hourly_mean_HR_per_user = hourly_mean_HR_per_user.merge(report, on = "Id", how= "inner")

    # Calculate the hourly mean for each class
    hourly_mean_HR = hourly_mean_HR_per_user.groupby(["Class", "Hour"]).mean().reset_index()

    # Compute hourly mean heart rate for given Id
    id_mean = hourly_mean_HR_per_user[hourly_mean_HR_per_user["Id"] == str(Id)]
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
                  height = 400,
                  x = "Hour",
                  y = "Value",
                  color = "Class",
                  markers = True,
                  title = f"Mean heart rate per hour compared to class for user {Id}",
                  color_discrete_map=colors
    )

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Hour",
                      yaxis_title="Heart rate",
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

    #Print summary
    # print(hourly_mean_HR.groupby("Class")["Value"].describe())
    # print(f"Summary for user {Id}")
    # print(id_mean["Value"].describe())


def HR_zones_per_group(df):
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
    heart_rate_df["Minutes"] = 5 / 60
    zones_df = heart_rate_df.groupby(["Id", "Class", "Zone"])["Minutes"].sum().unstack()

    # Convert to percentages
    zones_df["Total Minutes"] = zones_df[labels].sum(axis = 1)
    zones_df["Rest"] = zones_df["Rest"] / zones_df["Total Minutes"]
    zones_df["Very Light"] = zones_df["Very Light"] / zones_df["Total Minutes"]
    zones_df["Light"] = zones_df["Light"] / zones_df["Total Minutes"]
    zones_df["Moderate"] = zones_df["Moderate"] / zones_df["Total Minutes"]
    zones_df["Heavy"] = zones_df["Heavy"] / zones_df["Total Minutes"]
    zones_df["Maximum"] = zones_df["Maximum"] / zones_df["Total Minutes"]


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
                      height=400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Class",
                      yaxis_title="Percentage",
                      font_color="white",
                      legend=dict(yanchor="top", y=1, xanchor="left", x=1.02),
                      )

    st.plotly_chart(fig)

    # Print summary for each zone by class
    # print("Summary of time spent in rest zone")
    # print(zones_df.groupby("Class")["Rest"].describe().to_string())
    # print("\nSummary of time spent in very light zone")
    # print(zones_df.groupby("Class")["Very Light"].describe().to_string())
    # print("\nSummary of time spent in light zone")
    # print(zones_df.groupby("Class")["Light"].describe().to_string())
    # print("\nSummary of time spent in moderate zone")
    # print(zones_df.groupby("Class")["Moderate"].describe().to_string())
    # print("\nSummary of time spent in heavy zone")
    # print(zones_df.groupby("Class")["Heavy"].describe().to_string())
    # print("\nSummary of time spent in maximum zone")
    # print(zones_df.groupby("Class")["Maximum"].describe().to_string())


    # Print number of light, moderate, and heavy users
    # print(heart_rate_df.drop_duplicates("Id")["Class"].value_counts())

    # Print the dataframe
    # print(zones_df)




















# HR_zones_per_group()
# mean_HR_per_group()

# HR_zones(2.022484408E9)

