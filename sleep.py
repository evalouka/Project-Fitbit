import pandas as pd
import sqlite3

def get_users_sleep_minutes(user_id):
    con = sqlite3.connect("fitbit_database.db")
    query = "SELECT Id, COUNT(*) as duration_minutes FROM minute_sleep WHERE value >= 1 and Id = ?"
    df_user_sleep = pd.read_sql_query(query, con, params=(user_id,))
    
    if not df_user_sleep.empty:
        df_user_sleep['Id'] = df_user_sleep['Id'].astype(str)
    
    con.close()
    return df_user_sleep

def get_global_sleep_minutes():

    con = sqlite3.connect("fitbit_database.db")
    query = "SELECT Id, COUNT(*) as duration_minutes FROM minute_sleep WHERE value >= 1 GROUP BY Id"
    df_total_sleep = pd.read_sql_query(query, con)
    
    if not df_total_sleep.empty:
        df_total_sleep['Id'] = pd.to_numeric(df_total_sleep['Id'], errors='coerce')
        df_total_sleep['Id'] = df_total_sleep['Id'].astype('Int64').astype(str)
    
    con.close()
    return df_total_sleep
