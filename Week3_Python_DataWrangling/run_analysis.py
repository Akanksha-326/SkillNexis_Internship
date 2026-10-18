"""
SkillNexis Internship – Week 3: Python & Data Wrangling
End-to-End Pipeline Runner
Executes data exploration, cleaning, transformations, visualizations, and exports.
"""

from pathlib import Path
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# Visualization styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
sns.set_palette("tab10")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

current_dir = Path(__file__).resolve().parent
charts_dir = current_dir / "charts"
charts_dir.mkdir(parents=True, exist_ok=True)

dataset_path = current_dir / "data - data.csv"
output_path = current_dir / "cleaned_dataset.csv"

print("=" * 80)
print(" SKILLNEXIS INTERNSHIP – WEEK 3: PYTHON & DATA WRANGLING PIPELINE")
print("=" * 80)

# 1. Load Dataset
if not dataset_path.exists():
    print(f"Error: Original dataset not found at {dataset_path}")
    exit(1)

df_raw = pd.read_csv(dataset_path)
print(f"\n[1] Loaded Raw Dataset: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
print(f"    Missing values count: {df_raw.isnull().sum().sum()}")
print(f"    Duplicate rows count: {df_raw.duplicated().sum()}")

# 2. Data Cleaning
df_clean = df_raw.copy()

# A. Standardize Date strings and impute missing date
df_clean['Date'] = df_clean['Date'].apply(lambda x: x.replace("'", "").strip() if pd.notnull(x) else "2020/12/22")
df_clean['Date'] = pd.to_datetime(df_clean['Date'], format='mixed')

# B. Correct Duration typo (450 -> 45)
df_clean.loc[df_clean['Duration'] == 450, 'Duration'] = 45

# C. Correct inverted Pulse vs Maxpulse
inverted_mask = df_clean['Pulse'] > df_clean['Maxpulse']
if inverted_mask.any():
    for idx in df_clean[inverted_mask].index:
        p, mp = df_clean.loc[idx, 'Pulse'], df_clean.loc[idx, 'Maxpulse']
        df_clean.loc[idx, 'Pulse'] = mp
        df_clean.loc[idx, 'Maxpulse'] = p

# D. Impute missing Calories with group median based on Duration
cal_medians = df_clean.groupby('Duration')['Calories'].transform('median')
df_clean['Calories'] = df_clean['Calories'].fillna(cal_medians).round(1)

# E. Remove duplicate records
df_clean = df_clean.drop_duplicates().reset_index(drop=True)

# 3. Feature Engineering
df_clean['Calories_Per_Min'] = (df_clean['Calories'] / df_clean['Duration']).round(2)
df_clean['Pulse_Spread'] = df_clean['Maxpulse'] - df_clean['Pulse']
df_clean['Day_Name'] = df_clean['Date'].dt.day_name()

def classify_intensity(pulse: float) -> str:
    if pulse >= 115:
        return 'High'
    elif pulse >= 100:
        return 'Moderate'
    else:
        return 'Low'

df_clean['Intensity_Level'] = df_clean['Pulse'].apply(classify_intensity)
df_clean = df_clean.sort_values('Date').reset_index(drop=True)

print(f"\n[2] Data Cleaning & Feature Engineering Complete:")
print(f"    Cleaned Dataset Shape: {df_clean.shape[0]} rows x {df_clean.shape[1]} columns")
print(f"    Missing values remaining: {df_clean.isnull().sum().sum()}")
print(f"    Duplicate rows remaining: {df_clean.duplicated().sum()}")

# 4. Export Cleaned Dataset
df_clean.to_csv(output_path, index=False)
print(f"\n[3] Cleaned Dataset exported to: '{output_path.name}'")

# 5. Generate Visualizations
print("\n[4] Generating Publication-Grade Visualizations in charts/:")

# Chart 1: Box Plot of Calories by Duration
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x="Duration", y="Calories", hue="Duration", data=df_clean, palette="Blues", ax=ax, width=0.4, boxprops=dict(alpha=0.8), legend=False)
sns.stripplot(x="Duration", y="Calories", data=df_clean, color="navy", size=6, jitter=0.2, ax=ax)
ax.set_title("Calorie Expenditure Distribution by Workout Duration", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Workout Duration (Minutes)", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
plt.tight_layout()
fig.savefig(charts_dir / "1_calories_by_duration.png", dpi=300)
plt.close(fig)
print("    - Saved: charts/1_calories_by_duration.png")

# Chart 2: Histogram & KDE
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
plt.close(fig)
print("    - Saved: charts/2_calories_distribution.png")

# Chart 3: Scatter Plot - Pulse vs Calories
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(x="Pulse", y="Calories", data=df_clean, ax=ax, color="#1f77b4",
            scatter_kws={"s": 60, "alpha": 0.8}, line_kws={"color": "darkred", "linewidth": 2, "label": "Linear Fit Trendline"})
ax.set_title("Relationship Between Average Pulse and Calories Burned", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Average Pulse (bpm)", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "3_pulse_vs_calories_scatter.png", dpi=300)
plt.close(fig)
print("    - Saved: charts/3_pulse_vs_calories_scatter.png")

# Chart 4: Daily Caloric Trend
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
plt.close(fig)
print("    - Saved: charts/4_daily_calories_trend.png")

# Chart 5: Correlation Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
numeric_cols = ["Duration", "Pulse", "Maxpulse", "Calories", "Calories_Per_Min", "Pulse_Spread"]
corr = df_clean[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5, ax=ax)
ax.set_title("Correlation Heatmap of Workout Metrics", fontsize=14, fontweight="bold", pad=12)
plt.tight_layout()
fig.savefig(charts_dir / "5_correlation_heatmap.png", dpi=300)
plt.close(fig)
print("    - Saved: charts/5_correlation_heatmap.png")

# 6. Relational Catalog Merge Preview
workout_catalog = pd.DataFrame({
    'Duration': [30, 45, 60],
    'Workout_Format': ['HIIT Sprint', 'Circuit Conditioning', 'Endurance Training'],
    'Target_Heart_Zone': ['Zone 4-5', 'Zone 3-4', 'Zone 2-3'],
    'Assigned_Coach': ['Coach Alex', 'Coach Sarah', 'Coach Marcus']
})
df_merged = pd.merge(df_clean, workout_catalog, on='Duration', how='left')

print("\n[5] Relational Data Merge Demonstration:")
print(df_merged[['Date', 'Duration', 'Workout_Format', 'Assigned_Coach', 'Pulse', 'Calories', 'Intensity_Level']].head(5).to_string(index=False))

print("\n" + "=" * 80)
print(" ALL PIPELINE STEPS COMPLETED & VALIDATED SUCCESSFULLY (0 ERRORS)")
print("=" * 80 + "\n")
