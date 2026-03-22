"""
Part 3: Heart Rate and Exercise Intensity Analysis

This script provides functions to visualize heart rate and exercise intensity
for individual Fitbit users.

Note: You need to call this function with an ID. Otherwise it does not work!!
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "browser"

connection = sqlite3.connect("fitbit_database.db")
cursor = connection.cursor()
cursor.execute("SELECT DISTINCT Id FROM heart_rate LIMIT 5")
print(cursor.fetchall())

def plot_user_data(user_id):
    # Connect to database
    conn = sqlite3.connect("fitbit_database.db")
    
    # --- Query heart rate ---
    heart_query = f"""
    SELECT Time, Value
    FROM heart_rate
    WHERE Id = {float(user_id)}
    """
    
    heart_df = pd.read_sql_query(heart_query, conn)
    
    # --- Query intensity ---
    intensity_query = f"""
    SELECT ActivityHour, TotalIntensity
    FROM hourly_intensity
    WHERE Id = {float(user_id)}
    """
    
    intensity_df = pd.read_sql_query(intensity_query, conn)
    
    conn.close()
    
    # --- Convert to datetime ---
    heart_df['Time'] = pd.to_datetime(heart_df['Time'], format='%m/%d/%Y %I:%M:%S %p')
    intensity_df['ActivityHour'] = pd.to_datetime(intensity_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p')
    
    # --- Create plot ---
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_yaxes(title_text="Heart Rate (bpm)", secondary_y=False)
    fig.update_yaxes(title_text="Total Intensity", secondary_y=True)

    fig.add_trace(go.Scatter(x=heart_df['Time'], y=heart_df['Value'],
              mode='lines', name='Heart Rate (bpm)',
              hovertemplate="Time: %{x}<br>Heart Rate: %{y} bpm<extra></extra>"), 
              secondary_y=False)
    fig.add_trace(go.Scatter(x=intensity_df['ActivityHour'], y=intensity_df['TotalIntensity'],
              mode='lines', name='Total Intensity',
              hovertemplate="Time: %{x}<br>Intensity: %{y}<extra></extra>"), 
              secondary_y=True)
    
    fig.update_layout(title=f"Heart Rate vs Exercise Intensity for User {user_id}")
    
    return fig
    


def plot_heart_rate_and_intensity(user_id, db_path='fitbit_database.db', date_range=None):
    """
    Create a figure showing heart rate and exercise intensity for a specific user.
    
    Args:
        user_id: The Id of the user to analyze
        db_path: Path to the SQLite database file
        date_range: Optional tuple of (start_date, end_date) as strings 'YYYY-MM-DD'
        
    Returns:
        Matplotlib figure object
    """
    conn = sqlite3.connect(db_path)
    
    # Query heart rate data
    heart_rate_query = f"""
    SELECT Time, Value
    FROM heart_rate
    WHERE Id = {user_id}
    ORDER BY Time
    """
    
    # Query hourly intensity data
    intensity_query = f"""
    SELECT ActivityHour, TotalIntensity, AverageIntensity
    FROM hourly_intensity
    WHERE Id = {user_id}
    ORDER BY ActivityHour
    """
    
    try:
        # Load data
        df_heart = pd.read_sql_query(heart_rate_query, conn)
        df_intensity = pd.read_sql_query(intensity_query, conn)
        
        # Convert time columns to datetime
        df_heart['Time'] = pd.to_datetime(df_heart['Time'])
        df_intensity['ActivityHour'] = pd.to_datetime(df_intensity['ActivityHour'])
        
        # Apply date range filter if specified
        if date_range:
            start_date, end_date = date_range
            df_heart = df_heart[(df_heart['Time'] >= start_date) & 
                               (df_heart['Time'] <= end_date)]
            df_intensity = df_intensity[(df_intensity['ActivityHour'] >= start_date) & 
                                       (df_intensity['ActivityHour'] <= end_date)]
        
        # Create figure with two subplots
        fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
        
        # Plot 1: Heart Rate
        axes[0].plot(df_heart['Time'], df_heart['Value'], 
                    color='#e74c3c', linewidth=0.8, alpha=0.7)
        axes[0].fill_between(df_heart['Time'], df_heart['Value'], 
                            alpha=0.3, color='#e74c3c')
        
        # Add average line
        avg_heart_rate = df_heart['Value'].mean()
        axes[0].axhline(y=avg_heart_rate, color='darkred', linestyle='--', 
                       linewidth=2, label=f'Average: {avg_heart_rate:.1f} bpm')
        
        axes[0].set_ylabel('Heart Rate (bpm)', fontsize=12, fontweight='bold')
        axes[0].set_title(f'Heart Rate and Exercise Intensity - User {user_id}', 
                         fontsize=14, fontweight='bold', pad=20)
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(loc='upper right', fontsize=10)
        
        # Add heart rate zones
        axes[0].axhspan(0, 100, alpha=0.1, color='green', label='Resting')
        axes[0].axhspan(100, 140, alpha=0.1, color='yellow', label='Moderate')
        axes[0].axhspan(140, 200, alpha=0.1, color='red', label='Intense')
        
        # Plot 2: Total Intensity
        axes[1].bar(df_intensity['ActivityHour'], df_intensity['TotalIntensity'],
                   width=0.03, color='#3498db', alpha=0.7, edgecolor='navy')
        
        axes[1].set_xlabel('Time', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Total Intensity', fontsize=12, fontweight='bold')
        axes[1].set_title('Exercise Intensity by Hour', fontsize=13, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # Add average intensity line
        avg_intensity = df_intensity['TotalIntensity'].mean()
        axes[1].axhline(y=avg_intensity, color='darkblue', linestyle='--', 
                       linewidth=2, label=f'Average: {avg_intensity:.1f}')
        axes[1].legend(loc='upper right', fontsize=10)
        
        # Format x-axis
        plt.xticks(rotation=45, ha='right')
        
        # Add statistics text box
        stats_text = f'Heart Rate Stats:\n'
        stats_text += f'  Min: {df_heart["Value"].min():.0f} bpm\n'
        stats_text += f'  Max: {df_heart["Value"].max():.0f} bpm\n'
        stats_text += f'  Avg: {df_heart["Value"].mean():.0f} bpm\n\n'
        stats_text += f'Intensity Stats:\n'
        stats_text += f'  Total Hours: {len(df_intensity)}\n'
        stats_text += f'  Avg Intensity: {df_intensity["TotalIntensity"].mean():.1f}\n'
        stats_text += f'  Peak Intensity: {df_intensity["TotalIntensity"].max():.0f}'
        
        plt.gcf().text(0.02, 0.5, stats_text,
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                      fontsize=9, verticalalignment='center',
                      transform=plt.gcf().transFigure)
        
        plt.tight_layout()
        
        # Save figure
        output_path = f'user_data/outputs/part3_heart_rate_intensity_user_{user_id}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization for User {user_id}")
        
        plt.close()
        
    except Exception as e:
        print(f"Error processing User {user_id}: {str(e)}")
        conn.close()
        return None
    
    conn.close()
    return fig


def analyze_heart_rate_zones(user_id, db_path='fitbit_database.db'):
    """
    Analyze time spent in different heart rate zones.
    
    Args:
        user_id: The Id of the user to analyze
        db_path: Path to the SQLite database file
        
    Returns:
        DataFrame with time spent in each zone
    """
    conn = sqlite3.connect(db_path)
    
    query = f"""
    SELECT Value
    FROM heart_rate
    WHERE Id = {user_id}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Define heart rate zones
    def classify_zone(hr):
        if hr < 100:
            return 'Resting'
        elif hr < 120:
            return 'Light'
        elif hr < 140:
            return 'Moderate'
        elif hr < 160:
            return 'Hard'
        else:
            return 'Maximum'
    
    df['Zone'] = df['Value'].apply(classify_zone)
    
    # Calculate time in each zone (assuming 5-second intervals)
    zone_counts = df['Zone'].value_counts()
    zone_time_minutes = (zone_counts * 5 / 60).round(2)
    
    return zone_time_minutes


