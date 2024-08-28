import pandas as pd
import os

# Define the directory containing the CSV files
input_path = r"C:\Pricer\PRICERFILES"

# Process each CSV file in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        # Read the CSV file specifying dtype as string for safety
        file_path = os.path.join(input_path, file_name)
        df = pd.read_csv(
            file_path, dtype=str, low_memory=False
        )  # Read everything as string for safety

        # Print the columns of the dataframe for debugging purposes
        print("Columns in the CSV:", df.columns)

        # Explicitly convert relevant columns to numeric, handling errors
        numeric_cols = [" PrtMhr", " DepositMhr", " DepositQty", " ScmKne", " CmtKne"]

        # Convert relevant columns to numeric, coercing errors to NaN
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Handle NaN values in numeric columns to ensure calculations work correctly
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Perform calculations
        df[" PrtMhr"] += df[" DepositMhr"] * df[" DepositQty"]
        df[" ScmKne"] += df[" DepositMhr"] * df[" DepositQty"] * df[" CmtKne"]

        # Additional condition: if DepositQty == 0 and DepositMhr > 0
        condition = (df[" DepositQty"] == 0) & (df[" DepositMhr"] > 0)
        df.loc[condition, " PrtMhr"] += df.loc[condition, " DepositMhr"]
        df.loc[condition, " ScmKne"] += df.loc[condition, " DepositMhr"]

        # Columns that should be quoted (with conditions)
        quoted_columns = [" PrtNm", " MivzaNm", " SmallComments", " MivzaTitle"]

        # Enclose in quotes only if they contain a value
        for col in quoted_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f'"{x}"')

        # Formatting the relevant numeric columns to two decimal places safely
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
