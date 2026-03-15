import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def plot_user_vs_global_calories(Id, con):

    user_query = "SELECT * FROM daily_activity WHERE Id = ?"
    user_df = pd.read_sql_query(user_query, con, params=(Id,))

    global_query = "SELECT ActivityDate, AVG(Calories) as average_calories FROM daily_activity GROUP BY ActivityDate"
    global_df = pd.read_sql_query(global_query, con)

    con.close()

    if user_df.empty:
        print(f"No data found for ID: {Id}")
        return

    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    user_df = user_df.sort_values('ActivityDate')

    global_df['ActivityDate'] = pd.to_datetime(global_df['ActivityDate'])
    global_df = global_df.sort_values('ActivityDate')

    plt.figure(figsize=(12, 6))
    plt.bar(user_df['ActivityDate'], user_df['Calories'], color="#2c94a0", label='User calories burend')
    plt.plot(global_df['ActivityDate'],global_df['average_calories'], color="#322ca0", label = 'Global calories burned', linestyle = '-')
    plt.xlim(user_df['ActivityDate'].min(), user_df['ActivityDate'].max())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    plt.title(f"Calories burned per day")
    plt.xlabel("Date")
    plt.ylabel("Calories burned")
    plt.xticks(rotation=45)
    plt.show()
