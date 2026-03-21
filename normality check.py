""" This file contains graphs to visually verify the model assumption that the errors of
the linear regression model of Sleep vs SedentaryMinutes are normally distributed

 Note: This file needs to be run independently of the dashboard
 """

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go

conn = sqlite3.connect("fitbit_database.db")
sleep_df = pd.read_sql_query("SELECT Id, date, logId FROM minute_sleep", conn)
activity_df = pd.read_sql_query("SELECT Id, ActivityDate, SedentaryMinutes FROM daily_activity", conn)
conn.close()

sleep_df["sleep_date"] = pd.to_datetime(sleep_df["date"]).dt.date
activity_df["activity_date"] = pd.to_datetime(activity_df["ActivityDate"]).dt.date

daily_sleep = sleep_df.groupby(["Id", "sleep_date"], as_index=False).size().rename(columns={"size": "sleep_minutes"})
merged = pd.merge(daily_sleep, activity_df[["Id", "activity_date", "SedentaryMinutes"]], left_on=["Id", "sleep_date"], right_on=["Id", "activity_date"], how="inner").dropna()

x = merged["SedentaryMinutes"].values.astype(float)
y = merged["sleep_minutes"].values.astype(float)
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
y_pred = slope * x + intercept
residuals = y - y_pred

print(f"Matched rows: {len(merged)}")
print(f"Slope:     {slope:.4f}")
print(f"Intercept: {intercept:.4f}")
print(f"R²:        {r_value**2:.4f}")
print(f"P-value:   {p_value:.4e}")

# Plot 1: Scatter + Regression Line
x_line = np.linspace(x.min(), x.max(), 200)
y_line = slope * x_line + intercept

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=x, y=y, mode="markers", marker=dict(color="steelblue", opacity=0.5, size=6), name="Data"))
fig1.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", line=dict(color="crimson", width=2), name=f"Fit (R²={r_value**2:.3f})"))
fig1.update_layout(title="Sedentary Minutes vs Sleep Duration", xaxis_title="Sedentary Minutes", yaxis_title="Sleep Duration (minutes)", template="plotly_white")
fig1.show()

# Plot 2: Residuals vs Fitted
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=y_pred, y=residuals, mode="markers", marker=dict(color="darkorange", opacity=0.5, size=6)))
fig2.add_hline(y=0, line=dict(color="black", dash="dash"))
fig2.update_layout(title="Residuals vs Fitted Values", xaxis_title="Fitted Values", yaxis_title="Residuals", template="plotly_white")
fig2.show()

# Plot 3: Histogram of Residuals
fig3 = go.Figure()
fig3.add_trace(go.Histogram(x=residuals, nbinsx=40, marker_color="mediumseagreen", opacity=0.75))
fig3.update_layout(title="Histogram of Residuals", xaxis_title="Residuals", yaxis_title="Frequency", template="plotly_white")
fig3.show()

# Plot 4: Q-Q Plot
(osm, osr), (slope_qq, intercept_qq, r_qq) = stats.probplot(residuals)
qq_line_x = np.array([osm.min(), osm.max()])
qq_line_y = slope_qq * qq_line_x + intercept_qq

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=osm, y=osr, mode="markers", marker=dict(color="mediumpurple", opacity=0.6, size=6), name="Q-Q"))
fig4.add_trace(go.Scatter(x=qq_line_x, y=qq_line_y, mode="lines", line=dict(color="crimson", width=2), name="Normal line"))
fig4.update_layout(title="Q-Q Plot of Residuals", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", template="plotly_white")
fig4.show()