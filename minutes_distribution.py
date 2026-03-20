"""
This script provides a function to visualize the distribution of activity minutes per day for a selected user.

"""

import streamlit as st
import plotly.express as px


def distribution_activity_minutes_for_id(df,user_id):
    """
           Plot distribution of activity minutes per day for a selected user.

           Args:
               df: Activity dataframe containing "Id", "ActivityDate", "VeryActiveMinutes", "FairlyActiveMinutes",
               "LightlyActiveMinutes", and "SedentaryMinutes"
               user_id: The Id of the user to analyze

           """

    # Filter activity data for given Id
    df_id = df[df["Id"] == user_id].copy()

    if df_id.empty:
        st.info("No activity data available for this user")
        return

    # Order the columns to go from Sedentary to VeryActive
    minutes_df = df_id[["ActivityDate", "SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"]].copy()

    # Rename columns
    minutes_df = minutes_df.rename(columns={"SedentaryMinutes": "Sedentary",
                                    "LightlyActiveMinutes": "Lightly active",
                                    "FairlyActiveMinutes": "Fairly active",
                                    "VeryActiveMinutes": "Very active"})

    labels = ["Sedentary", "Lightly active", "Fairly active", "Very active"]
    # Convert to percentages
    minutes_df["Total Minutes"] = minutes_df[labels].sum(axis=1)
    for zone in labels:
        minutes_df[zone] = minutes_df[zone] / minutes_df["Total Minutes"]

    # Stacked bar chart of the minutes dataframe
    fig = px.bar(minutes_df,
                 x = "ActivityDate",
                 y = ["Sedentary", "Lightly active", "Fairly active", "Very active"],
                 title = f"Daily distribution of activity minutes for user {user_id}",
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




