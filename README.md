Fitbit Data Analysis Dashboard

A data analysis project that explores Fitbit usage data collected from 35 participants in 2016. The project covers statistical analysis, data visualization, database querying, and an interactive dashboard built with Streamlit.



## Project Overview

This project was developed as part of a university assignment. Using real-world Fitbit data, we investigate the activity, sleep, and health patterns of survey participants. The final product is an interactive dashboard aimed at business analysts and the study participants themselves.

The project is divided into 5 parts:

- *Part 1* – Exploratory data analysis on daily activity data
- *Part 2* – GitHub version control setup and collaboration
- *Part 3* – Database querying and multi-table analysis
- *Part 4* – Data wrangling, merging, and aggregation
- *Part 5* – Interactive Streamlit dashboard
![img.png](img.png)

## Project Structure

Project-Fitbit/
│
├── main.py                          # Entry point of the application
│
├── # --- Analysis Modules ---
├── activity_logs.py                 # Activity log processing
├── calories.py                      # Calorie data analysis
├── calories_regression.py           # Calorie regression modeling
├── heart_rate.py                    # Heart rate data processing
├── heart_rate_vs_exercise_intensity.py  # Heart rate vs. intensity analysis
├── intensity.py                     # Intensity metrics
├── minutes_distribution.py          # Activity minutes distribution
├── sleep.py                         # Sleep data processing
├── sleep_activity.py                # Sleep & activity correlation
├── step.py                          # Step count analysis

├── user_classification.py           # User segmentation/classification
├── weather.py                       # Weather data integration
│
├── # --- Visualizations (Generated) ---
├── calories_by_block.png
├── calories_regression.png  (residuals_histogram, qq_plot, sedentary_sleep_regression)
├── intensity_analysis.png   (plot1–plot5, steps_vs_intensity, etc.)
├── sleep_by_block.png
├── steps_by_block.png
│
├── fitbit_database.db               # Main SQLite database
├── README.md
│
├── user_data/
│   └── outputs/
│       ├── part3_user_classification_complete.png
│       ├── user_classification_db.csv
│       └── user_stats_by_class.csv
│
├── weather_data/
│   └── Chicago_weather_march_april.csv




## Dataset

This project uses two data sources:

### 1. Fitbit Database (fitbit_database.db)
A SQLite database containing fitness tracking data from multiple users. It includes the following tables:

| Table | Description |
|-------|-------------|
| daily_activity | Daily activity summary (steps, distance, active minutes, sedentary time) |
| heart_rate | Heart rate measurements over time |
| hourly_calories | Calories burned per hour |
| hourly_intensity | Exercise intensity levels per hour |
| hourly_steps | Step count per hour |
| minute_sleep | Sleep tracking data per minute |
| weight_log | User weight log entries |

### 2. Weather Data (weather_data/Chicago_weather_march_april.csv)
Daily weather data for Chicago covering March–April 2016, containing 33 features including temperature, humidity, precipitation, wind speed, UV index, and general conditions.


---

##  Requirements


Install all dependencies with:
bash
pip install -r requirements.txt


| Package | Version | Purpose |
|------------|---------|---------|
| matplotlib | 3.10.8 | Plotting and data visualization |
| numpy | 2.4.3 | Numerical computations |
| pandas | 3.0.1 | Data manipulation and analysis |
| plotly | 6.6.0 | Interactive charts |
| scipy | 1.17.1 | Statistical analysis and regression |
| statsmodels | 0.14.6 | Advanced statistical modeling |
| streamlit | 1.55.0 | Web app / dashboard interface |

---

## How to Run

### 1. Install dependencies
bash
pip install -r requirements.txt


### 2. Run the Dashboard
bash
streamlit run dashboard.py

> Make sure fitbit_database.db is in the root project folder before running.

---

## Project Parts

### Part 1 – Exploratory Data Analysis
Explores daily_activity data from the Fitbit database, including:
- Unique user count and total distance per user
- Calories burned per day per user (with date range filtering)
- Workout frequency by day of the week
- OLS regression: Calories ~ TotalSteps + Id
- Per-user regression visualization

### Part 3 – Database Analysis
Connects to fitbit_database.db via sqlite3 and includes:
- Sleep duration analysis per user
- Regression: active minutes vs sleep duration
- Regression: sedentary activity vs sleep duration (with normality checks)
- Activity broken into 4-hour time blocks (steps, calories, sleep)
- Heart rate and exercise intensity visualization per user
- Weather data integration and activity correlation

### Part 4 – Data Wrangling
Focuses on cleaning and preparing data for the dashboard:
- Handling missing values in the weight_log table
- Merging tables and grouping by individual user
- Aggregating data by user, date range, and time of day
- Preparing summaries for the dashboard

### Part 5 – Dashboard
An interactive Streamlit dashboard with:
- *Home page* — general statistics and visual summaries of the dataset
- *Individual page* — select a user ID from the sidebar to view personal stats
- *Time filter* — filter data by date range or time of day
- *Sleep analysis* — explore variables that affect sleep duration

---

## Contributors

| Name | Role |
|------|------|
| Rojin Naseh | |
| Naomi van Diermen | |
| Eva Quist | |
| Aimee de Jonge | |

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| Python 3 | Core language |
| pandas & numpy | Data manipulation |
| plotly & matplotlib | Visualizations |
| scipy & statsmodels | Statistics and OLS regression |
| sqlite3 | Database access |
| Streamlit | Interactive dashboard |
| GitHub | Version control and collaboration |

---

## Notes
- All scripts assume fitbit_database.db is in the root project folder. Adjust the path if needed.
- The dataset covers activity from *33 Fitbit users* over several weeks in *2016*.
- This README will be updated continuously as the project develops.