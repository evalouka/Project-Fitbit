import pandas as pd
import sqlite3


def get_fitbit_report():
    con = sqlite3.connect("fitbit_database.db")
    sleep_query = "SELECT Id, logId, COUNT(*) as duration_minutes FROM minute_sleep GROUP BY logId"
    df_sleep = pd.read_sql_query(sleep_query, con)
    df_sleep['Id'] = df_sleep['Id'].astype(str)
    df_sleep['logId'] = df_sleep['logId'].astype(str)

    activity_query = "SELECT Id, COUNT(*) as appearance_count FROM daily_activity GROUP BY Id"
    df_activity = pd.read_sql_query(activity_query, con)
    df_activity['Id'] = df_activity['Id'].astype(str)

    def classify_user(count):
        if count <= 10: return "Light user"
        if count <= 15: return "Moderate user"
        return "Heavy user"

    df_class = pd.DataFrame({
        'Id': df_activity['Id'],
        'Class': df_activity['appearance_count'].apply(classify_user)
    })

    final_df = pd.merge(df_sleep, df_class, on="Id", how="left")

    con.close()
    return final_df

full_report = get_fitbit_report()
print(full_report)



import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


def sedentary_sleep_regression():
    con = sqlite3.connect("fitbit_database.db")

    df_sleep = pd.read_sql_query("SELECT Id, date FROM minute_sleep", con)
    df_activity = pd.read_sql_query("SELECT Id, ActivityDate, SedentaryMinutes FROM daily_activity", con)
    con.close()

    # Extract just the date part (remove the time)
    df_sleep['date'] = pd.to_datetime(df_sleep['date']).dt.date
    df_activity['ActivityDate'] = pd.to_datetime(df_activity['ActivityDate']).dt.date

    df_sleep['Id'] = df_sleep['Id'].astype(str)
    df_activity['Id'] = df_activity['Id'].astype(str)

    # Count rows per person per day = total sleep minutes
    df_sleep = df_sleep.groupby(['Id', 'date']).size().reset_index(name='SleepMinutes')

    # Rename to match for merging
    df_activity = df_activity.rename(columns={'ActivityDate': 'date'})
    df = pd.merge(df_sleep, df_activity, on=['Id', 'date'], how='inner').dropna()

    print(f"Merged rows: {len(df)}")

    X = df['SedentaryMinutes'].values
    y = df['SleepMinutes'].values

    result = np.polyfit(X, y, 1)
    slope = result[0]
    intercept = result[1]
    y_pred = slope * X + intercept
    residuals = y - y_pred

    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - ss_res / ss_tot

    print(f"Intercept:   {intercept:.4f}")
    print(f"Slope:       {slope:.4f}")
    print(f"R-squared:   {r_squared:.4f}")

    #  Plot 1: Scatterplot + Regression Line
    plt.figure(figsize=(8, 5))
    plt.scatter(X, y, alpha=0.4, color='steelblue', label='Data')
    x_line = np.linspace(X.min(), X.max(), 200)
    plt.plot(x_line, slope * x_line + intercept, color='red', linewidth=2, label=f'y = {slope:.2f}x + {intercept:.2f}')
    plt.xlabel('Sedentary Minutes')
    plt.ylabel('Sleep Duration (minutes)')
    plt.title('Sedentary Activity vs Sleep Duration')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Plot 2 Q-Q Plot
    plt.figure(figsize=(8, 5))
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title('Q-Q Plot of Residuals\n(checks normality assumption)')
    plt.tight_layout()
    plt.show()

sedentary_sleep_regression()

#second part

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# connect to the database
conn = sqlite3.connect("fitbit_database.db")

# define 4-hour time blocks
bins   = [0, 4, 8, 12, 16, 20, 24]
labels = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]

def plot_steps_by_block(conn, bins=bins, labels=labels):
    # load hourly steps table from the database
    steps_df = pd.read_sql_query("SELECT ActivityHour, StepTotal FROM hourly_steps", conn)

    # convert ActivityHour column to datetime format
    steps_df["ActivityHour"] = pd.to_datetime(steps_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")

    # extract the hour from the datetime
    steps_df["Hour"] = steps_df["ActivityHour"].dt.hour

    # assign each row to a 4-hour block based on the hour
    steps_df["Block"] = pd.cut(steps_df["Hour"], bins=bins, labels=labels, right=False)

    # compute the average steps per block across all participants
    steps_avg = steps_df.groupby("Block", observed=True)["StepTotal"].mean()

    # plot the results as a bar plot
    plt.figure(figsize=(9, 5))
    plt.bar(steps_avg.index, steps_avg.values, color="#4C9BE8", edgecolor="white", width=0.6)
    plt.title("Average Steps per 4-Hour Block", fontsize=14, fontweight="bold")
    plt.xlabel("Time Block (hours)", fontsize=11)
    plt.ylabel("Average Steps", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("steps_by_block.png", dpi=150)
    plt.show()

# call it like this:
plot_steps_by_block(conn)

# CALORIES

# hourly calories table from the database
cal_df = pd.read_sql_query("SELECT ActivityHour, Calories FROM hourly_calories", conn)

# convert ActivityHour column to datetime format
cal_df["ActivityHour"] = pd.to_datetime(cal_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")

# extract the hour from the datetime
cal_df["Hour"] = cal_df["ActivityHour"].dt.hour

# assign each row to a 4-hour block based on the hour
cal_df["Block"] = pd.cut(cal_df["Hour"], bins=bins, labels=labels, right=False)

# compute the average calories burnt per block across all participants
cal_avg = cal_df.groupby("Block", observed=True)["Calories"].mean()

# plot the results as a barplot
plt.figure(figsize=(9, 5))
plt.bar(cal_avg.index, cal_avg.values, color="#E8804C", edgecolor="white", width=0.6)
plt.title("Average Calories Burnt per 4-Hour Block", fontsize=14, fontweight="bold")
plt.xlabel("Time Block (hours)", fontsize=11)
plt.ylabel("Average Calories", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("calories_by_block.png", dpi=150)
plt.show()

# SLEEP

# load minute sleep table from the database (each row = 1 minute)
sleep_df = pd.read_sql_query("SELECT date, value FROM minute_sleep", conn)

# convert date column to datetime format
sleep_df["date"] = pd.to_datetime(sleep_df["date"], format="%m/%d/%Y %I:%M:%S %p")

# extract the hour from the datetime
sleep_df["Hour"] = sleep_df["date"].dt.hour

# assign each row to a 4-hour block based on the hour
sleep_df["Block"] = pd.cut(sleep_df["Hour"], bins=bins, labels=labels, right=False)

# value == 1 means the participant was asleep; convert to integer (1 = asleep, 0 = not)
sleep_df["Asleep"] = (sleep_df["value"] == 1).astype(int)

# compute average minutes asleep per block (each row = 1 minute, so mean * 60 gives minutes)
sleep_avg = sleep_df.groupby("Block", observed=True)["Asleep"].mean() * 60

# plot the results as a bar plot
plt.figure(figsize=(9, 5))
plt.bar(sleep_avg.index, sleep_avg.values, color="#9B4CE8", edgecolor="white", width=0.6)
plt.title("Average Minutes of Sleep per 4-Hour Block", fontsize=14, fontweight="bold")
plt.xlabel("Time Block (hours)", fontsize=11)
plt.ylabel("Average Minutes Asleep", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("sleep_by_block.png", dpi=150)
plt.show()












