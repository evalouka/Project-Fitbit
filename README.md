## Fitbit Data Analysis Dashboard

A data analysis project that explores Fitbit usage data collected from 35 participants in 2016. The project covers statistical analysis, data visualization, database querying, and an interactive dashboard built with Streamlit.



## Project Overview

This project was developed as part of a university assignment. Using real-world Fitbit data, we investigate the activity, sleep, and health patterns of survey participants. The final product is an interactive dashboard aimed at business analysts and the study participants themselves.

The project is divided into 5 parts:

- Part 1 – Exploratory data analysis on daily activity data
- Part 2 – GitHub version control setup and collaboration
- Part 3 – Database querying and multi-table analysis
- Part 4 – Data wrangling, merging, and aggregation
- Part 5 – Interactive Streamlit dashboard

## Project Structure

Project-Fitbit/
│
├── main.py                          # Streamlit dashboard entry point
│
├── # --- Analysis Modules ---
├── activity_logs.py                 # Activity log processing
├── basic_inspection_csvdata.py      # Basic data inspection and visualizations
├── calories.py                      # Calorie data analysis
├── calories_regression.py           # Calorie regression modeling
├── heart_rate.py                    # Heart rate data processing
├── intensity.py                     # Intensity metrics
├── minutes_distribution.py          # Activity minutes distribution
├── normality check.py               # Normality check for regression model errors
├── sleep.py                         # Sleep data processing
├── sleep_activity.py                # Sleep & activity correlation
├── step.py                          # Step count analysis and sleep & sedentary regression
├── user_classification.py           # User segmentation/classification
├── weather.py                       # Weather data integration
├── weight.py                        # Weight and BMI analysis
│
├── # --- Data ---
├── fitbit_database.db               # Main SQLite database
├── daily_activity.csv               # Daily activity CSV file
│
├── # --- Configuration ---
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
│
├── user_data/
│   └── outputs/
│       ├── part3_user_classification_complete.png
│       ├── user_classification_db.csv
│       └── user_stats_by_class.csv
│
└── weather_data/
    └── chicago_weather_march_april.csv




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



| Package     | Version | Purpose                                      |
|-------------|---------|----------------------------------------------|
| matplotlib  | 3.3.4   | Plotting and data visualization              |
| numpy       | 1.23.5  | Numerical computations                       |
| pandas      | 1.5.3   | Data manipulation and analysis               |
| plotly      | 6.6.0   | Interactive charts                           |
| scipy       | 1.6.2   | Statistical analysis and regression          |
| statsmodels | 0.12.2  | Advanced statistical modeling                |
| streamlit   | 1.40.1  | Web app / dashboard interface                |
| jinja2      | 3.1.6   | Table styling and formatted output           |
| Python      | 3.8.8   | Programming language used to run the project |


---

## How to Run

# 1. Clone the repository
git clone <your-repo-url>

# 2. Navigate to the project folder
cd Project-Fitbit

# 3. Create a conda environment
conda create -n fitbit_env python=3.8.8

# 4. Activate it
conda activate fitbit_env

# 5. Install all dependencies
pip install -r requirements.txt

# 6. Run the dashboard
streamlit run main.py

> Make sure fitbit_database.db is in the root project folder before running.

---

## Project Parts

### Part 1 – Exploratory Data Analysis
Explores daily_activity data from the Fitbit database, including:
- Unique user count and total distance per user
- Activity time and distance breakdown per user
- Visualization of reaching 10k steps per day
- Calories burned per day per user (with date range filtering)
- Workout frequency by day of the week
- OLS regression: Calories ~ TotalSteps + Id
- Per-user regression visualization
- Distribution of activity minutes per user

### Part 3 – Database Analysis
Connects to fitbit_database.db via sqlite3 and includes:
- Sleep duration analysis per user
- Regression: active minutes vs sleep duration
- Regression: sedentary activity vs sleep duration (with normality checks)
- Activity broken into 4-hour time blocks (steps, calories, sleep)
- Heart rate and exercise intensity visualization per user
- Weather data integration and activity correlation
- Intensity analysis


### Part 4 – Data Wrangling
Focuses on cleaning and preparing data for the dashboard:
- Handling missing values in the weight_log table
- Visualization of weight and BMI per user
- Merging tables and grouping by individual user
- Aggregating data by user, date range, and time of day
- Preparing summaries for the dashboard

### Part 5 – Dashboard
An interactive Streamlit dashboard with:
- Home page — general statistics and visual summaries of the dataset
- Individual page — select a user ID from the sidebar to view personal stats
- Time filter — filter data by date range or time of day
- Sleep analysis — explore variables that affect sleep duration

---

## Contributors

| Name |  
|------|
| Rojin Naseh | 
| Naomi van Diermen |
| Eva Quist | 
| Aimee de Jonge | 

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
- The dataset covers activity from 35 Fitbit users over several weeks in 2016.
