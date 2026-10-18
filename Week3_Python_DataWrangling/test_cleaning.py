import pandas as pd
import numpy as np

# Load raw dataset
df_raw = pd.read_csv("data - data.csv")
print("Raw shape:", df_raw.shape)

df = df_raw.copy()

# 1. Clean Date strings: remove single quotes and whitespace, impute missing date
df["Date"] = df["Date"].apply(lambda x: x.replace("'", "").strip() if pd.notnull(x) else "2020/12/22")

# Convert Date to datetime format YYYY-MM-DD
df["Date"] = pd.to_datetime(df["Date"], format="mixed")

# 2. Handle typo in Duration: 450 is a typo for 45
df.loc[df["Duration"] == 450, "Duration"] = 45

# 3. Handle inverted Pulse and Maxpulse (where Pulse > Maxpulse)
mask_inverted = df["Pulse"] > df["Maxpulse"]
if mask_inverted.any():
    print(f"Found {mask_inverted.sum()} row(s) with Pulse > Maxpulse. Correcting inverted values.")
    for idx in df[mask_inverted].index:
        p, mp = df.loc[idx, "Pulse"], df.loc[idx, "Maxpulse"]
        df.loc[idx, "Pulse"] = mp
        df.loc[idx, "Maxpulse"] = p

# 4. Handle missing Calories using median of Duration group
cal_medians = df.groupby("Duration")["Calories"].transform("median")
df["Calories"] = df["Calories"].fillna(cal_medians).round(1)

# 5. Remove duplicate records
dups_count = df.duplicated().sum()
print(f"Duplicates found and removed: {dups_count}")
df = df.drop_duplicates().reset_index(drop=True)

# 6. Derived metrics
df["Calories_Per_Min"] = (df["Calories"] / df["Duration"]).round(2)
df["Pulse_Spread"] = df["Maxpulse"] - df["Pulse"]
df["Day_Name"] = df["Date"].dt.day_name()

def categorize_intensity(pulse):
    if pulse >= 115:
        return "High"
    elif pulse >= 100:
        return "Moderate"
    else:
        return "Low"

df["Intensity_Level"] = df["Pulse"].apply(categorize_intensity)

# 7. Sort by Date
df = df.sort_values("Date").reset_index(drop=True)

print("\n=== CLEANED DATA SUMMARY ===")
print("Shape:", df.shape)
print("Missing values:\n", df.isnull().sum())
print("Duplicates:", df.duplicated().sum())
print("\nSample preview:")
print(df.head(10).to_string())

# Test saving to CSV
df.to_csv("cleaned_dataset.csv", index=False)
print("\ncleaned_dataset.csv created successfully!")
