import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm

#Connect to data base
connection = sqlite3.connect("fitbit_database.db")

#Read data
full_weather_data = pd.read_csv("weather_data/chicago_weather_march_april.csv")

#Create weather dataframe with all needed data
weather = full_weather_data[["datetime", "temp", "precip",]].copy()

#Convert the datetime column to date objects
weather["datetime"] = pd.to_datetime(weather["datetime"])

#Create daily activity dataframe with needed data from daily_activity
query = f"SELECT Id, ActivityDate, TotalSteps FROM daily_activity"
cursor = connection.cursor()
cursor.execute(query)
rows = cursor.fetchall()
daily_activity_df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description]).copy()

#Convert the ActivityDate column to date objects
daily_activity_df["ActivityDate"] = pd.to_datetime(daily_activity_df["ActivityDate"])

#Merge the weather and activity dataframe based on date
merged_df = pd.merge(weather, daily_activity_df, left_on="datetime", right_on="ActivityDate")


def scatterplot_per_id(Id):
       #Collect the data for given Id
       id_df = merged_df[merged_df["Id"] == Id]

       #Create 1x3 grid for three scatterplots
       fig, ax = plt.subplots(1, 3)

       #Scatterplot for Precipitation vs TotalSteps
       ax[0].scatter(id_df["precip"], id_df["TotalSteps"], color="lightskyblue")

       #Set y to dependent variable TotalSteps for regression
       y = id_df["TotalSteps"]

       #Make regression model for Precipitation vs TotalSteps
       x_precip = id_df["precip"]
       x_precip = sm.add_constant(x_precip)
       result_precip = sm.OLS(y, x_precip).fit()

       #Print summary
       print(result_precip.summary())

       #Find regression line for Precipitation vs TotalSteps
       intercept_precip = result_precip.params["const"]
       slope_precip = result_precip.params["precip"]
       x_line_precip = np.linspace(id_df["precip"].min(), id_df["precip"].max(), 100)
       y_line_precip = intercept_precip + slope_precip * x_line_precip

       #Plot the regression line for Precipitation vs TotalSteps and add title and labels for axes
       ax[0].plot(x_line_precip, y_line_precip, color = "royalblue")
       ax[0].set_title("Precipitation vs TotalSteps")
       ax[0].set_ylabel("Total steps")
       ax[0].set_xlabel("Precipitation (mm)")


       #Scatterplot for Temperature vs TotalSteps
       ax[1].scatter(id_df["temp"], id_df["TotalSteps"], color="lightskyblue")

       #Make regression model for Temperature vs TotalSteps
       x_temp = id_df["temp"]
       x_temp = sm.add_constant(x_temp)
       result_temp = sm.OLS(y, x_temp).fit()

       #Print summary
       print(result_temp.summary())

       #Find regression line for Temperature vs TotalSteps
       intercept_temp = result_temp.params["const"]
       slope_temp = result_temp.params["temp"]
       x_line_temp = np.linspace(id_df["temp"].min(), id_df["temp"].max(), 100)
       y_line_temp = intercept_temp + slope_temp * x_line_temp

       #Plot regression line for Temperature vs TotalSteps and add title and labels for axes
       ax[1].plot(x_line_temp, y_line_temp, color = "royalblue")
       ax[1].set_title("Temperature vs TotalSteps")
       ax[1].set_ylabel("Total steps")
       ax[1].set_xlabel("Temperature (Celsius)")

       #Scatterplot for Precipitation vs Temperature
       ax[2].scatter(id_df["temp"], id_df["precip"], color="lightskyblue")

       #Make precip dependent variable y
       y_precip = id_df["precip"]

       #Make regression model for Precipitation vs Temperature
       result = sm.OLS(y_precip, x_temp).fit()

       #Print summary
       print(result.summary())

       #Find regression line for Precipitation vs Temperature
       intercept = result.params["const"]
       slope = result.params["temp"]
       y_line = intercept + slope * x_line_temp

       #Plot regression line for Precipitation vs Temperature and add title and labels for axes
       ax[2].plot(x_line_temp, y_line, color = "royalblue")
       ax[2].set_title("Precip vs Temperature")
       ax[2].set_ylabel("Precipitation (mm)")
       ax[2].set_xlabel("Temperature (Celsius)")

       plt.tight_layout()
       plt.show()

def scatterplot_means():
       #Compute mean TotalSteps for each precipitation point
       means_precip = merged_df.groupby("precip")["TotalSteps"].mean().reset_index()

       #Scatterplot of precipitation vs TotalSteps
       plt.scatter(merged_df["precip"], merged_df["TotalSteps"], color="lightgrey", alpha=0.3, label = "Precipitation vs TotalSteps")

       #Scatterplot of precipitation vs mean TotalSteps
       plt.scatter(means_precip["precip"], means_precip["TotalSteps"], color = "royalblue", alpha = 1, label = "Precipitation vs TotalSteps means")

       #Add labels, title, and legend
       plt.xticks(rotation = 90)
       plt.xlabel("bins (mm)")
       plt.ylabel("Total Steps")
       plt.title("Scatterplot of Precipitation vs TotalSteps")
       plt.legend()
       plt.show()

       # Compute mean TotalSteps for each temperature point
       means_temp = merged_df.groupby("temp")["TotalSteps"].mean().reset_index()

       # Scatterplot of temperature vs TotalSteps
       plt.scatter(merged_df["temp"], merged_df["TotalSteps"], color = "lightgrey", alpha = 0.3, label = "Temperature vs TotalSteps")

       # Scatterplot of temperature vs mean TotalSteps
       plt.scatter(means_temp["temp"], means_temp["TotalSteps"], color = "royalblue", alpha = 1, label = "Temperature vs TotalSteps means")

       # Add labels, title, and legend
       plt.xticks(rotation=90)
       plt.xlabel("Temperature (Celsius)")
       plt.ylabel("Total Steps")
       plt.title("Scatterplot of Temperature vs TotalSteps")
       plt.legend()
       plt.show()

def barplot_activity_temperature_and_precip():
       #Make temperature bins and add them to the merged dataframe
       bins_temp = np.linspace(-2, 16, 10)
       merged_df["Temp_bin"] = pd.cut(merged_df["temp"], bins= bins_temp)

       #Compute mean TotalSteps per bin
       means_temp = merged_df.groupby("Temp_bin")["TotalSteps"].mean()

       #Plot bins and means
       plt.bar(means_temp.index.astype(str), means_temp.values)

       #Add labels and title
       plt.xlabel("Bins (Celsius)")
       plt.ylabel("TotalSteps")
       plt.title("Mean TotalSteps per temperature bin")
       plt.tight_layout()
       plt.xticks(rotation = 45)
       plt.show()

       # Make precipitation bins and add them to the merged dataframe
       bins_precip = np.linspace(0, 28, 8)
       merged_df["precip_bin"] = pd.cut(merged_df["precip"], bins=bins_precip)

       # Compute mean TotalSteps per bin
       means_precip = merged_df.groupby("precip_bin")["TotalSteps"].mean()

       # Plot bins and means
       plt.bar(means_precip.index.astype(str), means_precip.values)

       # Add labels and title
       plt.xlabel("Bins (mm)")
       plt.ylabel("TotalSteps")
       plt.title("Mean TotalSteps per precipitation bin")
       plt.tight_layout()
       plt.xticks(rotation=90)
       plt.show()

unique_id = daily_activity_df["Id"].drop_duplicates()
for value in unique_id.head(2):
       scatterplot_per_id(value)

scatterplot_means()

barplot_activity_temperature_and_precip()








