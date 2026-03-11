import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm
import streamlit as st
import matplotlib.cm as cm


def scatterplot_per_id(df1, df2, Id):
       merged_df = pd.merge(df1, df2, left_on="datetime", right_on="ActivityDate")

       # Set y to dependent variable TotalSteps for regression
       y = merged_df["TotalSteps"]

       # Make regression model for Precipitation vs TotalSteps
       x_precip = merged_df["precip"]
       id_dummies = pd.get_dummies(merged_df["Id"], drop_first=True)
       x_precip = pd.concat([x_precip, id_dummies], axis=1)
       x_precip = sm.add_constant(x_precip)
       result_precip = sm.OLS(y, x_precip).fit()

       #Collect the data for given Id
       id_df = merged_df[merged_df["Id"] == Id]

       #Create 1x3 grid for three scatterplots
       fig, ax = plt.subplots(1, 2)

       #Scatterplot for Precipitation vs TotalSteps
       ax[0].scatter(id_df["precip"], id_df["TotalSteps"], color="lightskyblue")

       # Find regression line for Precipitation vs TotalSteps
       base_precip = result_precip.params["const"]
       id_variable_precip = result_precip.params.get(Id, 0.0)
       intercept_precip = base_precip + id_variable_precip
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
       x_temp = merged_df["temp"]
       x_temp = pd.concat([x_temp, id_dummies], axis=1)
       x_temp = sm.add_constant(x_temp)
       result_temp = sm.OLS(y, x_temp).fit()

       #Find regression line for Temperature vs TotalSteps
       base_temp = result_temp.params["const"]
       id_variable_temp = result_temp.params.get(Id, 0.0)
       intercept_temp = base_temp + id_variable_temp
       slope_temp = result_temp.params["temp"]
       x_line_temp = np.linspace(id_df["temp"].min(), id_df["temp"].max(), 100)
       y_line_temp = intercept_temp + slope_temp * x_line_temp

       #Plot regression line for Temperature vs TotalSteps and add title and labels for axes
       ax[1].plot(x_line_temp, y_line_temp, color = "royalblue")
       ax[1].set_title("Temperature vs TotalSteps")
       ax[1].set_ylabel("Total steps")
       ax[1].set_xlabel("Temperature (Celsius)")


       plt.tight_layout()
       plt.show()

def scatterplot_means(df1, df2, choose):
       #Merge the dataframes
       df2["ActivityDate"] = pd.to_datetime(df2["ActivityDate"])
       merged_df = pd.merge(df1, df2, left_on="datetime", right_on="ActivityDate")
       merged_df["Id"] = merged_df["Id"].astype(float)

       # Set y to dependent variable TotalSteps for regression
       y = merged_df["TotalSteps"]

       fig, ax = plt.subplots()

       if choose == "Precipitation":
              #Compute mean TotalSteps for each precipitation point
              means_precip = merged_df.groupby("precip")["TotalSteps"].mean().reset_index()

              #Scatterplot of precipitation vs TotalSteps
              ax.scatter(merged_df["precip"], merged_df["TotalSteps"], color= cm.get_cmap("Blues")(0.2), alpha=0.2, label = "Precipitation vs TotalSteps")

              #Scatterplot of precipitation vs mean TotalSteps
              ax.scatter(means_precip["precip"], means_precip["TotalSteps"], color= cm.get_cmap("Blues")(0.7), alpha = 1, label = "Precipitation vs TotalSteps means")


              # Make regression model for Precipitation vs TotalSteps
              x_precip = merged_df["precip"]
              x_precip = sm.add_constant(x_precip)
              result_precip = sm.OLS(y, x_precip).fit()

              intercept_precip = result_precip.params["const"]
              slope_precip = result_precip.params["precip"]
              x_line_precip = np.linspace(merged_df["precip"].min(), merged_df["precip"].max(), 100)
              y_line_precip = intercept_precip + slope_precip * x_line_precip

              #Add labels, title, and legend
              ax.tick_params(axis ="x", rotation = 90)
              ax.plot(x_line_precip, y_line_precip, color= cm.get_cmap("Blues")(0.9))
              ax.set_xlabel("Precipitation (mm)")
              ax.set_ylabel("Total Steps")
              ax.set_title("Scatterplot of Precipitation vs TotalSteps")
              ax.legend()

       else:
              # Compute mean TotalSteps for each temperature point
              means_temp = merged_df.groupby("temp")["TotalSteps"].mean().reset_index()

              # Scatterplot of temperature vs TotalSteps
              ax.scatter(merged_df["temp"], merged_df["TotalSteps"], color= cm.get_cmap("Blues")(0.2), alpha = 0.2, label = "Temperature vs TotalSteps")

              # Scatterplot of temperature vs mean TotalSteps
              ax.scatter(means_temp["temp"], means_temp["TotalSteps"], color= cm.get_cmap("Blues")(0.7), alpha = 1, label = "Temperature vs TotalSteps means")

              x_temp = merged_df["temp"]
              x_temp = sm.add_constant(x_temp)
              result_temp = sm.OLS(y, x_temp).fit()

              # Find regression line for Temperature vs TotalSteps
              intercept_temp = result_temp.params["const"]
              slope_temp = result_temp.params["temp"]
              x_line_temp = np.linspace(merged_df["temp"].min(), merged_df["temp"].max(), 100)
              y_line_temp = intercept_temp + slope_temp * x_line_temp

              # Add labels, title, and legend
              ax.tick_params(axis = "x", rotation=90)
              ax.plot(x_line_temp, y_line_temp, color= cm.get_cmap("Blues")(0.9))
              ax.set_xlabel("Temperature (Celsius)")
              ax.set_ylabel("Total Steps")
              ax.set_title("Scatterplot of Temperature vs TotalSteps")
              ax.legend()

       ax.set_frame_on(False)
       fig.patch.set_alpha(0)
       fig.tight_layout()
       ax.xaxis.label.set_color("white")
       ax.tick_params(colors="white")
       ax.yaxis.label.set_color("white")
       ax.title.set_color("white")
       st.pyplot(fig)



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

# unique_id = daily_activity_df["Id"].drop_duplicates()
# for value in unique_id.head(3):
#        scatterplot_per_id(weather, daily_activity_df, value)



#
# barplot_activity_temperature_and_precip()








