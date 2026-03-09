import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from sleep import get_sleep_minutes


def sedentary_sleep_regression():

    # Get total sleep minutes per person (one row per Id)
    df_sleep = get_sleep_minutes()
    df_sleep["Id"] = df_sleep["Id"].astype(str)

    # Get total sedentary minutes per person by summing across all their days
    con = sqlite3.connect("fitbit_database.db")
    df_activity = pd.read_sql_query(
        """
        SELECT Id, SUM(SedentaryMinutes) AS SedentaryMinutes
        FROM daily
        
        _activity
        GROUP BY Id
        """,
        con
    )
    con.close()
    df_activity["Id"] = df_activity["Id"].astype(str)

    # Merge the two tables on Id so each row has
    # one person's total sleep and total sedentary minutes
    df = pd.merge(df_sleep, df_activity, on="Id", how="inner").dropna()
    print(f"Merged rows: {len(df)}")

    # Define sedentary minutes as the explanatory variable (X)
    # and sleep duration as the response variable (y)
    X = df["SedentaryMinutes"].values
    y = df["duration_minutes"].values

    # Fit a straight line through the data using least squares
    slope, intercept = np.polyfit(X, y, 1)
    y_pred = slope * X + intercept

    # Calculate residuals (difference between actual and predicted sleep)
    residuals = y - y_pred

    # Calculate R-squared to measure how well the line fits the data
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - ss_res / ss_tot

    print(f"Intercept:  {intercept:.4f}")
    print(f"Slope:      {slope:.4f}")
    print(f"R-squared:  {r_squared:.4f}")

    # Plot 1: scatter plot of the raw data with the regression line on top
    plt.figure(figsize=(8, 5))
    plt.scatter(X, y, alpha=0.4, color="steelblue", label="Data")
    x_line = np.linspace(X.min(), X.max(), 200)
    plt.plot(
        x_line,
        slope * x_line + intercept,
        color="red",
        linewidth=2,
        label=f"y = {slope:.2f}x + {intercept:.2f}",
    )
    plt.xlabel("Sedentary Minutes")
    plt.ylabel("Sleep Duration (minutes)")
    plt.title("Sedentary Activity vs Sleep Duration")
    plt.legend()
    plt.tight_layout()
    plt.savefig("sedentary_sleep_regression.png", dpi=150)
    plt.show()

    # Plot 2: Q-Q plot to visually check if residuals follow a normal distribution
    # If the points lie close to the diagonal line, normality holds
    plt.figure(figsize=(8, 5))
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title("Q-Q Plot of Residuals\n(normality check)")
    plt.tight_layout()
    plt.savefig("qq_plot.png", dpi=150)
    plt.show()

    # Plot 3: histogram of residuals with a normal curve overlaid
    # A bell-shaped histogram matching the red curve confirms normality
    plt.figure(figsize=(8, 5))
    plt.hist(residuals, bins=30, color="steelblue", edgecolor="white", density=True)
    mean, sigma = residuals.mean(), residuals.std()
    x_norm = np.linspace(residuals.min(), residuals.max(), 200)
    plt.plot(
        x_norm,
        stats.norm.pdf(x_norm, mean, sigma),
        color="red",
        linewidth=2,
        label="Normal curve",
    )
    plt.xlabel("Residual")
    plt.ylabel("Density")
    plt.title("Residuals Distribution\n(normality check)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("residuals_histogram.png", dpi=150)
    plt.show()

    return df


if __name__ == "__main__":
    sedentary_sleep_regression()

#second part

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Import get_sleep_minutes to get valid sleep Ids
from sleep import get_sleep_minutes

# Connect to the database
conn = sqlite3.connect("fitbit_database.db")

bins   = [0, 4, 8, 12, 16, 20, 24]
labels = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]


