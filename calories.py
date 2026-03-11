import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def plot_user_calories(Id):

    con = sqlite3.connect('fitbit_database.db')
    query = "SELECT * FROM daily_activity WHERE Id = ?"
    user_data = pd.read_sql_query(query, con, params=(Id,))
    con.close()

    if user_data.empty:
        print(f"No data found for ID: {Id}")
        return

    user_data['ActivityDate'] = pd.to_datetime(user_data['ActivityDate'])
    user_data = user_data.sort_values('ActivityDate')

    plt.figure(figsize=(10, 6))
    plt.plot(user_data['ActivityDate'], user_data['Calories'], marker='o', color='skyblue')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
    plt.title(f"Calories burned per day")
    plt.xlabel("Date")
    plt.ylabel("Calories burned")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', linestyle='-', alpha=0.5)
    plt.tight_layout()
    plt.show()

plot_user_calories(1503960366)