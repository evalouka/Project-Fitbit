# 🏃 Fitbit Data Analysis Dashboard

A data analysis project that explores Fitbit usage data collected from 33 participants in 2016. The project covers statistical analysis, data visualization, database querying, and an interactive dashboard built with Streamlit.

---

## 📌 Project Overview

This project was developed as part of a university assignment. Using real-world Fitbit data, we investigate the activity, sleep, and health patterns of survey participants. The final product is an interactive dashboard aimed at business analysts and the study participants themselves.

The project is divided into 5 parts:

- **Part 1** – Exploratory data analysis on daily activity data
- **Part 2** – GitHub version control setup and collaboration
- **Part 3** – Database querying and multi-table analysis
- **Part 4** – Data wrangling, merging, and aggregation
- **Part 5** – Interactive Streamlit dashboard

---

## 📁 Project Structure
```
Project-Fitbit/
│
├── data/
│   ├── daily_activity.csv          # Daily activity per user
│   └── fitbit_database.db          # SQLite database with all Fitbit tables
│
├── part1/                          # Exploratory analysis scripts
├── part3/                          # Database analysis scripts
├── part4/                          # Data wrangling scripts
├── part5/                          # Streamlit dashboard
│
└── README.md                       # You are here
```

---

## 🗄️ Dataset

The data comes from 33 Fitbit users who submitted usage data via an Amazon survey in 2016. The SQLite database contains the following tables:

| Table | Description |
|---|---|
| `daily_activity` | Daily steps, calories, and active minutes per user |
| `heartrate` | Heart rate measured every 5 seconds |
| `hourly_calories` | Calories burnt per hour |
| `hourly_intensity` | Exercise intensity per hour |
| `hourly_steps` | Steps taken per hour |
| `minute_sleep` | Sleep data recorded per minute |
| `weightlog` | Weight, fat percentage, and BMI per user |

---

## 📦 Requirements

Make sure you have **Python 3** installed. Then install the required libraries:
```bash
pip install pandas numpy plotly scipy statsmodels streamlit sqlite3
```

> `sqlite3` comes built-in with Python — no separate installation needed.

---

## 🚀 How to Run

### Run the Dashboard (Part 5)
```bash
streamlit run part5/dashboard.py
```

---

## 📊 Part 1 – Exploratory Data Analysis

This part explores `daily_activity.csv` and includes:

- Count of unique users and total distance per user
- Calories burnt per day per user (with date range filtering)
- Workout frequency by day of the week
- OLS regression: `Calories ~ TotalSteps + Id`
- Regression visualization per user

---

## 🗃️ Part 3 – Database Analysis

This part connects to `fitbit_database.db` using `sqlite3` and includes:

- Sleep duration analysis per user
- Regression: active minutes vs sleep duration
- Regression: sedentary activity vs sleep duration (with normality checks)
- Activity broken into 4-hour time blocks (steps, calories, sleep)
- Heart rate and exercise intensity visualization per user
- Weather data integration and activity correlation

---

## 🔧 Part 4 – Data Wrangling

This part focuses on cleaning and merging data:

- Handling missing values in the `weightlog` table
- Merging tables and grouping by individual
- Aggregating data by user, date range, and time of day
- Preparing summaries for the dashboard

---

## 📈 Part 5 – Dashboard

The Streamlit dashboard includes:

- **Home page** — general statistics and visual summaries of the dataset
- **Individual page** — select a user ID from the sidebar to view personal statistics
- **Time filter** — filter data by date range or time of day
- **Sleep analysis** — explore what variables affect sleep duration

---

## 👥 Contributors

| Name | Contribution |
|---|---|
| Rojin Naseh | |
| Naomi van Diermen | |
| Eva Quist | |
| Aimee de Jonge | |

---

## 🛠️ Tools & Technologies

- **Python 3** — core language
- **pandas & numpy** — data manipulation
- **plotly & scipy** — visualizations and statistics
- **statsmodels** — OLS regression
- **sqlite3** — database access
- **Streamlit** — interactive dashboard
- **PyCharm** — development environment
- **GitHub** — version control and collaboration
- **Visual Studio Code** — development environment

---

## 📝 Notes

- All scripts assume `fitbit_database.db` is available locally. Adjust the path in each script if needed.
- The dataset covers activity from **33 Fitbit users** over several weeks in **2016**.
- This README will be updated continuously as the project develops..

