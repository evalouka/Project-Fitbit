import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm

#Connect to data base
connection = sqlite3.connect("fitbit_database.db")


def mean_heart_rate_per_day(Id):
    #Creart heart_rate dataframe for the given Id
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate WHERE Id = ?"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate, (float(Id),))
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()

    #Convert the time column to only keep the date and convert value column to numbers
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"]).dt.date
    heart_rate_df["Value"] = pd.to_numeric(heart_rate_df["Value"])

    #Caculate mean heart rate per day
    means_heart_rate = heart_rate_df.groupby("Time")["Value"].mean().reset_index()

    #Plot data
    plt.plot(means_heart_rate["Time"], means_heart_rate["Value"])
    plt.scatter(means_heart_rate["Time"], means_heart_rate["Value"])

    #Add title and labels
    plt.xlabel("Date")
    plt.ylabel("Heart rate")
    plt.title(f"Mean heart rate per day for user {Id}")

    plt.show()

    # Print summary
    print(means_heart_rate["Value"].describe())


def heart_rate_vs_activity(Id):
    #Create heart rate dataframe for given Id
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate WHERE Id = ?"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate, (float(Id),))
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()

    #Compute mean heart rate for each hour of each date
    heart_rate_df["Hour"] = pd.to_datetime(heart_rate_df["Time"]).dt.floor("H")
    means_heart_rate = heart_rate_df.groupby("Hour")["Value"].mean().reset_index()


    #Create activity dataframe for given Id
    query_activity = f"SELECT Id, ActivityHour, StepTotal FROM hourly_steps WHERE Id = ?"
    cursor_activity = connection.cursor()
    cursor_activity.execute(query_activity, (float(Id),))
    rows_activity = cursor_activity.fetchall()
    hourly_activity_df = pd.DataFrame(rows_activity, columns=[x[0] for x in cursor_activity.description]).copy()
    hourly_activity_df["ActivityHour"] = pd.to_datetime(hourly_activity_df["ActivityHour"]).dt.floor("H")

    #Create intensity dataframe for given Id
    query_intensity = f"SELECT Id, ActivityHour, AverageIntensity FROM hourly_intensity WHERE Id = ?"
    cursor_intensity = connection.cursor()
    cursor_intensity.execute(query_intensity, (float(Id),))
    rows_intensity = cursor_intensity.fetchall()
    intensity_df = pd.DataFrame(rows_intensity, columns=[x[0] for x in cursor_intensity.description]).copy()
    intensity_df["ActivityHour"] = pd.to_datetime(intensity_df["ActivityHour"]).dt.floor("H")

    #Merge dataframes
    hourly_activity_df = hourly_activity_df.merge(means_heart_rate, left_on="ActivityHour", right_on="Hour")
    hourly_activity_df = hourly_activity_df.merge(intensity_df, on = ["Id", "ActivityHour"], how = "left")

    #Scatterplot of StepTotal vs Value (heart rate) colored by average intensity
    plt.scatter(hourly_activity_df["StepTotal"], hourly_activity_df["Value"], c=hourly_activity_df["AverageIntensity"], cmap= "Blues")

    #Add labels, title, and colorbar
    plt.xlabel("Step Total")
    plt.ylabel("Heart rate")
    plt.title(f"Step total vs heart rate colored by the average intensity for user {Id}")
    plt.colorbar()
    plt.show()

    #Compute correlation between StepTotal and heart rate
    corr_steps = hourly_activity_df["StepTotal"].corr(hourly_activity_df["Value"])

    #Compute correlation between AverageIntensity and heart rate
    corr_intensity = hourly_activity_df["StepTotal"].corr(hourly_activity_df["AverageIntensity"])

    #Print correlations
    print("Correlation between heart rate and total steps: " + str(corr_steps))
    print("Correlation between heart rate and average intensity " + str(corr_intensity))

    #Print summary
    print(hourly_activity_df[["StepTotal", "Value", "AverageIntensity"]].describe())

