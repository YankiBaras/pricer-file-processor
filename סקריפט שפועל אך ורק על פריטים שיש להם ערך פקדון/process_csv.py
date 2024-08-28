import pandas as pd
import os

# Define the directory containing the CSV files
input_path = r"C:\Pricer\PRICERFILES"

# Process each CSV file in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        # Read the CSV file with low_memory=False to avoid dtype warnings
        file_path = os.path.join(input_path, file_name)
        df = pd.read_csv(file_path, low_memory=False)

        # Print the columns of the dataframe for debugging purposes
        print("Columns in the CSV:", df.columns)

        # Strip any leading/trailing whitespace from column names
        df.columns = df.columns.str.strip()

        # Define numeric columns
        numeric_cols = [
            "PrtMhr",
            "PrtMhrStr100g",
            "PrtMhr100g",
            "MhrMivzaNeto",
            "PrtMhrMivza100g",
            "DepositMhr",
            "DepositQty",
            "CmtKne",
            "ScmKne",
        ]

        # Convert relevant columns to numeric, forcing errors to NaN
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Perform calculations using df.loc
        df.loc[:, "PrtMhr"] += df.loc[:, "DepositMhr"] * df.loc[:, "DepositQty"]
        df.loc[:, "ScmKne"] += (
            df.loc[:, "DepositMhr"] * df.loc[:, "DepositQty"] * df.loc[:, "CmtKne"]
        )

        # Additional condition: if DepositQty == 0 and DepositMhr > 0
        condition = (df["DepositQty"] == 0) & (df["DepositMhr"] > 0)
        df.loc[condition, "PrtMhr"] += df.loc[condition, "DepositMhr"]
        df.loc[condition, "ScmKne"] += df.loc[condition, "DepositMhr"]

        # Format numeric columns to two decimal places as strings
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else ""
                )

        # Write back to the original CSV file, overwriting it
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

print("Processing complete. Original files have been modified.")
