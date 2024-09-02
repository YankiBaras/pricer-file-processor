import pandas as pd  # type: ignore
import os
import numpy as np  # type: ignore


def process_csv_file(file_path):
    """Function to process a given CSV file."""
    df = pd.read_csv(file_path)

    # Print the columns of the dataframe for debugging purposes
    print("Columns in the CSV:", df.columns)

    # Normalize column names by stripping whitespace
    df.columns = df.columns.str.strip()

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

    # Continue with previous calculations
    df["PrtMhr"] = df["PrtMhr"] + (
        df.get("DepositMhr", 0).fillna(0) * df.get("DepositQty", 0).fillna(0)
    )

    # Update ScmKne again after calculations with Deposit values
    df["ScmKne"] = df["ScmKne"] + (
        df.get("DepositMhr", 0).fillna(0)
        * df.get("DepositQty", 0).fillna(0)
        * df.get("CmtKne", 0).fillna(0)
    )

    # Additional condition: if DepositQty == 0 and DepositMhr > 0
    condition_additional = (df.get("DepositQty", 0) == 0) & (
        df.get("DepositMhr", 0) > 0
    )
    df.loc[condition_additional, "PrtMhr"] += df.get("DepositMhr", 0)
    df.loc[condition_additional, "ScmKne"] += df.get("DepositMhr", 0)

    # Write back to the original CSV file, overwriting it
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"Processed file: {file_path}")


def main():
    # Define the directory containing the CSV files
    input_path = r"C:\Pricer\PRICERFILES"

    # Process each CSV file in the input directory
    for file_name in os.listdir(input_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_path, file_name)
            process_csv_file(file_path)

    print("Processing complete. Original files have been modified.")


if __name__ == "__main__":
    main()
