import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

pio.renderers.default = "browser"

"""In this file resolving the missing values of the database are covered.
As 31 out of the 33 values in the column Fat are null, it is decided to remove this column.
In the column WeightKg 2 values were missing. As all values were registered in the column WeightPounds, it was decided
to convert the pounds to kg by using: 1 pound = 0.45359237 kg """


def get_weight_data(user_id):
    conn = sqlite3.connect("fitbit_database.db")
    weight_data = pd.read_sql_query(f"""
        SELECT Date, WeightKg, WeightPounds, BMI
        FROM weight_log
        WHERE Id = {float(user_id)}
    """, conn)
    conn.close()
    return weight_data


def plot_weight_trend(weight_df):
    weight_df = weight_df.copy()
    weight_df['Date'] = pd.to_datetime(weight_df['Date'], format='%m/%d/%Y %I:%M:%S %p')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_yaxes(title_text="Weight (Kg)", secondary_y=False)
    fig.update_yaxes(title_text="BMI", secondary_y=True)

    fig.add_trace(go.Scatter(x=weight_df['Date'], y=weight_df["WeightKg"],
              mode='lines+markers', name='Weight (Kg)',
              hovertemplate="Date: %{x}<br>Weight: %{y} Kg<extra></extra>"),
              secondary_y=False)
    fig.add_trace(go.Scatter(x=weight_df["Date"], y=weight_df["BMI"],
              mode='lines+markers', name='BMI',
              hovertemplate="Date: %{x}<br>BMI: %{y}<extra></extra>"),
              secondary_y=True)

    fig.update_xaxes(
        tickformat="%b %d\n%Y",
        dtick="D1"
    )

    fig.update_layout(title="Weight and BMI over time")
    return fig

def average_bmi(user_id):
    conn = sqlite3.connect("fitbit_database.db")
    bmi_df = pd.read_sql_query("""
        SELECT Id, AVG(BMI) as AvgBMI
        FROM weight_log
        GROUP BY CAST(ROUND(Id) AS INTEGER)
    """, conn)
    conn.close()

    group_average = bmi_df["AvgBMI"].mean()
    bmi_df["Id"] = bmi_df["Id"].astype('int64').astype(str)

    user_bmi = bmi_df[bmi_df["Id"] == str(user_id)].copy()


    fig = px.bar(user_bmi, x="Id", y="AvgBMI",
                 labels={"Id": "User Id", "AvgBMI": "Average BMI"},
                 title=f"Average BMI: User {user_id} vs Group Average")
    fig.update_xaxes(type="category")
    fig.add_hline(y=group_average, line_dash="dash",
                  line_color="red", annotation_text="Group Average")
    return fig


