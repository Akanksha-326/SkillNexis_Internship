import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
sns.set_palette("tab10")

charts_dir = Path("charts")
charts_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("cleaned_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

# Chart 1: Box Plot & Bar Chart of Calories by Duration
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x="Duration", y="Calories", data=df, palette="Blues", ax=ax, width=0.4, boxprops=dict(alpha=0.8))
sns.stripplot(x="Duration", y="Calories", data=df, color="navy", size=6, jitter=0.2, ax=ax)
ax.set_title("Calorie Expenditure Distribution by Workout Duration", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Workout Duration (Minutes)", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
plt.tight_layout()
fig.savefig(charts_dir / "1_calories_by_duration.png", dpi=300)
plt.close(fig)
print("Chart 1 saved.")

# Chart 2: Histogram & KDE of Calories Burned
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df["Calories"], kde=True, color="#2b5c8f", bins=8, ax=ax, edgecolor="black", alpha=0.6)
ax.axvline(df["Calories"].mean(), color="red", linestyle="--", linewidth=1.5, label=f"Mean: {df['Calories'].mean():.1f} kcal")
ax.axvline(df["Calories"].median(), color="green", linestyle="-.", linewidth=1.5, label=f"Median: {df['Calories'].median():.1f} kcal")
ax.set_title("Distribution of Calories Burned per Workout Session", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
ax.set_ylabel("Frequency (Session Count)", fontsize=11, fontweight="bold")
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "2_calories_distribution.png", dpi=300)
plt.close(fig)
print("Chart 2 saved.")

# Chart 3: Scatter Plot - Pulse vs Calories with Regression Trendline
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(x="Pulse", y="Calories", data=df, ax=ax, color="#1f77b4",
            scatter_kws={"s": 60, "alpha": 0.8}, line_kws={"color": "darkred", "linewidth": 2, "label": "Trendline"})
ax.set_title("Relationship Between Average Pulse and Calories Burned", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Average Pulse (bpm)", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "3_pulse_vs_calories_scatter.png", dpi=300)
plt.close(fig)
print("Chart 3 saved.")

# Chart 4: Time Series Line Plot - Daily Caloric Expenditure Over Time
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Date"], df["Calories"], marker="o", color="#d95f02", linewidth=2, markersize=5, label="Daily Calories")
ax.axhline(df["Calories"].mean(), color="navy", linestyle="--", alpha=0.7, label=f"Monthly Average ({df['Calories'].mean():.1f} kcal)")
ax.set_title("Daily Caloric Burn Trend (December 2020)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Workout Date", fontsize=11, fontweight="bold")
ax.set_ylabel("Calories Burned (kcal)", fontsize=11, fontweight="bold")
plt.xticks(rotation=45)
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(charts_dir / "4_daily_calories_trend.png", dpi=300)
plt.close(fig)
print("Chart 4 saved.")

# Chart 5: Correlation Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
numeric_cols = ["Duration", "Pulse", "Maxpulse", "Calories", "Calories_Per_Min", "Pulse_Spread"]
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5, ax=ax)
ax.set_title("Correlation Heatmap of Workout Metrics", fontsize=14, fontweight="bold", pad=12)
plt.tight_layout()
fig.savefig(charts_dir / "5_correlation_heatmap.png", dpi=300)
plt.close(fig)
print("Chart 5 saved.")
