import pandas as pd
import plotly.express as px
import streamlit as st

def get_users_sleep_minutes(user_id, df_sleep):
    df_user = df_sleep[df_sleep['Id'] == str(user_id)].copy()
    df_user_sleep = df_user.groupby(['Id', 'clean_date']).size().reset_index(name='duration_minutes')
    return df_user_sleep

def get_global_sleep_minutes(df_sleep):
    df_global = df_sleep.groupby('Id').agg(
        sleep_minutes=('value', 'count'),
        sleep_day_count=('clean_date', 'nunique')
    ).reset_index()
    return df_global

def total_avg_sleep_per_night(sleep_df):
    df = get_global_sleep_minutes(sleep_df)
    df['avg_per_night'] = df['sleep_minutes'] / df['sleep_day_count']
    return df[df['sleep_day_count'] > 0]['avg_per_night'].mean()

def get_average_sleep(Id, sleep_df, view_by):
    data_df = get_users_sleep_minutes(Id, sleep_df)
    data_df["clean_date"] = pd.to_datetime(data_df["clean_date"])

    plot_df = None
    x_col = ""
    title = ""
    xlabel = ""

    view_by = view_by.strip()

    if view_by == "Day":
        data_df["DayOfWeek"] = data_df["clean_date"].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        plot_df = data_df.groupby("DayOfWeek")["duration_minutes"].mean().reindex(day_order).reset_index()
        x_col = "DayOfWeek"
        xlabel = "Day of the week"
        title = f"Average sleep per day of the week for user {Id}"

    elif view_by == "Week":
        data_df["Week"] = data_df["clean_date"].dt.isocalendar().week.astype(int)
        plot_df = data_df.groupby("Week")["duration_minutes"].mean().reset_index()
        x_col = "Week"
        xlabel = "Week number"
        title = f"Average sleep per week for user {Id}"

    fig = px.bar(plot_df, x=x_col, y='duration_minutes', title=title)

    fig.update_traces(marker_color="#6d62c4",marker_line_color="white", marker_line_width=1.5)

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title=xlabel,
                      yaxis_title="Sleep minutes",
                      font_color="Black")
    
    st.plotly_chart(fig)
