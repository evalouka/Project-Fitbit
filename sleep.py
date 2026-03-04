import pandas as pd
import sqlite3

def get_sleep_minutes():
    con = sqlite3.connect("Aimee3\Project-Fitbit/fitbit_database.db")
    query = "SELECT Id, COUNT(*) as duration_minutes FROM minute_sleep WHERE value = 1 GROUP BY Id"
    df_user_sleep = pd.read_sql_query(query, con)
    
    if not df_user_sleep.empty:
        df_user_sleep['Id'] = df_user_sleep['Id'].astype(str)
    
    con.close()
    return df_user_sleep

def classify_user():
    con = sqlite3.connect("Aimee3\Project-Fitbit/fitbit_database.db")
    activity_query = "SELECT Id, SUM(VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) as total_active_minutes FROM daily_activity GROUP BY Id"
    df_activity = pd.read_sql_query(activity_query, con)
    df_activity['Id'] = df_activity['Id'].astype(str)

    con.close()
    return df_activity

def sleep_activity_corr():
    df_sleep = get_sleep_minutes()
    df_active = classify_user()

    df_combined = pd.merge(df_sleep, df_active, on="Id")

    if df_combined.empty:
        return "No matching data found between sleep and activity tables."

    correlation = df_combined['total_active_minutes'].corr(df_combined['duration_minutes'])
    print(f"Correlation Coefficient: {correlation:.2f}")

    if correlation > 0.7:
        print("Strong positive relationship")
    elif correlation > 0.3:
        print("Moderate positive relationship")
    else:
        print("Weak or no relationship")

    return df_combined

print(sleep_activity_corr())