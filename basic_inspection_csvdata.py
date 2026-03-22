import pandas as pd
import plotly.express as px

#df = pd.read_csv("daily_activity.csv")

#Count unique users
#unique_users = df["Id"].nunique()
#print(unique_users)
#print(df.describe())

def plot_total_distance(df):
    total_distance = df.groupby("Id")["TotalDistance"].sum().reset_index()
    total_distance["Id"] = total_distance["Id"].astype(str)

    fig = px.bar(total_distance, x="Id", y="TotalDistance",
                 title="Total Distance per User",
                 labels={"Id": "User Id", "TotalDistance": "Total Distance"},
                 text=total_distance["TotalDistance"].round(1))
    fig.update_traces(textposition="outside")
    fig.update_traces(hovertemplate="User Id: %{x}<br>Total Distance: %{y}<extra></extra>")
    return fig


def plot_activity_time_breakdown(df):
    activity_time_cols = ["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]
    activity_time_df = df.groupby("Id")[activity_time_cols].sum().reset_index()
    activity_time_df["Id"] = activity_time_df["Id"].astype(str)

    fig = px.bar(activity_time_df, x="Id", y=activity_time_cols,
                 barmode="stack",
                 title="Minutes active per User")
    fig.update_yaxes(title_text="Minutes")
    fig.update_xaxes(title_text="User Id")
    return fig


def plot_activity_distance_breakdown(df):
    activity_minute_cols = ["VeryActiveDistance", "ModeratelyActiveDistance", "LightActiveDistance", "SedentaryActiveDistance"]
    activity_minute_df = df.groupby("Id")[activity_minute_cols].sum().reset_index()


    fig = px.bar(activity_minute_df, x="Id", y=activity_minute_cols,
                 barmode="stack",
                 title="Distance breakdown per User")
    fig.update_yaxes(title_text="Distance")
    fig.update_xaxes(title_text="User Id")
    return fig


def plot_ten_k_steps(df):
    unique_users = df["Id"].nunique()
    ten_k_df = df[df["TotalSteps"] >= 10000]
    users_hitting = ten_k_df["Id"].nunique()

    names = ["Users who reached 10k steps", "Users who did not reach the goal"]
    values = [users_hitting, (unique_users - users_hitting)]

    fig = px.pie(names=names, values=values,
                 title="Users Reaching 10,000 Steps (At Least Once)",
                 color_discrete_sequence=["green", "red"])
    fig.update_traces(pull=[0, 0.05])
    return fig


def plot_days_over_10k(df):
    ten_k_df = df[df["TotalSteps"] >= 10000]
    ten_k_counts = ten_k_df.groupby("Id")["TotalSteps"].count().reset_index()
    ten_k_counts.columns = ["Id", "DaysOver10k"]
    ten_k_counts["Id"] = ten_k_counts["Id"].astype(str)

    fig = px.pie(ten_k_counts, names="Id", values="DaysOver10k",
                 title="Days Each User Hit 10k Steps")
    return fig