def HR_zones(Id):
    #Create heart rate datafarme for given Id
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate WHERE Id = ?"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate, (float(Id),))
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Date"] = pd.to_datetime(heart_rate_df["Time"]).dt.date

    #Compute max heart rate
    max_hr = heart_rate_df["Value"].max()

    #Create bins and labels for HR zones
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    labels = ["Rest", "Very Light", "Light", "Moderate", "Heavy", "Maximum"]

    #Assign a zone to each record for the Id
    heart_rate_df["Zone"] = pd.cut(heart_rate_df["Value"]/max_hr, bins= bins, labels = labels)

    #Calculate how many minutes are spend in each zone
    heart_rate_df["Minutes"] = 5 / 60
    zones_df = heart_rate_df.groupby(["Date", "Zone"])["Minutes"].sum().unstack()
    zones_df.columns = zones_df.columns.astype(str)

    #Convert to percentages
    zones_df["Total Minutes"] = zones_df[labels].sum(axis=1)
    zones_df["Rest"] = zones_df["Rest"] / zones_df["Total Minutes"]
    zones_df["Very Light"] = zones_df["Very Light"] / zones_df["Total Minutes"]
    zones_df["Light"] = zones_df["Light"] / zones_df["Total Minutes"]
    zones_df["Moderate"] = zones_df["Moderate"] / zones_df["Total Minutes"]
    zones_df["Heavy"] = zones_df["Heavy"] / zones_df["Total Minutes"]
    zones_df["Maximum"] = zones_df["Maximum"] / zones_df["Total Minutes"]
    zones_df = zones_df.drop(columns="Total Minutes")

    #Stacked bar chart
    zones_df.plot(kind ="bar", stacked ="True")

    #Add labels and title
    plt.xlabel("Date")
    plt.ylabel("Percentage")
    plt.title(f"Heart rate zone distribution per day for user {Id}")

    plt.show()

    # Print dataframe
    print(zones_df)

    #Print summary
    print(zones_df.describe())


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
    return df_class


def mean_HR_per_group():
    #Get report to know the class of each Id
    report = get_fitbit_report()[["Id", "Class"]].drop_duplicates()

    #Create heart rate dataframe
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate)
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Hour"] = pd.to_datetime(heart_rate_df["Time"], format= "%m/%d/%Y %I:%M:%S %p").dt.hour


    #Calculate mean heart rate per user for each hour of the day
    hourly_mean_HR_per_user = heart_rate_df.groupby(["Id", "Hour"]).mean().reset_index()
    hourly_mean_HR_per_user["Id"] = hourly_mean_HR_per_user["Id"].astype(str)


    #Merge the heart rate dataframe with the report
    hourly_mean_HR_per_user = hourly_mean_HR_per_user.merge(report, on = "Id", how= "inner")


    #Caclulate the hourly mean for each class
    hourly_mean_HR = hourly_mean_HR_per_user.groupby(["Class", "Hour"]).mean().reset_index()

    #Plot the data for each group
    for class_name, group in hourly_mean_HR.groupby("Class"):
        plt.plot(group["Hour"], group["Value"], label = class_name)
        plt.scatter(group["Hour"], group["Value"])


    plt.legend()
    plt.show()

    #Print summary
    print(hourly_mean_HR.groupby("Class")["Value"].describe())



def mean_HR_per_group_compared_to_id(Id):
    #Get report to know the class of each Id
    report = get_fitbit_report()[["Id", "Class"]].drop_duplicates()

    #Create heart rate dataframe
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate)
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Hour"] = pd.to_datetime(heart_rate_df["Time"], format= "%m/%d/%Y %I:%M:%S %p").dt.hour

    #Calculate mean heart rate per user for each hour of the day
    hourly_mean_HR_per_user = heart_rate_df.groupby(["Id", "Hour"]).mean().reset_index()
    hourly_mean_HR_per_user["Id"] = hourly_mean_HR_per_user["Id"].astype(str)

    #Merge the heart rate dataframe with the report
    hourly_mean_HR_per_user = hourly_mean_HR_per_user.merge(report, on = "Id", how= "inner")

    #Caclulate the hourly mean for each class
    hourly_mean_HR = hourly_mean_HR_per_user.groupby(["Class", "Hour"]).mean().reset_index()

    #Plot the data for each group
    for class_name, group in hourly_mean_HR.groupby("Class"):
        plt.plot(group["Hour"], group["Value"], label = class_name, alpha = 0.4)
        plt.scatter(group["Hour"], group["Value"], alpha = 0.4)

    #Compute hourly mean heart rate for the given Id
    id_hr_df = hourly_mean_HR_per_user[hourly_mean_HR_per_user["Id"] == str(Id)]
    id_mean = id_hr_df.groupby("Hour")["Value"].mean().reset_index()

    #Plot data
    plt.plot(id_mean["Hour"], id_mean["Value"], color = "black", label= "Id")
    plt.scatter(id_mean["Hour"], id_mean["Value"], color="black")

    plt.legend()
    plt.show()

    #Print summary
    print(hourly_mean_HR.groupby("Class")["Value"].describe())
    print(f"Summary for user {Id}")
    print(id_mean["Value"].describe())


