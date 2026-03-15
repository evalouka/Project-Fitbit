import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm
import streamlit as st
import matplotlib.cm as cm
import plotly.express as px

def scatterplot_per_id(df1, df2, Id, choose):
       merged_df = pd.merge(df1, df2, left_on="datetime", right_on="ActivityDate")

       # Set y to dependent variable TotalSteps for regression
       y = merged_df["TotalSteps"]

       if choose == "Precipitation":
              #Compute mean TotalSteps for each precipitation point
              x = "precip"
              xlabel = "Precipitation (mm)"
              title = "Scatterplot of Precipitation vs TotalSteps"

       else:
              x = "temp"
              xlabel = "Temperature (Celsius)"
              title = "Scatterplot of Temperature vs TotalSteps"


       # Make regression model for Precipitation vs TotalSteps
       x_reg = merged_df[x]
       id_dummies = pd.get_dummies(merged_df["Id"], drop_first=True)
       x_reg = pd.concat([x_reg, id_dummies], axis=1)
       x_reg = sm.add_constant(x_reg)
       result = sm.OLS(y, x_reg).fit()

       #Collect the data for given Id
       id_df = merged_df[merged_df["Id"] == Id]


       # Find regression line for Precipitation vs TotalSteps
       base = result.params["const"]
       id_variable = result.params.get(Id, 0.0)
       intercept = base + id_variable
       slope = result.params[x]
       x_line = np.linspace(id_df[x].min(), id_df[x].max(), 100)
       y_line = intercept + slope * x_line

       fig = px.scatter(id_df,
                        x=x,
                        y="TotalSteps",
                        opacity=0.2,
                        color_discrete_sequence=[px.colors.sequential.Blues[2]],
                        title=title)

       fig.add_scatter(x=x_line,
                       y=y_line,
                       mode="lines",
                       line=dict(color=px.colors.sequential.Blues[7]),
                       name="Regression")

       fig.update_layout(height=500,
                         paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)",
                         xaxis_title=xlabel,
                         yaxis_title="Total Steps",
                         font_color="white")

       st.plotly_chart(fig)


def scatterplot_means(df1, df2, choose):
       # Merge the dataframes
       df2["ActivityDate"] = pd.to_datetime(df2["ActivityDate"])
       merged_df = pd.merge(df1, df2, left_on="datetime", right_on="ActivityDate")
       merged_df["Id"] = merged_df["Id"].astype(float)

       # Set y to dependent variable TotalSteps for regression
       y = merged_df["TotalSteps"]


       if choose == "Precipitation":
              #Compute mean TotalSteps for each precipitation point
              x = "precip"
              xlabel = "Precipitation (mm)"
              title = "Scatterplot of Precipitation vs TotalSteps"

       else:
              x = "temp"
              xlabel = "Temperature (Celsius)"
              title = "Scatterplot of Temperature vs TotalSteps"
              # Compute mean TotalSteps for each temperature point

       means = merged_df.groupby(x)["TotalSteps"].mean().reset_index()

       x_reg = merged_df[x]
       x_reg = sm.add_constant(x_reg)
       result = sm.OLS(y,x_reg).fit()

       # Find regression line for Temperature vs TotalSteps
       intercept = result.params["const"]
       slope = result.params[x]
       x_line = np.linspace(merged_df[x].min(), merged_df[x].max(), 100)
       y_line = intercept + slope * x_line

       fig = px.scatter(merged_df,
                        x=x,
                        y= "TotalSteps",
                        opacity= 0.2,
                        color_discrete_sequence=[px.colors.sequential.Blues[2]],
                        title= title)

       fig.add_scatter(x = means[x],
                       y = means["TotalSteps"],
                       mode = "markers",
                       marker= dict(color= px.colors.sequential.Blues[6]),
                       name = "Means")

       fig.add_scatter(x= x_line,
                       y = y_line,
                       mode ="lines",
                       line= dict(color= px.colors.sequential.Blues[7]),
                       name = "Regression")

       fig.update_layout(height = 500,
                         paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)",
                         xaxis_title=xlabel,
                         yaxis_title="Total Steps",
                         font_color="white")

       st.plotly_chart(fig)


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









       # #Create 1x3 grid for three scatterplots
       # fig, ax = plt.subplots(1, 2)
       #
       # #Scatterplot for Precipitation vs TotalSteps
       # ax[0].scatter(id_df["precip"], id_df["TotalSteps"], color="lightskyblue")
       #
       # # Find regression line for Precipitation vs TotalSteps
       # base_precip = result_precip.params["const"]
       # id_variable_precip = result_precip.params.get(Id, 0.0)
       # intercept_precip = base_precip + id_variable_precip
       # slope_precip = result_precip.params["precip"]
       # x_line_precip = np.linspace(id_df["precip"].min(), id_df["precip"].max(), 100)
       # y_line_precip = intercept_precip + slope_precip * x_line_precip
       #
       # #Plot the regression line for Precipitation vs TotalSteps and add title and labels for axes
       # ax[0].plot(x_line_precip, y_line_precip, color = "royalblue")
       # ax[0].set_title("Precipitation vs TotalSteps")
       # ax[0].set_ylabel("Total steps")
       # ax[0].set_xlabel("Precipitation (mm)")
       #
       #
       # #Scatterplot for Temperature vs TotalSteps
       # ax[1].scatter(id_df["temp"], id_df["TotalSteps"], color="lightskyblue")
       #
       # #Make regression model for Temperature vs TotalSteps
       # x_temp = merged_df["temp"]
       # x_temp = pd.concat([x_temp, id_dummies], axis=1)
       # x_temp = sm.add_constant(x_temp)
       # result_temp = sm.OLS(y, x_temp).fit()
       #
       # #Find regression line for Temperature vs TotalSteps
       # base_temp = result_temp.params["const"]
       # id_variable_temp = result_temp.params.get(Id, 0.0)
       # intercept_temp = base_temp + id_variable_temp
       # slope_temp = result_temp.params["temp"]
       # x_line_temp = np.linspace(id_df["temp"].min(), id_df["temp"].max(), 100)
       # y_line_temp = intercept_temp + slope_temp * x_line_temp
       #
       # #Plot regression line for Temperature vs TotalSteps and add title and labels for axes
       # ax[1].plot(x_line_temp, y_line_temp, color = "royalblue")
       # ax[1].set_title("Temperature vs TotalSteps")
       # ax[1].set_ylabel("Total steps")
       # ax[1].set_xlabel("Temperature (Celsius)")
       #
       #
       # plt.tight_layout()
       # plt.show()