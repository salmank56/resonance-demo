import os
import glob
import logging
from logger_config import setup_logging

setup_logging()

# List of directories to remove files from
directories = [
    "crunchbase-scraper/crunchbase_scrapes",
    "crunchbase-scraper/investors",
    "linkedin-scraper/linkedin_scrapes/company",
    "linkedin-scraper/linkedin_scrapes/investors",
    "website-scraper/website_scrapes",
]

logging.info("Removing .json files from directories...")
# Remove .json files from the directories
for directory in directories:
    files = glob.glob(f"{directory}/*.json")
    for file in files:
        os.remove(file)
        
logging.info("Removing .pdf, .crdownload, and .exe files from website-scraper directory...")
# Remove .pdf, .crdownload, and .exe files from website-scraper directory
files = glob.glob("website-scraper/*")
for file in files:
    if file.endswith(".pdf") or file.endswith(".crdownload") or file.endswith(".exe"):
        os.remove(file)

file_path = "crunchbase-scraper/processed_investors_files.txt"
if os.path.exists(file_path):
    logging.info(f"Removing {file_path} file...")
    os.remove(file_path)
else:
    logging.info(f"{file_path} does not exist. No need to remove.")

logging.info("<<< DONE AND READY FOR NEW SCRAPING >>>")