import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import scipy.stats as stats
from datetime import datetime
import matplotlib.dates as mdates

def get_global_activity():
    #returns how many active minutes each user has
    con = sqlite3.connect(r"C:\Users\jonge\PycharmProjects\Data Engineering\Aimee3\Project-Fitbit\fitbit_database.db")
    
    act_query = """SELECT Id, 
    COUNT(DISTINCT substr(ActivityDate, 1, 10)) as activity_day_count, 
    SUM(VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) as total_active_minutes 
    FROM daily_activity GROUP BY Id"""
    df_activity = pd.read_sql_query(act_query, con)

    if not df_activity.empty:
        df_activity['Id'] = pd.to_numeric(df_activity['Id'], errors= 'coerce')
        df_activity['Id'] = df_activity['Id'].astype('Int64').astype(str)
    con.close()

    return df_activity

def get_user_activity(user_id):

    con = sqlite3.connect(r"C:\Users\jonge\PycharmProjects\Data Engineering\Aimee3\Project-Fitbit\fitbit_database.db")
    query = "SELECT Id, ActivityDate, SUM(VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) as active_minutes FROM daily_activity WHERE Id = ? GROUP BY ActivityDate"
    df_activity = pd.read_sql_query(query, con, params=(user_id,))

    if not df_activity.empty:
        df_activity['Id'] = pd.to_numeric(df_activity['Id'], errors= 'coerce')
        df_activity['Id'] = df_activity['Id'].astype('Int64').astype(str)

    con.close()
    return df_activity

def get_daily_activity_all_users():
    #returns the daily active minutes for each user at each day
    con = sqlite3.connect(r"C:\Users\jonge\PycharmProjects\Data Engineering\Aimee3\Project-Fitbit\fitbit_database.db")
    query = "SELECT Id, ActivityDate, (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) as daily_active_minutes FROM daily_activity"
    df = pd.read_sql_query(query, con)
    con.close()

    df['Id'] = pd.to_numeric(df['Id'], errors='coerce')
    df['Id'] = df['Id'].astype('Int64').astype(str)
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
    return df

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

    print(f"You have {activity_count} activity entries over the last 2 months, therefore you are a {category}")
    return activity_count

def bar_average_activity_week():

    con = sqlite3.connect('fitbit_database.db')
    df = pd.read_sql_query("SELECT ActivityDate FROM daily_activity", con)
    con.close()

    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
    df['DayOfWeek'] = df['ActivityDate'].dt.day_name()

    day_count = df['DayOfWeek'].value_counts()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_count = day_count.reindex(day_order)

    plt.figure(figsize=(10, 6))
    plt.bar(day_count.index, day_count.values, color="#208f55", edgecolor='black')
    plt.title('Total Workout Frequency per Day of the Week', fontsize=15)
    plt.xlabel('Day of the Week')
    plt.ylabel('Total Number of Activities Logged')
    plt.grid(axis='y', linestyle='-', alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_global_activity_4_weeks():
    df = get_daily_activity_all_users()
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])

    last_day = df['ActivityDate'].max()
    first_day = last_day - pd.Timedelta(days=28)
    df_recent = df[df['ActivityDate'] >= first_day]
    daily_summary = df_recent.groupby('ActivityDate')['daily_sum'].mean().reset_index()

    plt.figure(figsize=(10, 5))
    plt.plot(daily_summary['ActivityDate'], daily_summary['daily_sum'], marker='o', linestyle='-', color="#2c53a0", linewidth=2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.title(f"Global activity over the last 4 weeks", fontsize=14)
    plt.xlabel("Date (Weekly Markers)")
    plt.ylabel("Total Active Minutes")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_user_activity_4_weeks(user_id):
    df = get_daily_activity_all_users()

    df['Id'] = df['Id'].astype(str).str.strip()
    get_id = str(user_id).strip()

    user_df = df[df['Id'] == get_id].copy()
    if user_df.empty:
        print(f"Error: User {get_id} can not be found in the availible dataset.")
        return
    
    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    last_day = df['ActivityDate'].max()
    first_day = last_day - pd.Timedelta(days=28)

    complete_df = user_df[user_df['ActivityDate'] >= first_day].sort_values('ActivityDate')
    
    if complete_df.empty:
        print(f"There was no activity from user {user_id} in the last 4 weeks.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(complete_df['ActivityDate'], complete_df['daily_sum'], marker='o', linestyle='-', color="#2c53a0", linewidth=2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.title(f"Your activity over the last 4 weeks", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Total Active Minutes")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

