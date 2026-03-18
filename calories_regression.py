"""
This script provides a function that fits an OLS regression model with Id treated as a factor
and visualizes the relationship between calories and TotalSteps for a selected user.

"""

import pandas as pd
import statsmodels.api as sm
import streamlit as st
import numpy as np
import plotly.express as px

def plot_regression_calories(df, Id):
    """
       Create a figure that fits an OLS regression model with Calories as response variable, TotalSteps as an
       independent variable, and Id as factor that affects the intercept of the regression line.

       Args:
           df: activity dataframe containing "Id", "Calories", and "TotalSteps"
           Id: The Id of the user to analyze

       Returns:
          Plotly figure object
       """

    # Store calories in response variable y
    y = df["Calories"]

    # Store calories in independent variable x
    x = df[["TotalSteps"]]

    # Filter data for given Id
    df_id = df[df["Id"] == Id]

    if df_id.empty:
        st.write("No calories data available")
        return

    # Add dummy columns to account for ID factor
    id_dummies = pd.get_dummies(df["Id"], drop_first=True)
    x = pd.concat([x, id_dummies], axis=1)

    # Add a constant to ensure an intercept
    x = sm.add_constant(x)

    # Fit the model
    model = sm.OLS(y, x)
    results = model.fit()

    # Compute base intercept and the id variable to compute the intercept for a given ID
    base = results.params["const"]
    id_variable = results.params.get(Id,0.0)
    intercept = base + id_variable

    # Compute the slope of the regression line
    slope = results.params["TotalSteps"]

    # Store the regression line
    x_line = np.linspace(df_id["TotalSteps"].min(),df_id["TotalSteps"].max(),100)
    y_line = intercept + slope*x_line

    fig = px.scatter(df_id,
                     x= "TotalSteps",
                     y="Calories",
                     color_discrete_sequence=[px.colors.sequential.Blues[2]],
                     title=f"Calories vs Total Steps for user {Id}")

    fig.add_scatter(x=x_line,
                    y=y_line,
                    mode="lines",
                    line=dict(color=px.colors.sequential.Blues[7]),
                    name="Regression")

    fig.update_layout(height=450,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Total Steps",
                      yaxis_title="Calories",
                      font_color="white")

    st.plotly_chart(fig)

