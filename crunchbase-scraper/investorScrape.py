import os
import sys
import time
import json
import logging
import traceback
from os import listdir
import concurrent.futures
from os.path import isfile, join
from crunchbase import Crunchbase

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

# Directory to save investor data
investor_directory = "investors"
# Directory to find company data
company_directory = "crunchbase_scrapes"

# List of investors that could not be scraped
quarantined_investors = []

# Initialize Crunchbase object
crunchbase = Crunchbase()

# Get list of company files in the company directory
company_files = [
    f for f in listdir(company_directory) if isfile(join(company_directory, f))
]


def extract_investors_from_file(file):
    """
    Extracts investors from a given company file.
    """
    logging.info(f"Extracting investors from {file}...")
    investors = []

    processed_files_path = "processed_investors_files.txt"

    with open(f"{company_directory}/{file}", "r") as outfile:
        try:
            temp = json.loads(outfile.read())["data"]["cards"]["investors_list"]
        except:
            logging.info("Cannot find investors_list. Skipping.")

            # Save the file name to the processed files list
            with open(processed_files_path, "a") as processed_file:
                processed_file.write(file + "\n")

            return investors

        for each in temp:
            investors.append(each["investor_identifier"]["value"])
            try:
                for eachh in each["partner_identifiers"]:
                    investors.append(
                        f"{eachh['value']} partner {each['investor_identifier']['value']}"
                    )
            except:
                pass

    logging.info(f"Extracted {len(investors)} investors from {file}.")
    
    return investors

def process_investor(investor, company_file, crunchbase_ids):
    logging.info(f"Processing investor : {investor}")
    investor = investor.replace("/", " ")
    investor = investor.replace("|", " ")

    try:
        # Check if investor data already exists
        logging.info(f"Checking if data for {investor} already exists...")
        with open(f"{investor_directory}/{investor}.json", "r") as outfile:
            investor_data = json.loads(outfile.read())
            logging.info(f"Data for {investor} already exists.")
            try:
                # Check if links_to field exists
                old_links = investor_data["links_to"]
                if company_file not in old_links:
                    investor_data["links_to"].append(company_file)
            except:
                investor_data["links_to"] = [company_file]
            with open(f"{investor_directory}/{investor}.json", "w") as outfile:
                json.dump(investor_data, outfile)
            return
        
    except FileNotFoundError:
        pass

    if investor in quarantined_investors:
        return

    logging.info(f"Scraping data for {investor} from Crunchbase...")
    try:
        crunchbase_id, is_person = crunchbase_ids[investor]
    except KeyError:
        logging.info(f"No Crunchbase ID found for {investor}. Skipping.")
        return

    logging.info(f"Crunchbase ID for {investor}: {crunchbase_id}")

    try:
        investor_data = crunchbase.get_investor_details(
            crunchbase_id, isPerson=is_person
        )
        if investor_data is None:
            logging.info(f"Adding {investor} to quarantine!")
            quarantined_investors.append(investor)
            return

        investor_data["links_to"] = company_file
        with open(f"{investor_directory}/{investor}.json", "w") as outfile:
            json.dump(investor_data, outfile)
        logging.info(f"Data for {investor} written to file.")

    except Exception as e:
        logging.error(f"Exception occurred while scraping data for {investor}: {e}")
        with open("error-logs.txt", "a") as error_file:
            error_file.write(f"Error in process_investor for {investor}: {str(e)}\n")
            error_file.write(traceback.format_exc() + "\n")


def scrape_investor_data():
    """
    Scrapes investor data for each company.
    """
    logging.info("Starting to scrape investor data...")

    processed_files_path = "processed_investors_files.txt"

    # Load the list of processed files
    if os.path.exists(processed_files_path):
        with open(processed_files_path, "r") as processed_file:
            processed_files = set(line.strip() for line in processed_file)
    else:
        processed_files = set()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for file_count, company_file in enumerate(company_files):

            if company_file == ".DS_Store":
                continue

            if company_file in processed_files:
                logging.info(f"{company_file} is already processed. Skipping.")
                continue

            logging.info(
                f"Processing company file {file_count} of {len(company_files)}: {company_file}..."
            )

            investors = extract_investors_from_file(company_file)

            # Get Crunchbase IDs for all investors at once using multithreading
            crunchbase_ids = crunchbase.getCrunchbaseIDs(investors)

            for investor in reversed(investors):
                future = executor.submit(
                    process_investor, investor, company_file, crunchbase_ids
                )
                futures.append(future)
            
            logging.info(f"Saving {company_file} to processed_files.txt...")
            # Save the file name to the processed files list
            with open(processed_files_path, "a") as processed_file:
                processed_file.write(company_file + "\n")

        concurrent.futures.wait(futures)

    logging.info("Finished scraping investor data.")


scrape_investor_data()

