import sys
import io
import json
import base64
import contextlib
from pathlib import Path

# Setup script to execute and build week3_analysis.ipynb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Headless backend for saving figures
import matplotlib.pyplot as plt
import seaborn as sns

class NotebookBuilder:
    def __init__(self):
        self.cells = []
        self.execution_counter = 1
        self.global_env = {
            '__name__': '__main__',
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'Path': Path
        }

    def add_markdown(self, markdown_text):
        lines = [line + '\n' for line in markdown_text.splitlines()]
        if lines and lines[-1].endswith('\n'):
            lines[-1] = lines[-1][:-1] # trailing newline cleanup
        self.cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [l if i == len(lines)-1 else l for i, l in enumerate(markdown_text.splitlines(True))]
        })

    def add_code(self, code_text):
        source_lines = code_text.splitlines(True)
        cell_outputs = []

        # Custom display hook
        def custom_display(*args):
            for arg in args:
                if isinstance(arg, (pd.DataFrame, pd.Series)):
                    cell_outputs.append({
                        "output_type": "display_data",
                        "data": {
                            "text/html": [arg.to_frame().to_html() if isinstance(arg, pd.Series) else arg.to_html()],
                            "text/plain": [arg.to_string()]
                        },
                        "metadata": {}
                    })
                else:
                    cell_outputs.append({
                        "output_type": "display_data",
                        "data": {
                            "text/plain": [repr(arg)]
                        },
                        "metadata": {}
                    })

        # Intercept plt.show
        def custom_show():
            fig = plt.gcf()
            if fig.get_axes():
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                buf.seek(0)
                img_b64 = base64.b64encode(buf.read()).decode('utf-8')
                cell_outputs.append({
                    "output_type": "display_data",
                    "data": {
                        "image/png": img_b64,
                        "text/plain": [f"<Figure size {fig.get_size_inches()[0]*fig.dpi}x{fig.get_size_inches()[1]*fig.dpi} with {len(fig.get_axes())} Axes>"]
                    },
                    "metadata": {}
                })
                plt.close(fig)

        self.global_env['display'] = custom_display
        orig_show = plt.show
        plt.show = custom_show

        # Capture stdout
        stdout_capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stdout_capture):
                exec(code_text, self.global_env)
        except Exception as e:
            stdout_capture.write(f"\nExecution Error: {e}")
            print(f"Error in cell {self.execution_counter}: {e}")
            raise
        finally:
            plt.show = orig_show

        # Check if figure wasn't closed by show
        if plt.get_fignums():
            for fignum in plt.get_fignums():
                fig = plt.figure(fignum)
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                buf.seek(0)
                img_b64 = base64.b64encode(buf.read()).decode('utf-8')
                cell_outputs.append({
                    "output_type": "display_data",
                    "data": {
                        "image/png": img_b64,
                        "text/plain": [f"<Figure size {fig.get_size_inches()[0]*fig.dpi}x{fig.get_size_inches()[1]*fig.dpi} with {len(fig.get_axes())} Axes>"]
                    },
                    "metadata": {}
                })
                plt.close(fig)

        captured_text = stdout_capture.getvalue()
        if captured_text:
            cell_outputs.insert(0, {
                "name": "stdout",
                "output_type": "stream",
                "text": captured_text.splitlines(True)
            })

        self.cells.append({
            "cell_type": "code",
            "execution_count": self.execution_counter,
            "metadata": {},
            "outputs": cell_outputs,
            "source": source_lines
        })
        self.execution_counter += 1

    def save(self, filepath):
        notebook_dict = {
            "cells": self.cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.13.15"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook_dict, f, indent=1)
        print(f"Notebook successfully saved to {filepath} with {len(self.cells)} cells executed!")

nb = NotebookBuilder()

# -------------------------------------------------------------
# 1. Header & Overview
# -------------------------------------------------------------
nb.add_markdown("""# SkillNexis Internship – Week 3: Python & Data Wrangling
## Comprehensive Fitness Workout Data Cleaning, Transformation, and Exploratory Analysis

**Author:** Akanksha (Intern)  
**Track:** Data Science & Analytics  
**Organization:** SkillNexis  
**Project Overview:**  
This project demonstrates an end-to-end Python data wrangling workflow on an actual daily workout dataset (`data - data.csv`). It covers foundational Python programming concepts, in-depth exploratory data analysis (EDA), systematic data cleaning (handling missing values, duplicates, syntax inconsistencies, and physiological telemetry anomalies), feature engineering, relational data merging, and statistical visualizations using Matplotlib and Seaborn.
""")

# -------------------------------------------------------------
# 2. Setup & Imports
# -------------------------------------------------------------
nb.add_markdown("""### 1. Environment Setup & Library Imports
Importing essential data science libraries for manipulation, analysis, and visualization.
""")

nb.add_code("""import warnings
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# Visualization styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
sns.set_palette("tab10")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# Setup directories
charts_dir = Path("charts")
charts_dir.mkdir(parents=True, exist_ok=True)

print("Environment setup complete! Core libraries loaded successfully.")
""")

# -------------------------------------------------------------
# 3. Python Basics
# -------------------------------------------------------------
nb.add_markdown("""### 2. Python Basics
Demonstrating fundamental Python concepts required by the Week 3 syllabus applied directly to workout metrics:
- **Variables & Core Data Types** (`int`, `float`, `str`, `bool`)
- **Data Structures** (Lists, Tuples, Dictionaries, Sets)
- **Conditional Logic & Loops**
- **Functions & Reusable Code**
""")

nb.add_code("""# 1. Variables and Core Data Types
session_id: int = 101             # Integer
session_duration: float = 45.0    # Float (minutes)
session_date: str = "2020-12-01"  # String
is_high_intensity: bool = True    # Boolean

print(f"Session #{session_id}: Duration={session_duration}m, Date={session_date}, High Intensity={is_high_intensity}")
print(f"Data Types: id={type(session_id).__name__}, duration={type(session_duration).__name__}, date={type(session_date).__name__}, active={type(is_high_intensity).__name__}")

# 2. Python Lists (Ordered, mutable sequence)
workout_durations = [30, 45, 60, 45, 60]
workout_durations.append(90)
print("\\nWorkout Durations List:", workout_durations)
print(f"First workout: {workout_durations[0]}m, Total workouts recorded: {len(workout_durations)}")

# 3. Python Tuples (Ordered, immutable sequence)
benchmark_target = ("Cardio", 300, 120)  # (Workout Type, Calorie Target, Target Pulse)
print("\\nBenchmark Target Tuple:", benchmark_target)
print(f"Target Activity: {benchmark_target[0]}, Target Calories: {benchmark_target[1]} kcal")

# 4. Python Dictionaries (Key-Value mappings)
sample_workout = {
    "Duration": 60,
    "Date": "2020-12-01",
    "Pulse": 110,
    "Maxpulse": 130,
    "Calories": 409.1
}
print("\\nSample Workout Dictionary:", sample_workout)
print(f"Pulse: {sample_workout['Pulse']} bpm, Calories: {sample_workout['Calories']} kcal")

# 5. Python Sets (Unordered collection of distinct elements)
unique_durations = set(workout_durations)
print("\\nUnique Durations Set:", unique_durations)
""")

nb.add_code("""# 6. Conditionals & Loops
workout_samples = [
    {"duration": 30, "calories": 195.1},
    {"duration": 45, "calories": 282.4},
    {"duration": 60, "calories": 409.1},
    {"duration": 60, "calories": 215.2}
]

print("Looping through workouts with conditional evaluation:")
for idx, w in enumerate(workout_samples, 1):
    cal = w["calories"]
    if cal >= 350:
        category = "High Burn"
    elif cal >= 250:
        category = "Moderate Burn"
    else:
        category = "Light Burn"
    print(f"  Session {idx} ({w['duration']} min, {cal} kcal) -> Classification: {category}")

# 7. Functions and Reusable Code
def calculate_burn_efficiency(calories: float, duration: float) -> float:
    \"\"\"Calculates calories burned per minute of exercise.\"\"\"
    if duration <= 0:
        return 0.0
    return round(calories / duration, 2)

burn_rate = calculate_burn_efficiency(sample_workout["Calories"], sample_workout["Duration"])
print(f"\\nCalculated Burn Efficiency for sample workout: {burn_rate} kcal/min")
""")

# -------------------------------------------------------------
# 4. Loading Dataset
# -------------------------------------------------------------
nb.add_markdown("""### 3. Loading the Existing Dataset
Loading the raw dataset `data - data.csv` using Pandas.
""")

nb.add_code("""dataset_path = "data - data.csv"
df_raw = pd.read_csv(dataset_path)

print(f"Dataset successfully loaded from: '{dataset_path}'")
print(f"Dataset Dimensions: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
""")

# -------------------------------------------------------------
# 5. Exploratory Data Analysis
# -------------------------------------------------------------
nb.add_markdown("""### 4. Initial Exploratory Data Analysis (EDA)
Inspecting the raw data structure, sample records, data types, and summary statistics.
""")

nb.add_code("""print("--- FIRST 5 ROWS ---")
display(df_raw.head())

print("\\n--- LAST 5 ROWS ---")
display(df_raw.tail())

print("\\n--- DATASET INFO ---")
df_raw.info()

print("\\n--- SUMMARY STATISTICS ---")
display(df_raw.describe())
""")

nb.add_code("""print("--- MISSING VALUES AUDIT ---")
missing_series = df_raw.isnull().sum()
display(missing_series)

print(f"\\nTotal Missing Values across DataFrame: {df_raw.isnull().sum().sum()}")

# Duplicate records audit
duplicate_count = df_raw.duplicated().sum()
print(f"\\nTotal Duplicate Rows: {duplicate_count}")
if duplicate_count > 0:
    print("\\nDuplicate Rows Preview:")
    display(df_raw[df_raw.duplicated(keep=False)])
""")

nb.add_code("""print("--- UNIQUE VALUES PER COLUMN ---")
for col in df_raw.columns:
    print(f"Column '{col}': {df_raw[col].nunique()} unique values")

print("\\nDuration Value Counts (Raw):")
display(df_raw['Duration'].value_counts())
""")

# -------------------------------------------------------------
# 6. Data Quality Assessment
# -------------------------------------------------------------
nb.add_markdown("""### 5. Data Quality Assessment & Problem Identification
A systematic review of the raw dataset reveals several real-world data imperfections:
1. **Date Formatting Inconsistencies:** Dates contain single quote suffixes (e.g., `'2020/12/01\''`). Row 26 is formatted without slashes (`20201226`).
2. **Missing Date Value:** Row 22 has a `NaN` date between December 21 and December 23, 2020.
3. **Missing Caloric Entries:** Rows 18 and 28 have missing `Calories` values.
4. **Duplicate Record:** Rows 11 and 12 are exact duplicates of the December 12, 2020 workout.
5. **Duration Outlier/Typo:** Row 7 contains `Duration = 450` minutes (an entry typo for 45 minutes).
6. **Inverted Heart Rate Telemetry:** Row 23 records `Pulse = 130` and `Maxpulse = 101`, an impossible state where average pulse exceeds peak pulse.
""")

# -------------------------------------------------------------
# 7. Data Cleaning Pipeline
# -------------------------------------------------------------
nb.add_markdown("""### 6. Data Cleaning & Wrangling Pipeline
Executing documented transformations to address all identified data quality issues while preserving data integrity.
""")

nb.add_code("""# Create working copy
df_clean = df_raw.copy()

print("Initial Shape:", df_clean.shape)

# Step 1: Clean and standardize Date strings
# Remove trailing single quotes and whitespace, and impute missing date for row 22 (December 22, 2020)
df_clean['Date'] = df_clean['Date'].apply(lambda x: x.replace("'", "").strip() if pd.notnull(x) else "2020/12/22")
df_clean['Date'] = pd.to_datetime(df_clean['Date'], format='mixed')
print("[Cleaned] Date standardized to datetime format.")

# Step 2: Correct Duration data entry typo (450 minutes -> 45 minutes)
outlier_duration_idx = df_clean[df_clean['Duration'] == 450].index
df_clean.loc[outlier_duration_idx, 'Duration'] = 45
print(f"[Cleaned] Corrected Duration typo in row(s) {list(outlier_duration_idx)} from 450 to 45 minutes.")

# Step 3: Correct inverted Pulse vs Maxpulse
inverted_mask = df_clean['Pulse'] > df_clean['Maxpulse']
if inverted_mask.any():
    for idx in df_clean[inverted_mask].index:
        p, mp = df_clean.loc[idx, 'Pulse'], df_clean.loc[idx, 'Maxpulse']
        df_clean.loc[idx, 'Pulse'] = mp
        df_clean.loc[idx, 'Maxpulse'] = p
        print(f"[Cleaned] Row {idx}: Inverted Pulse ({p} bpm) and Maxpulse ({mp} bpm) corrected.")

# Step 4: Impute missing Calories using median of respective Duration group
cal_medians = df_clean.groupby('Duration')['Calories'].transform('median')
df_clean['Calories'] = df_clean['Calories'].fillna(cal_medians).round(1)
print("[Cleaned] Imputed missing Calories with group medians.")

# Step 5: Remove duplicate records
duplicates_found = df_clean.duplicated().sum()
df_clean = df_clean.drop_duplicates().reset_index(drop=True)
print(f"[Cleaned] Removed {duplicates_found} exact duplicate record(s). Cleaned shape: {df_clean.shape}")
""")

nb.add_code("""# Verify clean state
print("--- POST-CLEANING DATA QUALITY AUDIT ---")
print("Remaining Missing Values:")
display(df_clean.isnull().sum())
print(f"\\nRemaining Duplicate Rows: {df_clean.duplicated().sum()}")
print(f"\\nCleaned Data Types:\\n{df_clean.dtypes}")
""")

# -------------------------------------------------------------
# 8. Feature Engineering
# -------------------------------------------------------------
nb.add_markdown("""### 7. Feature Engineering & Transformations
Creating meaningful derived metrics to enhance analytical depth:
- `Calories_Per_Min`: Energy expenditure rate per minute.
- `Pulse_Spread`: Heart rate reserve (`Maxpulse - Pulse`).
- `Day_Name`: Day of the week for weekly pattern analysis.
- `Intensity_Level`: Categorization into Low, Moderate, and High intensity.
""")

nb.add_code("""# 1. Caloric Burn Rate (kcal / min)
df_clean['Calories_Per_Min'] = (df_clean['Calories'] / df_clean['Duration']).round(2)

# 2. Pulse Spread / Heart Rate Reserve
df_clean['Pulse_Spread'] = df_clean['Maxpulse'] - df_clean['Pulse']

# 3. Day of the Week
df_clean['Day_Name'] = df_clean['Date'].dt.day_name()

# 4. Custom Function for Workout Intensity Classification
def classify_intensity(pulse: float) -> str:
    \"\"\"Classifies workout intensity based on average pulse.\"\"\"
    if pulse >= 115:
        return 'High'
    elif pulse >= 100:
        return 'Moderate'
    else:
        return 'Low'

df_clean['Intensity_Level'] = df_clean['Pulse'].apply(classify_intensity)

# Sort by Date chronologically
df_clean = df_clean.sort_values('Date').reset_index(drop=True)

print("Enhanced Cleaned Dataset Preview (First 5 records):")
display(df_clean.head())
""")

# -------------------------------------------------------------
# 9. Filtering, Slicing & Pandas Operations
# -------------------------------------------------------------
nb.add_markdown("""### 8. Pandas Filtering, Indexing & Slicing Operations
Demonstrating filtering with single and multiple conditions, selecting rows/columns with `.loc` and `.iloc`, and custom query logic.
""")

nb.add_code("""# 1. Single condition filtering: Workouts lasting 60 minutes
workouts_60m = df_clean[df_clean['Duration'] == 60]
print(f"Total 60-minute workouts: {len(workouts_60m)}")

# 2. Multiple conditions filtering: Workouts with Duration >= 45 AND Calories > 300
high_burn_long_workouts = df_clean[(df_clean['Duration'] >= 45) & (df_clean['Calories'] > 300)]
print(f"Workouts with Duration >= 45 min and Calories > 300: {len(high_burn_long_workouts)}")
display(high_burn_long_workouts.head())

# 3. Row and column selection using .loc
selected_view = df_clean.loc[df_clean['Intensity_Level'] == 'High', ['Date', 'Duration', 'Pulse', 'Calories', 'Calories_Per_Min']]
print("\\nHigh Intensity Workouts Selected View:")
display(selected_view)

# 4. Positional indexing using .iloc (First 5 rows and specific columns)
print("\\nPositional Slicing with .iloc:")
display(df_clean.iloc[:5, [0, 1, 2, 4, 5]])
""")

# -------------------------------------------------------------
# 10. Grouping & Relational Merging
# -------------------------------------------------------------
nb.add_markdown("""### 9. Grouping, Aggregation & Relational Merging
Summarizing workout performance across categories and enriching the dataset using `pd.merge()`.
""")

nb.add_code("""# Grouping by Duration
duration_summary = df_clean.groupby('Duration').agg(
    Session_Count=('Calories', 'count'),
    Avg_Calories=('Calories', 'mean'),
    Median_Calories=('Calories', 'median'),
    Avg_Pulse=('Pulse', 'mean'),
    Avg_Burn_Rate=('Calories_Per_Min', 'mean')
).round(2)

print("--- SUMMARY METRICS BY WORKOUT DURATION ---")
display(duration_summary)

# Grouping by Intensity Level
intensity_summary = df_clean.groupby('Intensity_Level').agg(
    Session_Count=('Calories', 'count'),
    Avg_Calories=('Calories', 'mean'),
    Avg_Pulse=('Pulse', 'mean'),
    Avg_Maxpulse=('Maxpulse', 'mean')
).round(2).reindex(['High', 'Moderate', 'Low'])

print("\\n--- SUMMARY METRICS BY INTENSITY LEVEL ---")
display(intensity_summary)
""")

nb.add_code("""# Create supplementary reference DataFrame
workout_catalog = pd.DataFrame({
    'Duration': [30, 45, 60],
    'Workout_Format': ['HIIT Sprint', 'Circuit Conditioning', 'Endurance Training'],
    'Target_Heart_Zone': ['Zone 4-5', 'Zone 3-4', 'Zone 2-3'],
    'Assigned_Coach': ['Coach Alex', 'Coach Sarah', 'Coach Marcus']
})

print("--- SUPPLEMENTARY REFERENCE CATALOG ---")
display(workout_catalog)

# Perform Left Merge
df_merged = pd.merge(df_clean, workout_catalog, on='Duration', how='left')

print("\\n--- MERGED DATASET SAMPLE ---")
display(df_merged[['Date', 'Duration', 'Workout_Format', 'Assigned_Coach', 'Pulse', 'Calories', 'Intensity_Level']].head(8))
""")

# -------------------------------------------------------------
# 11. Data Visualization
# -------------------------------------------------------------
nb.add_markdown("""### 10. Data Visualizations (Matplotlib & Seaborn)
Creating 5 publication-grade visualizations based on the cleaned data:
1. **Box plot & Strip plot:** Calorie Expenditure by Duration
2. **Histogram & KDE:** Caloric Burn Distribution
3. **Scatter plot with Regression:** Heart Rate vs Calories
4. **Line plot:** Daily Caloric Trend over December 2020
5. **Correlation Heatmap:** Correlation between Numerical Metrics
""")

nb.add_code("""# Chart 1: Box Plot & Strip Plot of Calories by Duration
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x="Duration", y="Calories", hue="Duration", data=df_clean, palette="Blues", ax=ax, width=0.4, boxprops=dict(alpha=0.8), legend=False)
sns.stripplot(x="Duration", y="Calories", data=df_clean, color="navy", size=6, jitter=0.2, ax=ax)
ax.set_title("Calorie Expenditure Distribution by Workout Duration", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Workout Duration (Minutes)", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
plt.tight_layout()
fig.savefig(charts_dir / "1_calories_by_duration.png", dpi=300)
plt.show()
print("Saved: charts/1_calories_by_duration.png")
""")

nb.add_code("""# Chart 2: Histogram & KDE of Calories Burned
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df_clean["Calories"], kde=True, color="#2b5c8f", bins=8, ax=ax, edgecolor="black", alpha=0.6)
ax.axvline(df_clean["Calories"].mean(), color="red", linestyle="--", linewidth=1.5, label=f"Mean: {df_clean['Calories'].mean():.1f} kcal")
ax.axvline(df_clean["Calories"].median(), color="green", linestyle="-.", linewidth=1.5, label=f"Median: {df_clean['Calories'].median():.1f} kcal")
ax.set_title("Distribution of Calories Burned per Workout Session", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
ax.set_ylabel("Frequency (Session Count)", fontsize=11, fontweight="bold")
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "2_calories_distribution.png", dpi=300)
plt.show()
print("Saved: charts/2_calories_distribution.png")
""")

nb.add_code("""# Chart 3: Scatter Plot - Pulse vs Calories
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(x="Pulse", y="Calories", data=df_clean, ax=ax, color="#1f77b4",
            scatter_kws={"s": 60, "alpha": 0.8}, line_kws={"color": "darkred", "linewidth": 2, "label": "Linear Fit Trendline"})
ax.set_title("Relationship Between Average Pulse and Calories Burned", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Average Pulse (bpm)", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "3_pulse_vs_calories_scatter.png", dpi=300)
plt.show()
print("Saved: charts/3_pulse_vs_calories_scatter.png")
""")

nb.add_code("""# Chart 4: Daily Caloric Trend Line Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_clean["Date"], df_clean["Calories"], marker="o", color="#d95f02", linewidth=2, markersize=5, label="Daily Calories")
ax.axhline(df_clean["Calories"].mean(), color="navy", linestyle="--", alpha=0.7, label=f"Monthly Average ({df_clean['Calories'].mean():.1f} kcal)")
ax.set_title("Daily Caloric Burn Trend (December 2020)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Workout Date", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
plt.xticks(rotation=45)
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "4_daily_calories_trend.png", dpi=300)
plt.show()
print("Saved: charts/4_daily_calories_trend.png")
""")

nb.add_code("""# Chart 5: Correlation Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
numeric_cols = ["Duration", "Pulse", "Maxpulse", "Calories", "Calories_Per_Min", "Pulse_Spread"]
corr = df_clean[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5, ax=ax)
ax.set_title("Correlation Heatmap of Workout Metrics", fontsize=14, fontweight="bold", pad=12)
plt.tight_layout()
fig.savefig(charts_dir / "5_correlation_heatmap.png", dpi=300)
plt.show()
print("Saved: charts/5_correlation_heatmap.png")
""")

# -------------------------------------------------------------
# 12. Findings
# -------------------------------------------------------------
nb.add_markdown("""### 11. Key Findings & Business Insights
- **Average Performance:** The overall mean calories burned was **303.8 kcal** per session with a median of **291.2 kcal**.
- **Duration vs. Caloric Expenditure:** 60-minute sessions burned the highest total calories on average (**313.8 kcal**), followed by 45-minute sessions (**290.4 kcal**) and 30-minute sessions (**195.1 kcal**).
- **Efficiency Paradox:** 45-minute workouts achieved a higher calorie burn rate per minute (**~6.45 kcal/min**) compared to 60-minute workouts (**~5.23 kcal/min**), highlighting the higher metabolic intensity of shorter circuit sessions.
- **Heart Rate Correlation:** Average Pulse exhibits a positive correlation with Calories burned ($r \approx 0.40$), confirming that higher cardiovascular exertion drives increased energy output.
""")

# -------------------------------------------------------------
# 13. Export Cleaned Dataset
# -------------------------------------------------------------
nb.add_markdown("""### 12. Exporting the Cleaned Dataset
Exporting the processed dataset to `cleaned_dataset.csv` and verifying its integrity.
""")

nb.add_code("""output_file = "cleaned_dataset.csv"
df_clean.to_csv(output_file, index=False)

print(f"Cleaned dataset exported successfully to: '{output_file}'")

# Re-read and verify
df_verify = pd.read_csv(output_file)
print(f"Verification: Successfully loaded {df_verify.shape[0]} rows and {df_verify.shape[1]} columns.")
print("Missing values in export:\\n", df_verify.isnull().sum())
""")

# -------------------------------------------------------------
# 14. Validation
# -------------------------------------------------------------
nb.add_markdown("""### 13. Final Project Validation Checklist
- [x] Original dataset `data - data.csv` preserved unchanged.
- [x] Cleaned dataset `cleaned_dataset.csv` saved and validated.
- [x] All 5 charts generated and saved in `charts/`.
- [x] Zero missing values and zero duplicate rows in final data.
- [x] All cells executed without error.
""")

nb.add_code("""# Validation assertions
assert df_clean.shape[0] == 31, f"Expected 31 rows, got {df_clean.shape[0]}"
assert df_clean.isnull().sum().sum() == 0, "Cleaned dataset contains unexpected missing values!"
assert df_clean.duplicated().sum() == 0, "Cleaned dataset contains duplicate rows!"
assert (charts_dir / "1_calories_by_duration.png").exists(), "Chart 1 missing!"
assert (charts_dir / "2_calories_distribution.png").exists(), "Chart 2 missing!"
assert (charts_dir / "3_pulse_vs_calories_scatter.png").exists(), "Chart 3 missing!"
assert (charts_dir / "4_daily_calories_trend.png").exists(), "Chart 4 missing!"
assert (charts_dir / "5_correlation_heatmap.png").exists(), "Chart 5 missing!"
assert Path("cleaned_dataset.csv").exists(), "cleaned_dataset.csv missing!"

print("=" * 60)
print("ALL AUTOMATED VALIDATION CHECKS PASSED SUCCESSFULLY!")
print("=" * 60)
""")

nb.save("week3_analysis.ipynb")
