import json
import logging
import pandas as pd
from logger_config import setup_logging
import os

# setup_logging()

df = pd.read_csv("companies_list.csv")

# Replace NaN values with an empty string
df = df.fillna("")

companies = {"companies": []}
# Loop through create a json file for companies name
for index, row in df.iterrows():
    companies["companies"].append(
        {
            "Company Name": row["Company Name"],
            "Website": row["Website"],
            "Linkedin": row["Linkedin URL"],
        }
    )

# Remove existing file if it exists
if os.path.exists("companies_list.json"):
    os.remove("companies_list.json")

with open("companies_list.json", "w") as outfile:
    json.dump(companies, outfile)

print("Conversion completed and old file removed...")
