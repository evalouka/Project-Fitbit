#part 4

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import statsmodels.api as sm

DB_PATH = "fitbit_database.db"


# --- Helper: load hourly calories ---
def get_hourly_calories():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT Id, ActivityHour, Calories FROM hourly_calories", con)
    con.close()
    df['Id'] = df['Id'].astype(int).astype(str)
    df['ActivityHour'] = pd.to_datetime(df['ActivityHour'], format='mixed')
    df['Hour'] = df['ActivityHour'].dt.hour
    df['Date'] = df['ActivityHour'].dt.date
    return df


# --- Helper: load hourly steps ---
def get_hourly_steps():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT Id, ActivityHour, StepTotal FROM hourly_steps", con)
    con.close()
    df['Id'] = df['Id'].astype(int).astype(str)
    df['ActivityHour'] = pd.to_datetime(df['ActivityHour'], format='mixed')
    return df


# --- Helper: load hourly intensity ---
def get_hourly_intensity():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT Id, ActivityHour, AverageIntensity FROM hourly_intensity", con)
    con.close()
    df['Id'] = df['Id'].astype(int).astype(str)
    df['ActivityHour'] = pd.to_datetime(df['ActivityHour'], format='mixed')
    return df


# --- Plot 1: Average calories per hour of day (all users) ---
def plot_calories_by_hour():
    df = get_hourly_calories()
    avg = df.groupby('Hour')['Calories'].mean()

    plt.figure(figsize=(10, 5))
    plt.bar(avg.index, avg.values, color='steelblue', edgecolor='black')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Calories Burned')
    plt.title('Average Calories Burned per Hour of Day (All Users)')
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.show()

    print("Peak hour:", avg.idxmax(), "with avg calories:", round(avg.max(), 2))


# --- Plot 2: Per-individual calorie pattern (dashboard-ready) ---
def plot_calories_for_user(user_id, start_date=None, end_date=None):
    df = get_hourly_calories()
    df_user = df[df['Id'] == str(user_id)].copy()

    if start_date:
        df_user = df_user[df_user['Date'] >= pd.to_datetime(start_date).date()]
    if end_date:
        df_user = df_user[df_user['Date'] <= pd.to_datetime(end_date).date()]

    if df_user.empty:
        print(f"No data found for user {user_id}")
        return

    # Numerical summary
    print(f"\n--- Calorie Summary for User {user_id} ---")
    print(f"Total Calories Burned : {df_user['Calories'].sum()}")
    print(f"Average per Hour      : {df_user['Calories'].mean():.2f}")
    print(f"Max in one Hour       : {df_user['Calories'].max()}")
    print(f"Min in one Hour       : {df_user['Calories'].min()}")

    # Average by hour of day
    avg_by_hour = df_user.groupby('Hour')['Calories'].mean()

    plt.figure(figsize=(10, 5))
    plt.bar(avg_by_hour.index, avg_by_hour.values, color='coral', edgecolor='black')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Calories Burned')
    plt.title(f'Hourly Calorie Pattern for User {user_id}')
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.show()


# --- Plot 3: Steps vs Calories regression (merged tables) ---
def plot_steps_vs_calories():
    df_cal = get_hourly_calories()
    df_steps = get_hourly_steps()

    df = pd.merge(df_cal, df_steps, on=['Id', 'ActivityHour'], how='inner').dropna()
    print(f"\nMerged rows (steps + calories): {len(df)}")

    X = sm.add_constant(df['StepTotal'])
    y = df['Calories']
    model = sm.OLS(y, X).fit()
    print(model.summary())

    slope = model.params['StepTotal']
    intercept = model.params['const']

    plt.figure(figsize=(8, 5))
    plt.scatter(df['StepTotal'], df['Calories'], alpha=0.3, color='steelblue', label='Data')
    x_line = df['StepTotal'].sort_values()
    plt.plot(x_line, slope * x_line + intercept, color='red', linewidth=2,
             label=f'y = {slope:.4f}x + {intercept:.2f}')
    plt.xlabel('Steps per Hour')
    plt.ylabel('Calories Burned per Hour')
    plt.title('Steps vs Calories Burned (Hourly)')
    plt.legend()
    plt.tight_layout()
    plt.show()


# --- Plot 4: Intensity vs Calories regression ---
def plot_intensity_vs_calories():
    df_cal = get_hourly_calories()
    df_int = get_hourly_intensity()

    df = pd.merge(df_cal, df_int, on=['Id', 'ActivityHour'], how='inner').dropna()
    print(f"\nMerged rows (intensity + calories): {len(df)}")

    X = sm.add_constant(df['AverageIntensity'])
    y = df['Calories']
    model = sm.OLS(y, X).fit()
    print(model.summary())

    slope = model.params['AverageIntensity']
    intercept = model.params['const']

    plt.figure(figsize=(8, 5))
    plt.scatter(df['AverageIntensity'], df['Calories'], alpha=0.3, color='purple', label='Data')
    x_line = df['AverageIntensity'].sort_values()
    plt.plot(x_line, slope * x_line + intercept, color='red', linewidth=2,
             label=f'y = {slope:.2f}x + {intercept:.2f}')
    plt.xlabel('Average Intensity')
    plt.ylabel('Calories Burned per Hour')
    plt.title('Exercise Intensity vs Calories Burned (Hourly)')
    plt.legend()
    plt.tight_layout()
    plt.show()


# --- Check available user IDs ---
def print_user_ids():
    df = get_hourly_calories()
    print("\nAvailable user IDs:")
    print(df['Id'].unique())


# --- Run all ---
print_user_ids()  # run this first to see real IDs

plot_calories_by_hour()
plot_calories_for_user("1503960366")
plot_calories_for_user("1503960366", start_date="2016-03-28", end_date="2016-04-10")
plot_steps_vs_calories()
plot_intensity_vs_calories()

