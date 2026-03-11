import pandas as pd
import statsmodels.api as sm
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from sympy.physics.units import minutes

def regression_calories(df, Id):
    # Store calories in dependent variably y
    y = df["Calories"]

    # Store calories in independent variably x
    x = df[["TotalSteps"]]

    # Add dummy columns to account for ID factor
    id_dummies = pd.get_dummies(df["Id"], drop_first=True)
    x = pd.concat([x, id_dummies], axis=1)

    # Add constants to ensure an intercept
    x = sm.add_constant(x)

    # Fit the model
    model = sm.OLS(y, x)
    results = model.fit()

    # Find data belonging to the given ID and make a scatterplot
    df_id = df[df["Id"] == Id]

    if df_id.empty:
        st.write("No calories data available")
        return

    fig, ax = plt.subplots(figsize=(5,4))
    ax.scatter(df_id["TotalSteps"], df_id["Calories"], color= cm.get_cmap("Blues")(0.35))

    #Copmute base intercept and the id variable to calculate the intercept for a given ID
    base = results.params["const"]
    id_variable = results.params.get(Id,0.0)
    intercept = base + id_variable

    #Compute the slope of the regression line
    slope = results.params["TotalSteps"]

    #Plot the regression line
    x_line = np.linspace(df_id["TotalSteps"].min(),df_id["TotalSteps"].max(),100)
    y_line = intercept + slope*x_line

    ax.set_xlabel("Total steps")
    ax.set_ylabel("Calories")
    ax.set_title(f"Calories burned vs total steps taken for user {Id}")
    ax.plot(x_line, y_line,  color= cm.get_cmap("Blues")(0.8))
    ax.xaxis.label.set_color("white")
    ax.tick_params(colors= "white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    ax.set_frame_on(False)
    fig.patch.set_alpha(0)
    st.pyplot(fig)
