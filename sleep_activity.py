import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
from sleep import get_global_sleep_minutes, get_users_sleep_minutes
from activity_logs import get_global_activity, get_user_activity

def get_global_sleep_averages(con):
    df_sleep = get_global_sleep_minutes(con)
    
    if not df_sleep.empty:
        df_sleep['avg_daily_sleep'] = df_sleep['sleep_minutes'] / df_sleep['sleep_day_count']
        df_sleep['Id'] = pd.to_numeric(df_sleep['Id'], errors='coerce').astype('Int64').astype(str)
        
    return df_sleep[['Id', 'avg_daily_sleep']]

def get_global_activity_averages(con):

    df_act = get_global_activity(con)
    
    if not df_act.empty:
        df_act['avg_daily_activity'] = df_act['total_active_minutes'] / df_act['activity_day_count']
        df_act['Id'] = pd.to_numeric(df_act['Id'], errors='coerce').astype('Int64').astype(str)
        
    return df_act[['Id', 'avg_daily_activity']]

def global_sleep_activity_corr(con):

    df_sleep_avg = get_global_sleep_averages(con)
    df_act_avg = get_global_activity_averages(con)
    df_combined = pd.merge(df_sleep_avg, df_act_avg, on="Id")

    if df_combined.empty:
        return "No matching data found."
    
    df_combined = df_combined.sort_values(by='avg_daily_sleep', ascending=True)
    df_combined = df_combined.reset_index(drop=True)
    
    corr_sleep_to_act = df_combined['avg_daily_sleep'].corr(df_combined['avg_daily_activity'])
    corr_act_to_sleep = df_combined['avg_daily_activity'].corr(df_combined['avg_daily_sleep'])

    print(f"Correlation: {corr_sleep_to_act:.2f}")
    print(f"Correlation: {corr_act_to_sleep:.2f}")

    if corr_sleep_to_act > 0.7:
        print("Strong positive relationship")
    elif corr_sleep_to_act > 0.3:
        print("Moderate positive relationship")
    else:
        print("Weak or no relationship")

    plt.figure(figsize=(10, 6))
    plt.scatter(df_combined['avg_daily_sleep'], df_combined['avg_daily_activity'], alpha=0.5, color='blue')

    m, b = np.polyfit(df_combined['avg_daily_sleep'], df_combined['avg_daily_activity'], 1)
    x_range = np.array([df_combined['avg_daily_sleep'].min(), df_combined['avg_daily_sleep'].max()])
    y_trend = m * x_range + b

    plt.plot(x_range, y_trend, color='red', linewidth=2, label="Trend Line")
    
    plt.title(f"Sleep vs Activity (Correlation: {corr_sleep_to_act:.2f})")
    plt.xlabel("Sleep minutes")
    plt.ylabel("Active Minutes")
    plt.grid(True)
    plt.show()

    return df_combined

def individual_sleep_activity_corr(user_id, con):

    df_sleep = get_users_sleep_minutes(user_id, con)
    df_active = get_user_activity(user_id, con)

    user_id_str = str(user_id)
    
    df_sleep['get_date'] = pd.to_datetime(df_sleep['clean_date'])
    df_active['get_date'] = pd.to_datetime(df_active['ActivityDate'])

    df_combined = pd.merge(df_sleep, df_active, on="get_date")

    if df_combined.empty:
        print(f"No matching dates found for user {user_id_str}.")
        return None

    correlation = df_combined['active_minutes'].corr(df_combined['duration_minutes'])
    
    print(f"--- Analysis for User {user_id_str} ---")
    print(f"Days of data: {len(df_combined)}")
    print(f"Correlation Coefficient: {correlation:.2f}")

    if correlation > 0.7:
        print("Strong positive relationship")
    elif correlation > 0.3:
        print("Moderate positive relationship")
    else:
        print("Weak or no relationship")

    plt.figure(figsize=(10, 6))
    plt.scatter(df_combined['active_minutes'], df_combined['duration_minutes'], color='blue', alpha=0.7)

    m, b = np.polyfit(df_combined['active_minutes'], df_combined['duration_minutes'], 1)
    plt.plot(df_combined['active_minutes'], m*df_combined['active_minutes'] + b, color='red')

    plt.title(f"Individual Correlation: Sleep vs Activity (User {user_id_str})")
    plt.xlabel("Daily Active Minutes")
    plt.ylabel("Daily Sleep Minutes")
    plt.grid(True)
    plt.show()

    return correlation

#individual_sleep_activity_corr(2347167796)
#individual_sleep_activity_corr(4319703577)
global_sleep_activity_corr()