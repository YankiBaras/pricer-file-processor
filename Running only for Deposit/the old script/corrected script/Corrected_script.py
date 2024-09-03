import pandas as pd
import os
import csv
import shutil

# Define the directories
input_path = r"C:\Pricer\PRICERFILES"
backup_path = r"C:\Pricer\FileBackup"

# Ensure the backup directory exists
os.makedirs(backup_path, exist_ok=True)

# Process each CSV file in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        # Full file paths
        file_path = os.path.join(input_path, file_name)
        backup_file_path = os.path.join(backup_path, file_name)

        # Backup the original CSV file with error handling
        try:
            shutil.copy(file_path, backup_file_path)
        except PermissionError as e:
            print(f"PermissionError: {e} for file: {file_path}. Skipping this file.")
            continue  # Skip to the next file if backup fails

        # Read the CSV file, specifying dtype as string for safety
        df = pd.read_csv(file_path, dtype=str, low_memory=False)

        # Print the columns of the DataFrame for debugging purposes
        print("Columns in the DataFrame:", df.columns)

        # Strip columns of any leading/trailing whitespace
        df.columns = df.columns.str.strip()

        # Explicitly convert relevant columns to numeric, handling errors
        numeric_cols = ["PrtMhr", "DepositMhr", "DepositQty", "ScmKne", "CmtKne"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Handle NaN values in numeric columns to ensure calculations work correctly
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Perform calculations
        for index, row in df.iterrows():
            if row["DepositQty"] > 0:
                # If DepositQty > 0
                df.at[index, "PrtMhr"] += float(row["DepositMhr"]) * float(
                    row["DepositQty"]
                )
                df.at[index, "ScmKne"] += (
                    float(row["DepositMhr"])
                    * float(row["DepositQty"])
                    * float(row["CmtKne"])
                )
            else:
                # If DepositQty == 0
                df.at[index, "PrtMhr"] += float(row["DepositMhr"])
                df.at[index, "ScmKne"] += float(row["CmtKne"]) * float(
                    row["DepositMhr"]
                )

        # Format all numeric columns to two decimal places
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: f"{x:.2f}"
                )  # Format to two decimal places

        # Columns that should be quoted
        quoted_columns = ["PrtNm", "SmallComments", "MivzaTitle"]

        # Enclose values in quotes or keep them empty quotes if they are null/empty
        for col in quoted_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f'"{x}"' if pd.notnull(x) else '""')

        # Write back to the original CSV file
        df.to_csv(
            file_path,
            index=False,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_NONE,  # Ensures no automatic quoting by pandas
            quotechar='"',  # Specify the character to use for quoting
            escapechar="\\",
        )

print("Processing complete. Original files have been modified.")
