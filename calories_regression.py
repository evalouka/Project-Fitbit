import pandas as pd
import statsmodels.api as sm
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from sympy.physics.units import minutes
import plotly.express as px

def regression_calories(df, Id):
    # Store calories in dependent variably y
    y = df["Calories"]

    # Store calories in independent variably x
    x = df[["TotalSteps"]]

    # Add dummy columns to account for ID factor
    id_dummies = pd.get_dummies(df["Id"], drop_first=True)
    x = pd.concat([x, id_dummies], axis=1)

    # Add constants to ensure an intercept
    x = sm.add_constant(x)

    # Fit the model
    model = sm.OLS(y, x)
    results = model.fit()

    # Find data belonging to the given ID and make a scatterplot
    df_id = df[df["Id"] == Id]

    if df_id.empty:
        st.write("No calories data available")
        return


    # Copmute base intercept and the id variable to compute the intercept for a given ID
    base = results.params["const"]
    id_variable = results.params.get(Id,0.0)
    intercept = base + id_variable

    # Compute the slope of the regression line
    slope = results.params["TotalSteps"]

    # Store the regression line
    x_line = np.linspace(df_id["TotalSteps"].min(),df_id["TotalSteps"].max(),100)
    y_line = intercept + slope*x_line

    # Scatterplot of TotalSteps vs Calories
    fig = px.scatter(df_id,
                     x= "TotalSteps",
                     y="Calories",
                     color_discrete_sequence=[px.colors.sequential.Blues[2]],
                     title=f"Calories burned vs total steps taken for user {Id}")

    # Add regression line
    fig.add_scatter(x=x_line,
                    y=y_line,
                    mode="lines",
                    line=dict(color=px.colors.sequential.Blues[7]),
                    name="Regression")

    # Update layout of the figure
    fig.update_layout(height=500,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Total Steps",
                      yaxis_title="Calories",
                      font_color="white")

    st.plotly_chart(fig)

