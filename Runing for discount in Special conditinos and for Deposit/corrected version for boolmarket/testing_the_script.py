import pandas as pd  # type: ignore
import os
import numpy as np  # type: ignore
import shutil  # For backing up files
import csv  # For CSV quoting


def process_csv_file(file_path, backup_path):
    """Function to process a given CSV file."""
    backup_file_path = os.path.join(backup_path, os.path.basename(file_path))

    # # Backup the original CSV file with error handling
    # try:
    #     shutil.copy(file_path, backup_file_path)
    # except PermissionError as e:
    #     print(
    #         f"PermissionError: {e} for file: {file_path}. Continuing with processing."
    #     )

    # Read the CSV file, specifying dtype as string for safety
    df = pd.read_csv(file_path, dtype=str, low_memory=False)

    # Debug: Print the DataFrame before applying conditions
    print("DataFrame before applying conditions:")
    print(df.head())

    # Debug: Print column names to verify
    print("Columns in DataFrame:", df.columns.tolist())

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
        (df.get("PrtSwShakil", 0) == "1")
        & (df.get("MivzaDetails", "") == "GENERIC-DISCOUNT")
        & (df.get("MinimumQty", 0) > 0)
    )

    # Debug: Evaluate conditions manually
    print("Evaluating conditions:")
    print("PrtSwShakil condition:", df.get("PrtSwShakil", 0) == "1")
    print("MivzaDetails condition:", df.get("MivzaDetails", "") == "GENERIC-DISCOUNT")
    print("MinimumQty condition:", df.get("MinimumQty", 0) > 0)

    # Debug: Print the condition array
    print("Condition array:")
    print(condition)

    # Check how many rows satisfy the condition
    print("Condition True values count:", condition.sum())

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

    # Format all numeric columns to two decimal places
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: f"{x:.2f}"
            )  # Format to two decimal places

    # Columns that should be quoted based on specific conditions
    quoted_columns = [
        "PrtNm",
        "MivzaNm",
        "MivzaDetails",
        "SmallComments",
        "MivzaTitle",
        "SmallComments2",
    ]

    # Enclose values in quotes based on given requirements
    for col in quoted_columns:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: (
                    f'"{x}"'
                    if pd.notnull(x) and x != ""
                    else '""' if col in ["SmallComments", "MivzaTitle"] else x
                )
            )

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
