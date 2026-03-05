import pandas as pd
import sqlite3

def get_sleep_minutes(user_id):
    con = sqlite3.connect("fitbit_database.db")
    query = "SELECT Id, COUNT(*) as duration_minutes FROM minute_sleep WHERE value >= 1 and Id = ?"
    df_user_sleep = pd.read_sql_query(query, con, params=(user_id,))
    
    if not df_user_sleep.empty:
        df_user_sleep['Id'] = df_user_sleep['Id'].astype(str)
    
    con.close()
    return df_user_sleep

def get_activity_global():
    con = sqlite3.connect("fitbit_database.db")
    classify_query = "SELECT Id, SUM(VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) as total_active_minutes FROM daily_activity GROUP BY Id"
    df_activity = pd.read_sql_query(classify_query, con)
    df_activity['Id'] = df_activity['Id'].astype(str)

    con.close()
    return df_activity

def classify_user(user_id):

    conn = sqlite3.connect('fitbit_database.db')
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM daily_activity WHERE Id = ?"
    cursor.execute(query, (user_id,))
    
    activity_count = cursor.fetchone()[0]
    conn.close()

    if activity_count == 0:
        return f"User {user_id} has no recorded activity."
    elif activity_count <= 10:
        category = "Light user"
    elif 11 <= activity_count <= 15:
        category = "Moderate user"
    else:
        category = "Heavy user"

    return f"User {user_id} has {activity_count} activity entries: {category}"

print(classify_user(1503960366))