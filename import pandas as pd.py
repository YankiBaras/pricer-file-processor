import pandas as pd
import os

# Define the directory containing the CSV files
input_path = (
    r"C:\Users\yanki\Desktop\Neto_Chisachon_files"  # Update this path as needed
)
output_file = r"C:\Pricer\Extracted_Barcodes.csv"  # Output file path

# Barcode to search for
specific_barcode = (
    "7290001594865"  # Update this with the specific barcode you're looking for
)

# List to store data frames of matched rows
matched_rows = []

# Process each CSV file in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith(".csv"):
        # Construct full file path
        file_path = os.path.join(input_path, file_name)

        # Read the CSV file
        df = pd.read_csv(file_path, dtype=str, low_memory=False)

        # Check if 'PrtBarKod' column exists
        if "PrtBarKod" in df.columns:
            # Filter rows where the 'PrtBarKod' is equal to the specific barcode
            filtered_df = df[df["PrtBarKod"] == specific_barcode]

            # If there are any matching rows, add the filename column and append to the list
            if not filtered_df.empty:
                filtered_df["SourceFile"] = (
                    file_name  # Add a column with the name of the source file
                )
                matched_rows.append(filtered_df)

# Concatenate all matched data frames to a single data frame
if matched_rows:
    result_df = pd.concat(matched_rows, ignore_index=True)
    # Write the results to a new CSV file
    result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(
        f"Extracted rows with barcode {specific_barcode} have been saved to {output_file}"
    )
else:
    print(f"No matches found for barcode {specific_barcode}.")
