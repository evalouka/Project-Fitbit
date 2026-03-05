import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import scipy.stats as stats
from sleep import get_sleep_minutes, get_activity_global

def get_activity_individual(user_id):

    con = sqlite3.connect("fitbit_database.db")
    query = "SELECT Id, SUM(VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) as total_active_minutes FROM daily_activity WHERE Id = ? GROUP BY Id"
    df_activity = pd.read_sql_query(query, con)
    df_activity = pd.read_sql_query(query, con, params=(user_id,))

    con.close()
    return df_activity

def sleep_activity_corr_ind(user_id):

    df_sleep = get_sleep_minutes(user_id)
    df_active = get_activity_individual(user_id)

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

    plt.figure(figsize=(8, 6))

    stats.probplot(df_combined['total_active_minutes'], dist="norm", plot=plt)
    
    plt.title("QQ-Plot: Checking Normality of Active Minutes")
    plt.xlabel("Theoretical Quantiles")
    plt.ylabel("Ordered Values (Active Minutes)")
    plt.grid(True)

    return df_combined

#def sleep_activity_corr_global():

sleep_activity_corr_ind(1503960366)