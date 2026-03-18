import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

def plot_user_vs_global_calories(Id, con):

    user_query = "SELECT * FROM daily_activity WHERE Id = ?"
    user_df = pd.read_sql_query(user_query, con, params=(Id,))

    global_query = "SELECT ActivityDate, AVG(Calories) as average_calories FROM daily_activity GROUP BY ActivityDate"
    global_df = pd.read_sql_query(global_query, con)

    #con.close()

    if user_df.empty:
        print(f"No data found for ID: {Id}")
        return

    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    user_df = user_df.sort_values('ActivityDate')

    global_df['ActivityDate'] = pd.to_datetime(global_df['ActivityDate'])
    global_df = global_df.sort_values('ActivityDate')

    start_date = user_df['ActivityDate'].min()
    end_date = user_df['ActivityDate'].max()

    fig = px.bar(user_df, x='ActivityDate', y='Calories', 
                 title=f'Calories burned by user {Id} per day'
                 )
    fig.update_traces(marker_color="#2c7da0", name="User Calories", showlegend=True)

    line = px.line(global_df, x='ActivityDate', y='average_calories')
    line_trace = line.data[0]
    line_trace.update(name='Global Average', 
                  line=dict(color="#3C27C6", width=4, dash='dash'))
    
    fig.add_trace(line_trace)

    fig.update_xaxes(range=[start_date, end_date])
    fig.update_layout(height = 400,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Activity Dates",
                      yaxis_title="Calories burned",
                      font_color="white")

    fig.show()

#Id = 4319703577
#con = sqlite3.connect(r"C:\Users\jonge\PycharmProjects\Data Engineering\Project-Fitbit\fitbit_database.db")
#plot_user_vs_global_calories(Id, con)