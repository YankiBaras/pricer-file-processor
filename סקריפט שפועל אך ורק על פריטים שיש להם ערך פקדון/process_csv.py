import pandas as pd
import os

# Define the directory containing the CSV files
input_path = r"C:\Pricer\PRICERFILES"

# Process each CSV file in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        # Read the CSV file specifying dtypes or setting low_memory to False
        file_path = os.path.join(input_path, file_name)
        df = pd.read_csv(
            file_path, dtype=str, low_memory=False
        )  # Read everything as string for safety

        # Print the columns of the dataframe for debugging purposes
        print("Columns in the CSV:", df.columns)

        # Strip columns of any leading/trailing whitespace
        df.columns = df.columns.str
        # Convert relevant columns to numeric, handling errors and NaN
        numeric_cols = [
            "PrtMhr",
            "PrtMhrStr100g",
            "PrtMhr100g",
            "MhrMivzaNeto",
            "PrtMhrMivza100g",
            "DepositMhr",
            "DepositQty",
        ]
        for col in numeric_cols:
            # Convert to numeric, coerce errors to NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Perform calculations (ensure you fill missing values appropriately)
        df["PrtMhr"] = df["PrtMhr"].fillna(0) + (
            df.get("DepositMhr", 0).fillna(0) * df.get("DepositQty", 0).fillna(0)
        )

        df["ScmKne"] = df["ScmKne"].fillna(0) + (
            df.get("DepositMhr", 0).fillna(0)
            * df.get("DepositQty", 0).fillna(0)
            * df.get("CmtKne", 0).fillna(0)
        )

        # Additional condition: if DepositQty == 0 and DepositMhr > 0
        condition = (df.get("DepositQty", 0).fillna(0) == 0) & (
            df.get("DepositMhr", 0).fillna(0) > 0
        )
        df.loc[condition, "PrtMhr"] += df.loc[condition, "DepositMhr"].fillna(0)
        df.loc[condition, "ScmKne"] += df.loc[condition, "DepositMhr"].fillna(0)

        # Formatting the relevant columns to two decimal places safely
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: (
                        f"{x:.2f}"
                        if pd.notnull(x) and isinstance(x, (int, float))
                        else ""
                    )
                )

        # Write back to the original CSV file, overwriting it
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

print("Processing complete. Original files have been modified.")
