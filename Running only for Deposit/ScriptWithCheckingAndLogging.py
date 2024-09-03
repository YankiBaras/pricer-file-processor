import pandas as pd
import os
import csv
import shutil
import logging
from datetime import datetime

# Set up logging with a unique filename based on date and time
log_filename = f"process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",  # Overwrite the log file each time
)

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

        # Backup the original CSV file
        shutil.copy(file_path, backup_file_path)

        # Read the CSV file, specifying dtype as string for safety
        df = pd.read_csv(file_path, dtype=str, low_memory=False)

        # Print the columns of the DataFrame for debugging purposes
        logging.info(f"Processing file: {file_name}")
        logging.info(f"Columns in the DataFrame: {df.columns.tolist()}")

        # Explicitly convert relevant columns to numeric, handling errors
        numeric_cols = [" PrtMhr", " DepositMhr", " DepositQty", " ScmKne", " CmtKne"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Handle NaN values in numeric columns to ensure calculations work correctly
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Initialize set to store modified row indices
        modified_rows = set()

        # Perform calculations
        # Check modifications directly
        if " PrtMhr" in df and " DepositMhr" in df and " DepositQty" in df:
            pre_calc = df[" PrtMhr"].copy()
            df[" PrtMhr"] += df[" DepositMhr"] * df[" DepositQty"]
            modified_rows.update(df.index[df[" PrtMhr"] != pre_calc])

        if " ScmKne" in df and " CmtKne" in df:
            pre_calc = df[" ScmKne"].copy()
            df[" ScmKne"] += df[" DepositMhr"] * df[" DepositQty"] * df[" CmtKne"]
            modified_rows.update(df.index[df[" ScmKne"] != pre_calc])

        # Additional condition: if DepositQty == 0 and DepositMhr > 0
        if " DepositQty" in df and " DepositMhr" in df:
            condition = (df[" DepositQty"] == 0) & (df[" DepositMhr"] > 0)
            if " PrtMhr" in df and " ScmKne" in df:
                pre_calc_prt = df.loc[condition, " PrtMhr"].copy()
                pre_calc_scm = df.loc[condition, " ScmKne"].copy()

                df.loc[condition, " PrtMhr"] += df.loc[condition, " DepositMhr"]
                df.loc[condition, " ScmKne"] += df.loc[condition, " DepositMhr"]

        # Log the modified rows
        if modified_rows:
            logging.info(f"Modified rows in file {file_name}: {sorted(modified_rows)}")

        # Format DepositMhr and DepositQty to two decimal places
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else "0.00")


        # Columns that should be quoted
        quoted_columns = [" PrtNm", " SmallComments", " MivzaTitle"]

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

logging.info("Processing complete. Original files have been modified.")
print("Processing complete. Original files have been modified.")