def compare_heart_rate_intensity_correlation(user_id, db_path='fitbit_database.db'):
    """
    Analyze correlation between heart rate and exercise intensity.
    
    Args:
        user_id: The Id of the user to analyze
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    
    # Get hourly aggregated heart rate
    hr_query = f"""
    SELECT 
        strftime('%Y-%m-%d %H:00:00', Time) as Hour,
        AVG(Value) as AvgHeartRate
    FROM heart_rate
    WHERE Id = {user_id}
    GROUP BY Hour
    """
    
    # Get intensity data
    intensity_query = f"""
    SELECT 
        ActivityHour as Hour,
        TotalIntensity,
        AverageIntensity
    FROM hourly_intensity
    WHERE Id = {user_id}
    """
    
    df_hr = pd.read_sql_query(hr_query, conn)
    df_intensity = pd.read_sql_query(intensity_query, conn)
    conn.close()
    
    # Merge datasets
    df_merged = pd.merge(df_hr, df_intensity, on='Hour')
    
    # Calculate correlation
    correlation = df_merged['AvgHeartRate'].corr(df_merged['TotalIntensity'])
    
    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(df_merged['TotalIntensity'], df_merged['AvgHeartRate'],
                        alpha=0.6, c=df_merged['AvgHeartRate'], 
                        cmap='coolwarm', s=50)
    
    # Add trend line
    z = np.polyfit(df_merged['TotalIntensity'], df_merged['AvgHeartRate'], 1)
    p = np.poly1d(z)
    ax.plot(df_merged['TotalIntensity'], p(df_merged['TotalIntensity']), 
           "r--", linewidth=2, label=f'Trend line')
    
    ax.set_xlabel('Total Intensity', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Heart Rate (bpm)', fontsize=12, fontweight='bold')
    ax.set_title(f'Heart Rate vs Exercise Intensity - User {user_id}\n' + 
                f'Correlation: {correlation:.3f}', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.colorbar(scatter, ax=ax, label='Heart Rate (bpm)')
    
    plt.tight_layout()
    plt.savefig(f'user_data/outputs/part3_hr_intensity_correlation_user_{user_id}.png',
               dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Correlation analysis saved for User {user_id}")
    print(f"  Correlation coefficient: {correlation:.3f}")
    
    return correlation
