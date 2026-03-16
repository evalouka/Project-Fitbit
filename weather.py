"""
This script provides functions to visualize the relationship between weather (Temperature and Precipitation)
and activity (TotalSteps).

This script provides a function that fits an OLS regression model with Id treated as a factor
and visualizes the relationship between Temperature/Precipitation and TotalSteps for a selected user,
as well as a function that visualizes the same relationship for the entire dataset.

"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import streamlit as st
import plotly.express as px

def plot_weather_vs_activity_per_id(df1, df2, Id, choose):
    """
        Create a figure that fits an OLS regression model with TotalSeps as response variable, Precipitation
        or Temperature as an independent variable (depending on choose), and Id as factor that affects
        the intercept of the regression line.

        Args:
            df1: weather dataframe containing "datetime", "temp", and "precip"
            df2: activity dataframe containing "Id", "ActivityDate", and "TotalSteps"
            Id: The Id of the user to analyze
            choose: determines to compare TotalSteps to Temperature or Precipitation

        Returns:
            Plotly figure object
        """

    merged_df = pd.merge(df1, df2, left_on="datetime", right_on="ActivityDate")

    if merged_df.empty:
        st.write("No activity data available")

    # Set y to response variable TotalSteps for regression
    y = merged_df["TotalSteps"]

    if choose == "Precipitation":
            x = "precip"
            xlabel = "Precipitation (mm)"
            title = f"Precipitation vs Total Steps for user {Id}"

    else:
            x = "temp"
            xlabel = "Temperature (Celsius)"
            title = f"Temperature vs Total Steps for user {Id}"


    # Make regression model for Precipitation vs TotalSteps
    x_reg = merged_df[x]
    id_dummies = pd.get_dummies(merged_df["Id"], drop_first=True)
    x_reg = pd.concat([x_reg, id_dummies], axis=1)
    x_reg = sm.add_constant(x_reg)
    result = sm.OLS(y, x_reg).fit()

    # Filter data for given Id
    id_df = merged_df[merged_df["Id"] == Id]

    if id_df.empty():
        st.write("No activity data available for this user")


    # Find regression line for Precipitation vs TotalSteps
    base = result.params["const"]
    id_variable = result.params.get(Id, 0.0)
    intercept = base + id_variable
    slope = result.params[x]
    x_line = np.linspace(id_df[x].min(), id_df[x].max(), 100)
    y_line = intercept + slope * x_line

    fig = px.scatter(id_df,
                    x=x,
                    y="TotalSteps",
                    opacity=0.2,
                    color_discrete_sequence=[px.colors.sequential.Blues[2]],
                    title=title)

    fig.add_scatter(x=x_line,
                   y=y_line,
                   mode="lines",
                   line=dict(color=px.colors.sequential.Blues[7]),
                   name="Regression")

    fig.update_layout(height=500,
                     paper_bgcolor="rgba(0,0,0,0)",
                     plot_bgcolor="rgba(0,0,0,0)",
                     xaxis_title=xlabel,
                     yaxis_title="Total Steps",
                     font_color="white")

    st.plotly_chart(fig)


def plot_weather_vs_activity(df1, df2, choose):
    """
        Create a figure that fits an OLS regression model with TotalSeps as response variable, and Precipitation
        or Temperature as an independent variable (depending on choose).

        Args:
            Args:
            df1: weather dataframe containing "datetime", "temp", and "precip"
            df2: activity dataframe containing "Id", "ActivityDate", and "TotalSteps"
            choose: determines to compare TotalSteps to Temperature or Precipitation

        Returns:
            Plotly figure object
        """

    # Merge the dataframes
    merged_df = pd.merge(df1, df2, left_on="datetime", right_on="ActivityDate")

    if merged_df.empty:
        st.write("No activity data available")

    # Set y to response variable TotalSteps for regression
    y = merged_df["TotalSteps"]

    # Set x to independent variable precip or temp depending on choose
    if choose == "Precipitation":
           x = "precip"
           xlabel = "Precipitation (mm)"
           title = "Precipitation vs Total Steps"

    else:
           x = "temp"
           xlabel = "Temperature (Celsius)"
           title = "Temperature vs Total Steps"


    # Compute means of independent variable x
    means = merged_df.groupby(x)["TotalSteps"].mean().reset_index()

    # Fit regression model
    x_reg = merged_df[x]
    x_reg = sm.add_constant(x_reg)
    result = sm.OLS(y,x_reg).fit()

    # Find regression line for Temperature vs TotalSteps
    intercept = result.params["const"]
    slope = result.params[x]
    x_line = np.linspace(merged_df[x].min(), merged_df[x].max(), 100)
    y_line = intercept + slope * x_line

    fig = px.scatter(merged_df,
                    x=x,
                    y= "TotalSteps",
                    opacity= 0.2,
                    color_discrete_sequence=[px.colors.sequential.Blues[2]],
                    title= title)

    fig.add_scatter(x = means[x],
                   y = means["TotalSteps"],
                   mode="markers",
                   marker= dict(color= px.colors.sequential.Blues[6]),
                   name = "Means")

    fig.add_scatter(x= x_line,
                   y = y_line,
                   mode ="lines",
                   line= dict(color= px.colors.sequential.Blues[7]),
                   name = "Regression")

    fig.update_layout(height = 500,
                     paper_bgcolor="rgba(0,0,0,0)",
                     plot_bgcolor="rgba(0,0,0,0)",
                     xaxis_title=xlabel,
                     yaxis_title="Total Steps",
                     font_color="white")

    st.plotly_chart(fig)






