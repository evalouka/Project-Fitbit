import pandas as pd
import sqlite3
import plotly.express as px

def get_users_sleep_minutes(user_id, con):
    query = "SELECT Id, TRIM(SUBSTR(date, 1, INSTR(date, ' '))) as clean_date, COUNT(*) as duration_minutes FROM minute_sleep WHERE value >= 1 and Id = ? GROUP BY clean_date"
    df_user_sleep = pd.read_sql_query(query, con, params=(user_id,))

    if not df_user_sleep.empty:
        df_user_sleep['Id'] = pd.to_numeric(df_user_sleep['Id'], errors='coerce')
        df_user_sleep['Id'] = df_user_sleep['Id'].astype('Int64').astype(str)
        df_user_sleep['clean_date'] = pd.to_datetime(df_user_sleep['clean_date']).dt.date
    
    #con.close()
    return df_user_sleep

def get_global_sleep_minutes(con):

    query = "SELECT Id, COUNT(*) as sleep_minutes, COUNT(DISTINCT substr(date, 1, 10)) as sleep_day_count FROM minute_sleep WHERE value >= 1 GROUP BY Id"
    df_total_sleep = pd.read_sql_query(query, con)
    
    if not df_total_sleep.empty:
        df_total_sleep['Id'] = pd.to_numeric(df_total_sleep['Id'], errors='coerce')
        df_total_sleep['Id'] = df_total_sleep['Id'].astype('Int64').astype(str)
    
    #con.close()
    return df_total_sleep

def get_average_sleep(Id, con, view_by):
    data_df = get_users_sleep_minutes(Id, con)

    if view_by == "Day":
        data_df["clean_date"] = pd.to_datetime(data_df["clean_date"])
        xlabel = "Amount of sleep minutes"
        title = f"Average sleep per day {Id}"
    elif view_by == "Week":
        data_df["clean_date"] = pd.to_datetime(data_df["clean_date"]).by.week
        xlabel = "Date"
        title = f"Mean heart rate per day for user {Id}"

    fig = px.line(data_df, x='ActivityDate', y='duration_minutes', title=title, markers=True)

    fig.update_traces(line=dict(color="#62c4bc", width=2))

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title= xlabel,
                      yaxis_title= "Activity minutes",
                      font_color="Black")
    
    fig.show()
    

#view_by = "Total activity"
#Id = 4319703577
#con = sqlite3.connect(r"C:\Users\jonge\PycharmProjects\Data Engineering\Project-Fitbit\fitbit_database.db")
