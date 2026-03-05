import streamlit as st
import os
from heart_rate import mean_heart_rate_per_day, HR_zones_per_group
from user_classification import classify_users
import pandas as pd
import sqlite3
from heart_rate import HR_zones

st.set_page_config(
page_title = "Fitbit Dashboard",
layout = "wide",
initial_sidebar_state = "expanded"
)

st.title("Fitbit Dashboard")

#Connect to data base
connection = sqlite3.connect("fitbit_database.db")

@st.cache_data
def load_hr_data():
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate)
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Id"] = heart_rate_df["Id"].astype(str)
    return heart_rate_df

@st.cache_data
def load_unique_id():
    return classify_users()["Id"].astype(str)

heart_rate_df = load_hr_data()

general_tab, id_tab = st.tabs(["General", "Id"])


with general_tab:
    col1, col2 = st.columns(2)
    with col1:
        HR_zones_per_group(heart_rate_df)
    with col2:
        st.write("Other plots here")

with id_tab:
    col1, col2 = st.columns([1,6])
    with col1:
        Id = st.selectbox("Select user", options=load_unique_id())
        section = st.radio("Section", ["General", "Activity", "Sleep", "Heart rate", "Calories"])

    with col2:
        if section == "General":
            st.write("General data here")
        if section == "Activity":
            st.write("Activity here")
        if section == "Sleep":
            st.write("Sleep here")
        if section == "Heart rate":
            col1, col2 = st.columns(2)
            with col1:
                mean_heart_rate_per_day(heart_rate_df, Id)
                HR_zones(heart_rate_df, Id)
        if section == "Calories":
            st.write("Calories here")


