import pandas as pd
import os
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

        # Create backup of the original CSV file
        shutil.copy(file_path, backup_file_path)

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Print the columns of the DataFrame for debugging purposes
        print("Columns in the CSV:", df.columns)

        # Strip columns of any leading/trailing whitespace
        df.columns = df.columns.str.strip()

        # Perform calculations
        df["PrtMhr"] = df["PrtMhr"] + (
            df.get("DepositMhr", 0).fillna(0) * df.get("DepositQty", 0).fillna(0)
        )

        df["ScmKne"] = df["ScmKne"] + (
            df.get("DepositMhr", 0).fillna(0)
            * df.get("DepositQty", 0).fillna(0)
            * df.get("CmtKne", 0).fillna(0)
        )

        # Additional condition: if DepositQty == 0 and DepositMhr > 0
        condition = (df.get("DepositQty", 0).fillna(0) == 0) & (
            df.get("DepositMhr", 0).fillna(0) > 0
        )
        df.loc[condition, "PrtMhr"] += df.loc[condition, "DepositMhr"]
        df.loc[condition, "ScmKne"] += df.loc[condition, "DepositMhr"]

        # Write back to the original CSV file, overwriting it
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

print("Processing complete. Original files have been modified.")
