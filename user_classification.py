"""
Part 3: User Classification (Database Version)
File: part3_user_classification_db.py

This script classifies Fitbit users using SQL queries on fitbit_database.db:
- Light user: 10 or fewer days of activity
- Moderate user: 11-15 days of activity  
- Heavy user: 16 or more days of activity
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import sqlite3

def classify_users(db_path='fitbit_database.db'):
    """
    Classify users based on activity frequency using SQL query.
    
    Classification is done entirely in SQL for efficiency:
    - Light: ≤ 10 days
    - Moderate: 11-15 days
    - Heavy: ≥ 16 days
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        DataFrame with columns 'Id' and 'Class'
    """
    conn = sqlite3.connect(db_path)
    
    # SQL query that counts and classifies in one step
    query = """
    SELECT 
        Id,
        COUNT(*) as days_tracked,
        CASE 
            WHEN COUNT(*) <= 10 THEN 'Light'
            WHEN COUNT(*) <= 15 THEN 'Moderate'
            ELSE 'Heavy'
        END as Class
    FROM daily_activity
    GROUP BY Id
    ORDER BY days_tracked DESC
    """
    
    df_classification = pd.read_sql_query(query, conn)
    conn.close()
    
    return df_classification[['Id', 'Class']]


def get_user_stats_by_class(db_path='fitbit_database.db'):
    """
    Get comprehensive statistics for each user class using SQL.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        DataFrame with user-level statistics including classification
    """
    conn = sqlite3.connect(db_path)
    
    # Single SQL query to get all user statistics with classification
    query = """
    SELECT 
        Id,
        COUNT(*) as days_tracked,
        AVG(TotalSteps) as avg_daily_steps,
        AVG(TotalDistance) as avg_daily_distance,
        AVG(Calories) as avg_daily_calories,
        AVG(VeryActiveMinutes) as avg_very_active_min,
        AVG(FairlyActiveMinutes) as avg_fairly_active_min,
        AVG(LightlyActiveMinutes) as avg_lightly_active_min,
        AVG(SedentaryMinutes) as avg_sedentary_min,
        SUM(TotalSteps) as total_steps,
        SUM(TotalDistance) as total_distance,
        CASE 
            WHEN COUNT(*) <= 10 THEN 'Light'
            WHEN COUNT(*) <= 15 THEN 'Moderate'
            ELSE 'Heavy'
        END as Class
    FROM daily_activity
    GROUP BY Id
    ORDER BY days_tracked DESC
    """
    
    df_stats = pd.read_sql_query(query, conn)
    conn.close()
    
    return df_stats


def get_class_summary_stats(db_path='fitbit_database.db'):
    """
    Get summary statistics aggregated by user class.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        DataFrame with statistics summarized by class
    """
    df_user_stats = get_user_stats_by_class(db_path)
    
    # Aggregate by class
    class_summary = df_user_stats.groupby('Class').agg({
        'days_tracked': ['mean', 'min', 'max'],
        'avg_daily_steps': 'mean',
        'avg_daily_distance': 'mean',
        'avg_daily_calories': 'mean',
        'avg_very_active_min': 'mean',
        'avg_sedentary_min': 'mean',
        'total_steps': 'mean',
        'Id': 'count'  # Count of users in each class
    }).round(2)
    
    # Rename the Id count column
    class_summary.columns = ['_'.join(col).strip('_') for col in class_summary.columns]
    class_summary.rename(columns={'Id_count': 'num_users'}, inplace=True)
    
    return class_summary

def visualize_user_distribution_pie(df):
    class_counts = df["Class"].value_counts()

    fig = px.pie(names=class_counts.index, values=class_counts.values,
                 title="User Distribution by Activity Level")
    fig.update_traces(pull=[0.05, 0.05, 0.05],
                      textinfo="percent+label",
                      textfont=dict(size=11))
    return fig

def plot_user_count_by_class(df):
    class_counts = df["Class"].value_counts().reset_index()
    class_counts.columns = ["Class", "Count"]

    fig = px.bar(class_counts, x="Class", y="Count",
                 title="User Count by Class",
                 color="Class",
                 text="Count")
    fig.update_traces(textposition="outside")
    fig.update_yaxes(title_text="Number of Users")
    fig.update_xaxes(title_text="User Class")
    return fig

def visualize_user_distribution(db_path='fitbit_database.db'):
    """
    Create comprehensive visualizations of user classification.
    
    Args:
        db_path: Path to the SQLite database file
    """
    # Get data
    user_classification = classify_users(db_path)
    user_stats = get_user_stats_by_class(db_path)
    
    # Count users in each class
    class_counts = user_classification['Class'].value_counts()
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # Plot 1: Pie chart of distribution
    ax1 = fig.add_subplot(gs[0, 0])
    colors = ['#1dd1a1', '#feca57', '#ff6b6b']
    explode = (0.05, 0.05, 0.05)
    
    wedges, texts, autotexts = ax1.pie(
        class_counts.values, 
        labels=class_counts.index, 
        autopct='%1.1f%%',
        colors=colors, 
        startangle=90,
        explode=explode,
        textprops={'fontsize': 11, 'fontweight': 'bold'}
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax1.set_title('User Distribution by Activity Level', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Plot 2: Bar chart of user counts
    ax2 = fig.add_subplot(gs[0, 1])
    bars = ax2.bar(class_counts.index, class_counts.values, 
                   color=colors, edgecolor='black', alpha=0.7)
    ax2.set_xlabel('User Class', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Users', fontsize=11, fontweight='bold')
    ax2.set_title('User Count by Class', fontsize=13, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Plot 3: Days tracked distribution
    ax3 = fig.add_subplot(gs[0, 2])
    for class_name, color in zip(['Light', 'Moderate', 'Heavy'], colors):
        class_data = user_stats[user_stats['Class'] == class_name]
        ax3.scatter(class_data['days_tracked'], [class_name]*len(class_data),
                   s=100, alpha=0.6, color=color, edgecolor='black')
    
    ax3.set_xlabel('Days Tracked', fontsize=11, fontweight='bold')
    ax3.set_ylabel('User Class', fontsize=11, fontweight='bold')
    ax3.set_title('Activity Tracking Frequency', fontsize=13, fontweight='bold', pad=15)
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.axvline(10.5, color='gray', linestyle='--', alpha=0.5, label='Class boundaries')
    ax3.axvline(15.5, color='gray', linestyle='--', alpha=0.5)
    ax3.legend()
    
    # Plot 4: Average steps by class
    ax4 = fig.add_subplot(gs[1, 0])
    class_avg_steps = user_stats.groupby('Class')['avg_daily_steps'].mean()
    bars = ax4.bar(class_avg_steps.index, class_avg_steps.values,
                   color=colors, edgecolor='black', alpha=0.7)
    ax4.set_xlabel('User Class', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Average Daily Steps', fontsize=11, fontweight='bold')
    ax4.set_title('Average Activity Level by Class', fontsize=13, fontweight='bold', pad=15)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Plot 5: Box plot of steps by class
    ax5 = fig.add_subplot(gs[1, 1])
    class_order = ['Light', 'Moderate', 'Heavy']
    data_for_box = [user_stats[user_stats['Class'] == c]['avg_daily_steps'].values 
                    for c in class_order]
    
    bp = ax5.boxplot(data_for_box, tick_labels=class_order, patch_artist=True,
                     boxprops=dict(alpha=0.7),
                     medianprops=dict(color='red', linewidth=2))
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax5.set_xlabel('User Class', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Average Daily Steps', fontsize=11, fontweight='bold')
    ax5.set_title('Steps Distribution by Class', fontsize=13, fontweight='bold', pad=15)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Plot 6: Active vs Sedentary minutes
    ax6 = fig.add_subplot(gs[1, 2])
    class_active = user_stats.groupby('Class')['avg_very_active_min'].mean()
    class_sedentary = user_stats.groupby('Class')['avg_sedentary_min'].mean()
    
    x = np.arange(len(class_active))
    width = 0.35
    
    bars1 = ax6.bar(x - width/2, class_active.values, width, 
                    label='Very Active', color='limegreen', alpha=0.7, edgecolor='black')
    bars2 = ax6.bar(x + width/2, class_sedentary.values, width,
                    label='Sedentary', color='crimson', alpha=0.7, edgecolor='black')
    
    ax6.set_xlabel('User Class', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Average Minutes', fontsize=11, fontweight='bold')
    ax6.set_title('Activity Composition by Class', fontsize=13, fontweight='bold', pad=15)
    ax6.set_xticks(x)
    ax6.set_xticklabels(class_active.index)
    ax6.legend()
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.savefig('user_data/outputs/part3_user_classification_complete.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Comprehensive user classification visualization saved!")


# Main execution
if __name__ == "__main__":
    import os
    
    print("="*80)
    print("PART 3: USER CLASSIFICATION (DATABASE VERSION)")
    print("="*80)
    print()
    
    # Check if database exists
    if not os.path.exists('fitbit_database.db'):
        print("⚠️  Database file 'fitbit_database.db' not found!")
        print("Please download it from Canvas and place it in this directory.")
        print()
    else:
        print("✓ Database file found!")
        print()
        
        # Classify users
        print("Classifying users using SQL queries...")
        user_classification = classify_users()
        
        print(f"\nTotal users: {len(user_classification)}")
        print("\nUser Classification Summary:")
        print("-"*80)
        print(user_classification['Class'].value_counts())
        print()
        
        # Display sample
        print("Sample Classifications:")
        print("-"*80)
        print(user_classification.head(10))
        print()
        
        # Get detailed statistics
        print("Detailed Statistics by User Class:")
        print("="*80)
        class_summary = get_class_summary_stats()
        print(class_summary)
        print()
        
        # Save classification to CSV
        user_classification.to_csv('user_data/outputs/user_classification_db.csv', 
                                   index=False)
        print("✓ User classification saved to 'user_classification_db.csv'")
        print()
        
        # Get full user stats
        user_stats = get_user_stats_by_class()
        user_stats.to_csv('user_data/outputs/user_stats_by_class.csv', index=False)
        print("✓ Detailed user statistics saved to 'user_stats_by_class.csv'")
        print()
        
        # Create visualizations
        print("Creating comprehensive visualizations...")
        visualize_user_distribution()
        
        print()
        print("="*80)
        print("Classification Complete!")
        print("="*80)
        print()
        print("Key Insights:")
        class_counts = user_classification['Class'].value_counts()
        total = len(user_classification)
        for class_name in ['Heavy', 'Moderate', 'Light']:
            count = class_counts.get(class_name, 0)
            percentage = (count / total) * 100
            print(f"  {class_name:10s}: {count:2d} users ({percentage:5.1f}%)")
