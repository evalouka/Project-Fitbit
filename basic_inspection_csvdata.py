import pandas as pd
import plotly.express as px

df = pd.read_csv("daily_activity.csv")

#Count unique users
unique_users = df["Id"].nunique()
print(unique_users)
print(df.describe())

#Total distance per user
total_distance = df.groupby("Id")["TotalDistance"].sum()
print(total_distance)

fig = px.bar(x=total_distance.index.astype(str), y=total_distance.values, 
             title="Total Distance per User",
             labels={"x": "User Id", "y": "Total Distance"},
             text=total_distance.values.round(1))
fig.update_traces(textposition="outside")
fig.update_traces(hovertemplate="User Id: %{x}<br>Total Distance: %{y}<extra></extra>")
fig.show()

#CREATIVE PART

#Activity breakdown per user
activity_time_cols = ["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]
activity_time_df = df.groupby("Id")[activity_time_cols].sum().reset_index()
activity_time_df["Id"] = activity_time_df["Id"].astype(str)

activity_time_plot = px.bar(activity_time_df, x="Id", y=activity_time_cols,
             barmode="stack",
             title="Minutes active per User")
activity_time_plot.update_yaxes(title_text="Minutes")
activity_time_plot.update_xaxes(title_text="User Id")
activity_time_plot.show()

activity_minute_cols = ["VeryActiveDistance", "ModeratelyActiveDistance", "LightActiveDistance", "SedentaryActiveDistance"]
activity_minute_df = df.groupby("Id")[activity_minute_cols].sum().reset_index()
activity_minute_df["Id"] = activity_minute_df["Id"].astype(str)

activity_minute_plot = px.bar(activity_minute_df, x="Id", y=activity_minute_cols,
             barmode="stack",
             title="Distance breakdown per User")
activity_minute_plot.update_yaxes(title_text="Distance")
activity_minute_plot.update_xaxes(title_text="User Id")
activity_minute_plot.show()




#How many users are hitting 10k step once
ten_k_df = df[df["TotalSteps"] >= 10000]  
users_hitting = ten_k_df["Id"].nunique()
names = ["Users who reached 10k steps", "Users who did not reach the goal"]
values = [users_hitting,(unique_users-users_hitting)]
pie = px.pie(names=names, values=values, title="Users Reaching 10,000 Steps (At Least Once)", color_discrete_sequence=["green","red"])
pie.update_traces(pull=[0, 0.05])
pie.show()

ten_k_counts = ten_k_df.groupby("Id")["TotalSteps"].count().reset_index()
ten_k_counts.columns = ["Id", "DaysOver10k"]  # rename columns for clarity

pie_chart = px.pie(ten_k_counts, names="Id", values="DaysOver10k",
                   title="Days Each User Hit 10k Steps")
pie_chart.show()
