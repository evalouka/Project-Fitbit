import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#  Connect
DB_PATH = "fitbit_database.db"
conn = sqlite3.connect(DB_PATH)

#  Load tables

# Get list of tables in the database
hourly_intensity = pd.read_sql("SELECT * FROM hourly_intensity", conn)
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';", conn
)["name"].tolist()

# Function to safely load tables
def load_table(name):
    if name in tables:
        return pd.read_sql(f"SELECT * FROM {name}", conn)
    else:
        return None

# Load tables
daily_activity = load_table("daily_activity")
hourly_steps   = load_table("hourly_steps")

# Clean & parse
df = hourly_intensity.copy()
df.columns = df.columns.str.strip()
df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="mixed")
df["Date"]         = df["ActivityHour"].dt.date
df["Hour"]         = df["ActivityHour"].dt.hour
df["DayOfWeek"]    = df["ActivityHour"].dt.day_name()
df["IsWeekend"]    = df["ActivityHour"].dt.dayofweek >= 5
df["Id"]           = df["Id"].astype(str)

print("Shape:", df.shape)
print("\nMissing values:\n", df.isnull().sum())
print("\nBasic stats:\n", df[["TotalIntensity", "AverageIntensity"]].describe())

#  Stats per individual
def stats_per_individual(dataframe, user_id=None):
    if user_id is not None:
        dataframe = dataframe[dataframe["Id"] == str(user_id)]
    return (dataframe.groupby("Id")[["TotalIntensity", "AverageIntensity"]]
            .agg(["mean", "max", "sum"]).round(2))

print("\nPer-individual summary:")
print(stats_per_individual(df))

#  Stats per date range
def stats_per_date_range(dataframe, start_date=None, end_date=None):
    d = dataframe.copy()
    if start_date: d = d[d["Date"] >= pd.to_datetime(start_date).date()]
    if end_date:   d = d[d["Date"] <= pd.to_datetime(end_date).date()]
    return d.groupby("Date")[["TotalIntensity", "AverageIntensity"]].mean().round(2)

# Stats per hour
def stats_per_hour(dataframe, user_id=None):
    d = dataframe if user_id is None else dataframe[dataframe["Id"] == str(user_id)]
    return d.groupby("Hour")[["TotalIntensity", "AverageIntensity"]].mean().round(2)

#  Plots
plt.style.use("ggplot")   # <-- replaces sns.set_theme(), no install needed
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Fitbit – Hourly Intensity Analysis", fontsize=15, fontweight="bold")

hourly_avg = stats_per_hour(df)
axes[0, 0].plot(hourly_avg.index, hourly_avg["AverageIntensity"], marker="o", color="steelblue")
axes[0, 0].set_title("Avg Intensity by Hour of Day")
axes[0, 0].set_xlabel("Hour"); axes[0, 0].set_ylabel("Average Intensity")
axes[0, 0].set_xticks(range(0, 24))

wk_avg = df.groupby("IsWeekend")["AverageIntensity"].mean()
axes[0, 1].bar(["Weekday", "Weekend"], wk_avg.values, color=["steelblue", "tomato"])
axes[0, 1].set_title("Avg Intensity: Weekday vs Weekend")
axes[0, 1].set_ylabel("Average Intensity")

dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow_avg = df.groupby("DayOfWeek")["AverageIntensity"].mean().reindex(dow_order)
axes[1, 0].bar(dow_avg.index, dow_avg.values, color="mediumseagreen")
axes[1, 0].set_title("Avg Intensity by Day of Week")
axes[1, 0].set_xticks(range(len(dow_order)))
axes[1, 0].set_xticklabels(dow_order, rotation=30, ha="right")
axes[1, 0].set_ylabel("Average Intensity")

top_users = df["Id"].value_counts().head(8).index
df_top = df[df["Id"].isin(top_users)]
df_top.boxplot(column="TotalIntensity", by="Id", ax=axes[1, 1], rot=30)
axes[1, 1].set_title("TotalIntensity Distribution per User")
axes[1, 1].set_xlabel("User Id"); axes[1, 1].set_ylabel("Total Intensity")
plt.suptitle("")

plt.tight_layout()
plt.savefig("intensity_analysis.png", dpi=150)
plt.show()
print("Plot saved as intensity_analysis.png")

#  Steps vs Intensity
if hourly_steps is not None:
    hourly_steps["ActivityHour"] = pd.to_datetime(hourly_steps["ActivityHour"], format="mixed")
    hourly_steps["Id"] = hourly_steps["Id"].astype(str)
    merged = df.merge(hourly_steps, on=["Id", "ActivityHour"], how="inner")
    print("\nCorrelation – Intensity vs Steps:")
    print(merged[["TotalIntensity", "AverageIntensity", "StepTotal"]].corr().round(3))

    fig2, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(merged["StepTotal"], merged["TotalIntensity"], alpha=0.2, s=10, color="purple")
    ax.set_xlabel("Step Total"); ax.set_ylabel("Total Intensity")
    ax.set_title("Steps vs Total Intensity")
    plt.tight_layout()
    plt.savefig("steps_vs_intensity.png", dpi=150)
    plt.show()

#  Daily activity merge
if daily_activity is not None:
    daily_activity["ActivityDate"] = pd.to_datetime(daily_activity["ActivityDate"])
    daily_activity["Id"] = daily_activity["Id"].astype(str)

    daily_intensity = (df.groupby(["Id", "Date"])["TotalIntensity"]
                       .sum().reset_index()
                       .rename(columns={"Date": "ActivityDate", "TotalIntensity": "DailyTotalIntensity"}))
    daily_intensity["ActivityDate"] = pd.to_datetime(daily_intensity["ActivityDate"])

    merged_daily = daily_activity.merge(daily_intensity, on=["Id", "ActivityDate"], how="inner")
    if "TotalMinutesAsleep" in merged_daily.columns:
        corr = merged_daily[["DailyTotalIntensity", "TotalMinutesAsleep"]].corr()
        print("\nCorrelation – Daily Intensity vs Sleep:\n", corr.round(3))