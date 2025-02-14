"""
Z-Score Calculation and Normal Distribution Analysis Script

Author: [Your Name]
Date: [Current Date]

Description:
This script reads an employee dataset, processes pay and email-related metrics, and performs the following operations:
1. Converts necessary columns to numeric.
2. Computes mean and standard deviation for selected columns.
3. Calculates standardized scores (Z-scores) for each data point.
4. Computes cumulative probabilities using the normal distribution.
5. Saves results into an Excel file with separate sheets.

Inputs:
- A CSV file containing employee pay data and email volume metrics.
- Expected columns: 
  - 'PayData': Employee salary information.
  - 'WeeklyEmailCharacterVolume': Weekly volume of email characters sent.
  - 'No_of_Positive_emails_or_Complaint_Emails': Count of positive or complaint emails.

Outputs:
- An Excel file ('Final_PayData_with_Stats.xlsx') with:
  - 'Normal Distribution Settings' sheet containing mean and standard deviation.
  - 'Processed Data' sheet containing original data with calculated Z-scores and cumulative probabilities.

"""

import pandas as pd
from scipy.stats import zscore, norm
import os
import time

# Start execution timer to measure script performance
start_time = time.time()
print("Script execution started...")

# Step 1: Load the dataset
file_path = r"C:\Users\gundl\Downloads\MainData.csv"  # File that contains employee pay data
print("Loading dataset...")
try:
    df = pd.read_csv(file_path)  # Read the file into a pandas DataFrame
    print("Dataset loaded successfully. Shape:", df.shape)
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")  # Handle case where file is missing
    exit()
except pd.errors.EmptyDataError:
    print(f"Error: The file {file_path} is empty.")  # Handle case where file is empty
    exit()
except pd.errors.ParserError:
    print(f"Error: The file {file_path} could not be parsed.")  # Handle case where file has parsing errors
    exit()

# Step 2: Convert relevant columns to numeric format for calculations
columns_to_process = ["PayData", "WeeklyEmailCharacterVolume", "No_of_Positive_emails_or_Complaint_Emails"]
print("Converting columns to numeric format...")

for col in columns_to_process:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert text values to numeric, coerce invalid values to NaN
    num_missing = df[col].isna().sum()
    print(f"Column {col} - Converted to numeric. Missing values: {num_missing}")

# Step 3: Compute mean and standard deviation for each numeric column
print("Calculating mean and standard deviation...")
mean_std_data = {
    "Metric": ["Mean", "St Dev"],  # Define labels for statistical metrics
}

for col in columns_to_process:
    mean_std_data[col] = [df[col].mean(), df[col].std()]  # Compute mean and standard deviation
    print(f"{col} -> Mean: {df[col].mean()}, Std Dev: {df[col].std()}")

# Store mean and standard deviation in a new DataFrame
normal_distribution_settings = pd.DataFrame(mean_std_data)
print("Mean and standard deviation calculations completed.")

# Step 4: Compute standardized scores (Z-scores) to measure deviation from mean
print("Calculating standardized scores (Z-scores)...")
for col in columns_to_process:
    std_dev = df[col].std()
    if std_dev != 0:
        df[f"{col}_StandardisedScore"] = (df[col] - df[col].mean()) / std_dev  # Compute Z-score
    else:
        df[f"{col}_StandardisedScore"] = 0  # Assign zero if standard deviation is zero to avoid division error
    print(f"Computed Z-scores for {col}.")

# Step 5: Compute cumulative probability using normal distribution (CDF)
print("Calculating normal distribution cumulative probabilities...")
for col in columns_to_process:
    df[f"{col}_Normal_Dist"] = norm.cdf(df[col], df[col].mean(), df[col].std()) * 100  # Convert to percentage
    print(f"Computed cumulative probability for {col}.")

# Step 6: Save results into an Excel file with separate sheets
output_file_path = "Final_Data_with_Stats.xlsx"
print("Saving results to Excel file...")

# Ensure the output file has the correct extension
if not output_file_path.endswith(".xlsx"):
    output_file_path = "Final_Data_with_Stats.xlsx"

# Check if the output file exists, remove it first to avoid appending issues
if os.path.exists(output_file_path):
    os.remove(output_file_path)
    print("Existing file removed to ensure a fresh save.")

# Write results to Excel with separate sheets for statistics and processed data
with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
    normal_distribution_settings.to_excel(writer, sheet_name="Normal Distribution Settings", index=False)  # Save mean and std dev
    df.to_excel(writer, sheet_name="Processed Data", index=False)  # Save data with calculated metrics

# End execution timer and log total execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"Processing complete. File saved as {output_file_path}")
print(f"Total execution time: {execution_time:.2f} seconds")