def HR_zones_per_group():
    #Get report to know the class of each Id
    report = get_fitbit_report()[["Id", "Class"]].drop_duplicates()

    # Create heart rate dataframe
    query_heart_rate = f"SELECT Id, Time, Value FROM heart_rate"
    cursor = connection.cursor()
    cursor.execute(query_heart_rate)
    rows = cursor.fetchall()
    heart_rate_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()
    heart_rate_df["Id"] = heart_rate_df["Id"].astype(str)


    #Merge the heart rate dataframe with the report
    heart_rate_df = heart_rate_df.merge(report, on = "Id", how = "left")


    #Add column Max HR to the dataframe containing the max heart rate
    heart_rate_df["Max HR"] = heart_rate_df.groupby("Id")["Value"].transform("max")

    #Create bins and labels
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    labels = ["Rest", "Very Light", "Light", "Moderate", "Heavy", "Maximum"]

    #Calculate how many minutes are spend in each zone
    heart_rate_df["Zone"] = pd.cut(heart_rate_df["Value"] / heart_rate_df["Max HR"], bins=bins, labels=labels)
    heart_rate_df["Minutes"] = 5 / 60
    zones_df = heart_rate_df.groupby(["Id", "Class", "Zone"])["Minutes"].sum().unstack()
    zones_df.columns = zones_df.columns.astype(str)


    #Convert to percentages
    zones_df["Total Minutes"] = zones_df[labels].sum(axis = 1)
    zones_df["Rest"] = zones_df["Rest"] / zones_df["Total Minutes"]
    zones_df["Very Light"] = zones_df["Very Light"] / zones_df["Total Minutes"]
    zones_df["Light"] = zones_df["Light"] / zones_df["Total Minutes"]
    zones_df["Moderate"] = zones_df["Moderate"] / zones_df["Total Minutes"]
    zones_df["Heavy"] = zones_df["Heavy"] / zones_df["Total Minutes"]
    zones_df["Maximum"] = zones_df["Maximum"] / zones_df["Total Minutes"]

    #Print summary for each zone by class
    print("Summary of time spent in rest zone")
    print(zones_df.groupby("Class")["Rest"].describe().to_string())
    print("\nSummary of time spent in very light zone")
    print(zones_df.groupby("Class")["Very Light"].describe().to_string())
    print("\nSummary of time spent in light zone")
    print(zones_df.groupby("Class")["Light"].describe().to_string())
    print("\nSummary of time spent in moderate zone")
    print(zones_df.groupby("Class")["Moderate"].describe().to_string())
    print("\nSummary of time spent in heavy zone")
    print(zones_df.groupby("Class")["Heavy"].describe().to_string())
    print("\nSummary of time spent in maximum zone")
    print(zones_df.groupby("Class")["Maximum"].describe().to_string())

    #Calculate mean percentage of each class in each zone
    zones_df = zones_df.groupby("Class").mean()

    #Reindex the columns to go from light to heavy
    zones_df = zones_df.reindex(["Light user", "Moderate user", "Heavy user"])

    #Drop column Total Minutes so it is not in the plot
    zones_df = zones_df.drop(columns = "Total Minutes")

    #Stacked bar chart of zones_df
    zones_df.plot(kind = "bar", stacked = True)

    #Add labels and title
    plt.xlabel("Class")
    plt.ylabel("Percentage")
    plt.title("Heart rate zone distribution per class")

    plt.show()

    # Print the dataframe
    print(zones_df)


















HR_zones_per_group()
# mean_HR_per_group()

# mean_HR_per_group_compared_to_id(2.022484408E9)

