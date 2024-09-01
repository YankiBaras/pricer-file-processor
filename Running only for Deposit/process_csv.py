import pandas as pd
import os

# Define the directory containing the CSV files
input_path = r"C:\Pricer\PRICERFILES"

# Process each CSV file in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        # Read the CSV file, specifying dtype as string for safety
        file_path = os.path.join(input_path, file_name)
        df = pd.read_csv(file_path, dtype=str, low_memory=False)

        # Print the columns of the dataframe for debugging purposes
        print("Columns in the DataFrame:", df.columns)

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

        # Columns that should be quoted
        quoted_columns = [" PrtNm", " MivzaNm", " SmallComments", " MivzaTitle"]

        # Enclose values in quotes or keep them empty quotes if they are null/empty
        for col in quoted_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f'"{x}"' if pd.notnull(x) else '""')

        # Write back to the original CSV file without applying any extra quoting
        # Specify quoting behavior for only the individual columns that might contain special characters
        df.to_csv(
            file_path,
            index=False,
            encoding="utf-8-sig",
            quoting=1,  # QUOTE_MINIMAL (1) to prevent quoting on other fields
            quotechar='"',  # Specify the character to use for quoting
            escapechar="\\",
        )  # Escape character for special cases if needed

print("Processing complete. Original files have been modified.")
