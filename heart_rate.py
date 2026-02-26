import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm

#Connect to data base
connection = sqlite3.connect("fitbit_database.db")


def mean_heart_rate_per_day(Id):
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate WHERE Id = ?"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate, (float(Id),))
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    print(heart_rate_df.head())
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"]).dt.date
    heart_rate_df["Value"] = pd.to_numeric(heart_rate_df["Value"])
    means_heart_rate = heart_rate_df.groupby("Time")["Value"].mean().reset_index()
    print(means_heart_rate[["Time", "Value"]])
    plt.scatter(means_heart_rate["Time"], means_heart_rate["Value"])
    plt.show()


mean_heart_rate_per_day(2.022484408E9)
