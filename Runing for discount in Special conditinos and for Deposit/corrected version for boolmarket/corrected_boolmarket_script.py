import csv
import pandas as pd  # type: ignore
import os
import numpy as np  # type: ignore
import shutil  # For backing up files


def process_csv_file(file_path, backup_path):
    """Function to process a given CSV file."""
    backup_file_path = os.path.join(backup_path, os.path.basename(file_path))

    # Backup the original CSV file with error handling
    try:
        shutil.copy(file_path, backup_file_path)
    except PermissionError as e:
        print(f"PermissionError: {e} for file: {file_path}. Skipping this file.")

    # Read the CSV file, specifying dtype as string for safety
    df = pd.read_csv(file_path, dtype=str, low_memory=False)

    # Print the columns of the dataframe for debugging purposes
    print("Columns in the CSV:", df.columns)

    # Normalize column names by stripping whitespace
    df.columns = df.columns.str.strip()

    # Explicitly convert relevant columns to numeric, handling errors
    numeric_cols = [
        "PrtMhr",
        "DepositMhr",
        "DepositQty",
        "ScmKne",
        "CmtKne",
        "MinimumQty",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle NaN values in numeric columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Apply the specified conditions and processing
    condition = (
        (df.get("PrtSwShakil", 0) == 1)
        & (df.get("MivzaDetails", "") == "GENERIC-DISCOUNT")
        & (df.get("MinimumQty", 0) > 0)
    )

    # Step 1: Copy MinimumQty to CmtKne using get()
    df.loc[condition, "CmtKne"] = df.get("MinimumQty", 0)

    # Step 2: Modify CmtKne when MinimumQty is greater than 0 and less than 1
    df.loc[(condition) & (df.get("MinimumQty", 0) < 1), "CmtKne"] *= 1000

    # Step 3: Update ScmKne based on MinimumQty
    df.loc[condition, "ScmKne"] = df.get("ScmKne", 0) * df.get("MinimumQty", 0)

    # Rounding logic for ScmKne AFTER Step 3
    df.loc[condition, "ScmKne"] = df.loc[condition, "ScmKne"].apply(
        lambda x: np.floor(x)
        + (
            np.ceil((x % 1) * 10) / 10
            if (x % 1) >= 0.05
            else np.floor((x % 1) * 10) / 10
        )
    )

    # Step 4: Change MivzaDetails to 'YFOR' if MinimumQty > 0
    df.loc[df["MinimumQty"] > 0, "MivzaDetails"] = "YFOR"

    # Continue with previous calculations using new logic
    for index, row in df.iterrows():
        if float(row.get("DepositQty", 0)) > 0:
            # If DepositQty > 0
            df.at[index, "PrtMhr"] += float(row.get("DepositMhr", 0)) * float(
                row.get("DepositQty", 0)
            )
            df.at[index, "ScmKne"] += (
                float(row.get("DepositMhr", 0))
                * float(row.get("DepositQty", 0))
                * float(row.get("CmtKne", 0))
            )
        else:
            # If DepositQty == 0
            df.at[index, "PrtMhr"] += float(row.get("DepositMhr", 0))
            df.at[index, "ScmKne"] += float(row.get("CmtKne", 0)) * float(
                row.get("DepositMhr", 0)
            )

    # Format all numeric columns to two decimal places
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"{x:.2f}"
            )  # Format to two decimal places

    # Write back to the original CSV file, overwriting it
    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_NONE,
        quotechar='"',
        escapechar="\\",
    )
    print(f"Processed file: {file_path}")


def main():
    # Define the directory containing the CSV files
    input_path = r"C:\Pricer\PRICERFILES"
    backup_path = r"C:\Pricer\FileBackup"

    # Ensure the backup directory exists
    os.makedirs(backup_path, exist_ok=True)

    # Process each CSV file in the input directory
    for file_name in os.listdir(input_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_path, file_name)
            process_csv_file(file_path, backup_path)

    print("Processing complete. Original files have been modified.")


if __name__ == "__main__":
    main()
