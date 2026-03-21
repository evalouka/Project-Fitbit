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
to converted the pounds to kg by using: 1 pound = 0.45359237 kg """


conn = sqlite3.connect("fitbit_database.db")
cursor = conn.cursor()

weight_df = pd.read_sql_query("SELECT * FROM weight_log", conn)


"""To inspect the date the following program was used:
# Inspect the data
print(weight_df.columns)
print(weight_df.head())
print(weight_df.isnull().sum())  # count missing values per column
print(len(weight_df))

# Delete column Fat 
weight_df = weight_df.drop(columns=["Fat"]) 
print(weight_df.isnull().sum())

# Check if null values disappear
weight_df['WeightKg'] = weight_df['WeightKg'].fillna(weight_df['WeightPounds'] * 0.453592)
print(weight_df.isnull().sum())


# Update the database permanently
cursor.execute(" UPDATE weight_log SET WeightKg = WeightPounds * 0.453592 WHERE WeightKg IS NULL")
cursor.execute("ALTER TABLE weight_log DROP COLUMN Fat")
conn.commit()
conn.close()

"""



"""Vizualized the weight and the BMI per day for an unique user"""

def plot_weight_trend(user_id):
    conn = sqlite3.connect("fitbit_database.db")
    
    weight_df = pd.read_sql_query(f"""
        SELECT Date, WeightKg, BMI
        FROM weight_log
        WHERE Id = {float(user_id)}
    """, conn)
    
    conn.close()
    
    # Convert Date to datetime
    weight_df['Date'] = pd.to_datetime(weight_df['Date'], format='%m/%d/%Y %I:%M:%S %p')

    # Plot weight and BMI over time
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_yaxes(title_text="Weight (Kg)", secondary_y=False)
    fig.update_yaxes(title_text="BMI", secondary_y=True)

    fig.add_trace(go.Scatter(x=weight_df['Date'], y=weight_df["WeightKg"],
              mode='lines', name='Weight (Kg)',
              hovertemplate="Date: %{x}<br>Weight: %{y} Kg<extra></extra>"), 
              secondary_y=False)
    fig.add_trace(go.Scatter(x=weight_df["Date"], y=weight_df["BMI"],
              mode='lines', name='BMI',
              hovertemplate="Time: %{x}<br>BMI: %{y}<extra></extra>"), 
              secondary_y=True)
    
    fig.update_layout(title=f"Weight and BMI per day for User: {user_id}")
    
    return fig



def average_bmi(user_id):
    conn = sqlite3.connect("fitbit_database.db")

    bmi_df = pd.read_sql_query("""
        SELECT Id, AVG(BMI) as AvgBMI
        FROM weight_log
        GROUP BY Id
    """, conn)
    
    conn.close()

    group_average = bmi_df["AvgBMI"].mean()
    user_bmi = bmi_df[bmi_df["Id"] == float(user_id)].copy()
    user_bmi["Id"] = user_bmi["Id"].astype(int).astype(str)

    fig = px.bar(user_bmi, x="Id", y="AvgBMI",labels={"x": "User Id", "y": "Average BMI"},
                 title=f"Average BMI: User {user_id} vs Group Average")
    fig.add_hline(y=group_average, line_dash="dash",
                  line_color="red", annotation_text="Group Average")
    
    return fig