def plot_steps_by_block(conn, bins=bins, labels=labels):
    # Load hourly steps table from the database
    steps_df = pd.read_sql_query("SELECT ActivityHour, StepTotal FROM hourly_steps", conn)

    # Convert ActivityHour column to datetime format
    steps_df["ActivityHour"] = pd.to_datetime(steps_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")

    # Extract the hour from the datetime
    steps_df["Hour"] = steps_df["ActivityHour"].dt.hour

    # Assign each row to a 4-hour block based on the hour
    steps_df["Block"] = pd.cut(steps_df["Hour"], bins=bins, labels=labels, right=False)

    # Compute the average steps per block across all participants
    steps_avg = steps_df.groupby("Block", observed=True)["StepTotal"].mean()

    # Plot the results as a bar plot
    plt.figure(figsize=(9, 5))
    plt.bar(steps_avg.index, steps_avg.values, color="#4C9BE8", edgecolor="white", width=0.6)
    plt.title("Average Steps per 4-Hour Block", fontsize=14, fontweight="bold")
    plt.xlabel("Time Block (hours)", fontsize=11)
    plt.ylabel("Average Steps", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("steps_by_block.png", dpi=150)
    plt.show()


def plot_calories_by_block(conn, bins=bins, labels=labels):
    # Load hourly calories table from the database
    cal_df = pd.read_sql_query("SELECT ActivityHour, Calories FROM hourly_calories", conn)

    # Convert ActivityHour column to datetime format
    cal_df["ActivityHour"] = pd.to_datetime(cal_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")

    # Extract the hour from the datetime
    cal_df["Hour"] = cal_df["ActivityHour"].dt.hour

    # Assign each row to a 4-hour block based on the hour
    cal_df["Block"] = pd.cut(cal_df["Hour"], bins=bins, labels=labels, right=False)

    # Compute the average calories burnt per block across all participants
    cal_avg = cal_df.groupby("Block", observed=True)["Calories"].mean()

    # Plot the results as a barplot
    plt.figure(figsize=(9, 5))
    plt.bar(cal_avg.index, cal_avg.values, color="#E8804C", edgecolor="white", width=0.6)
    plt.title("Average Calories Burnt per 4-Hour Block", fontsize=14, fontweight="bold")
    plt.xlabel("Time Block (hours)", fontsize=11)
    plt.ylabel("Average Calories", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("calories_by_block.png", dpi=150)
    plt.show()


def plot_sleep_by_block(conn, bins=bins, labels=labels):
    # Call get_sleep_minutes() to get only the Ids that have sleep data
    df_valid_ids = get_sleep_minutes()
    valid_ids = df_valid_ids["Id"].tolist()

    # Load minute sleep table from the database (each row = 1 minute)
    sleep_df = pd.read_sql_query("SELECT Id, date, value FROM minute_sleep", conn)

    # Keep only Ids returned by get_sleep_minutes()
    sleep_df["Id"] = sleep_df["Id"].astype(str)
    sleep_df = sleep_df[sleep_df["Id"].isin(valid_ids)]

    # Convert date column to datetime format
    sleep_df["date"] = pd.to_datetime(sleep_df["date"], format="%m/%d/%Y %I:%M:%S %p")

    # Extract the hour from the datetime
    sleep_df["Hour"] = sleep_df["date"].dt.hour

    # Assign each row to a 4-hour block based on the hour
    sleep_df["Block"] = pd.cut(sleep_df["Hour"], bins=bins, labels=labels, right=False)

    # value == 1 means the participant was asleep; convert to integer (1 = asleep, 0 = not)
    sleep_df["Asleep"] = (sleep_df["value"] == 1).astype(int)

    # Compute average minutes asleep per block (each row = 1 minute, so mean * 60 gives minutes)
    sleep_avg = sleep_df.groupby("Block", observed=True)["Asleep"].mean() * 60

    # Plot the results as a bar plot
    plt.figure(figsize=(9, 5))
    plt.bar(sleep_avg.index, sleep_avg.values, color="#9B4CE8", edgecolor="white", width=0.6)
    plt.title("Average Minutes of Sleep per 4-Hour Block", fontsize=14, fontweight="bold")
    plt.xlabel("Time Block (hours)", fontsize=11)
    plt.ylabel("Average Minutes Asleep", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig("sleep_by_block.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    plot_steps_by_block(conn)
    plot_calories_by_block(conn)
    plot_sleep_by_block(conn)
    conn.close()
