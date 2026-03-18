"""
This script provides a function to visualize the distribution of activity minutes per day for a selected user.

"""

import streamlit as st
import plotly.express as px


def distribution_activity_minutes_for_id(df,Id):
    """
           Plot distribution of activity minutes per day for a selected user.

           Args:
               df: activity dataframe containing "Id", "ActivityDate", "VeryActiveMinutes", "FairlyActiveMinutes",
               "LightlyActiveMinutes", and "SedentaryMinutes"

           Returns:
                plotly figure object
           """

    # Filter activity data for given Id
    df_id = df[df["Id"] == Id].copy()

    if df_id.empty:
        st.write("No activity data available for this user")
        return

    # Order the columns to go from Sedentary to VeryActive
    minutes_df = df_id[["ActivityDate", "SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"]].copy()

    labels = ["SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"]
    # Convert to percentages
    minutes_df["Total Minutes"] = minutes_df[labels].sum(axis=1)
    for zone in labels:
        minutes_df[zone] = minutes_df[zone] / minutes_df["Total Minutes"]

    # Stacked bar chart of the minutes dataframe
    fig = px.bar(minutes_df,
                 x = "ActivityDate",
                 y = ["SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"],
                 title = f"Daily distribution of activity minutes for user {Id}",
                 color_discrete_sequence= px.colors.sequential.Blues_r)

    fig.update_layout(barmode ="stack",
                      height = 450,
                      paper_bgcolor ="rgba(0,0,0,0)",
                      plot_bgcolor = "rgba(0,0,0,0)",
                      xaxis_title = "Date",
                      yaxis_title = "Proportion",
                      font_color = "white",
                      legend = dict(yanchor = "top", y =1, xanchor ="left", x = 1.02),
                      )

    st.plotly_chart(fig)




