
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm
from user_classification import classify_users
import matplotlib.cm as cm
import streamlit as st
import plotly.express as px


def stacked_bar_chart_for_id(df,Id):
    # Filter activity data for given Id
    df_id = df[df["Id"] == Id].copy()

    # Order the columns to go from Sedentary to VeryActive
    minutes_df = df_id[["ActivityDate", "SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"]].copy()

    # Convert to percentages
    minutes_df["Total Minutes"] = minutes_df[["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]].sum(axis=1)
    minutes_df["SedentaryMinutes"] = minutes_df["SedentaryMinutes"] / minutes_df["Total Minutes"]
    minutes_df["LightlyActiveMinutes"] = minutes_df["LightlyActiveMinutes"] / minutes_df["Total Minutes"]
    minutes_df["FairlyActiveMinutes"] = minutes_df["FairlyActiveMinutes"] / minutes_df["Total Minutes"]
    minutes_df["VeryActiveMinutes"] = minutes_df["VeryActiveMinutes"] / minutes_df["Total Minutes"]

    # Stacked bar chart of the minutes dataframe
    fig = px.bar(minutes_df,
                 x = "ActivityDate",
                 y = ["SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"],
                 title = "Minutes distribution",
                 color_discrete_sequence= px.colors.sequential.Blues_r)

    fig.update_layout(barmode ="stack",
                      paper_bgcolor ="rgba(0,0,0,0)",
                      plot_bgcolor = "rgba(0,0,0,0)",
                      xaxis_title = "Date",
                      yaxis_title = "Percentage",
                      font_color = "white",
                      legend = dict(yanchor = "top", y =1, xanchor ="left", x = 1.02),
                      )

    st.plotly_chart(fig)




