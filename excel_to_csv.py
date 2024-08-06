import pandas as pd

# Load the Excel file
xls = pd.ExcelFile("JUNE 14 SLACK NEW COMPANIES.xlsx")

# Get the names of all sheets in the file
sheet_names = xls.sheet_names

# Loop over the sheet names and read each sheet
for sheet in sheet_names:
    data = pd.read_excel(xls, sheet)
    # Save the data to a CSV file
    data.to_csv(f"{sheet}.csv", index=False)
