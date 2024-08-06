import os
import sys
import json
import logging
import threading
import traceback
from scraper import Scraper
from data_extractor import DataExtractor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

folderName = "crunchbase_scrapes"
scraper = Scraper()
data_extractor = DataExtractor(folderName)

def load_companies():
    logging.info("Loading companies...")
    with open("../companies_list.json", "r") as outfile:
        companies = json.load(outfile)["companies"]
    logging.info(f"Loaded {len(companies)} companies.")

    # Filter out already scraped companies
    companies = [company for company in companies if not is_already_scraped(company)]
    logging.info(f"{len(companies)} companies left to scrape.")

    return companies


def is_already_scraped(company):
    # Get a list of all files in the directory
    files = os.listdir(folderName)

    # Check if a file for the company exists
    for file in files:
        if file.startswith(company["Company Name"]):
            logging.info(f'{company["Company Name"]} already scraped')
            return True

    return False


def write_to_file(company, count):
    logging.info(f"Writing data for {company['Company Name']} to file...")
    os.makedirs(folderName, exist_ok=True)  # Create the directory if it doesn't exist
    with open(f"{folderName}/{company['Company Name']}.json", "w") as outfile:
        json.dump(company, outfile)  # Write the entire company dictionary to the file
    logging.info(f"Data for {company['Company Name']} written to file.")


def scrape_company(company, count, companies):
    logging.info(f"Scraping company {count} of {len(companies)}: {company['Company Name']}...")
    try:
        company_json = scraper.scrape_company(company)
        if company_json is not None:
            company["data"] = (
                company_json  # Add the entire JSON response to the company dictionary
            )
            write_to_file(
                company, count
            )  # Write the entire company dictionary to a file
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        traceback.logging.info_exc()
        if "Cannot find" in str(e) and company["Company Name"] in str(e):
            with open("not_found_companies.txt", "a") as f:
                f.write(f"{company['Company Name']}\n")


def scrape_thread(start, end, companies):
    for count, company in enumerate(companies[start:end], start=start):
        # if count <= 399:
        #     continue
        company["Company Name"] = company["Company Name"].replace("/", "-")
        if not is_already_scraped(company):  # Remove the count argument
            scrape_company(company, count, companies)


def scrape_with_threads(companies):
    logging.info("Starting scraping with threads...")
    num_threads = 1
    thread_list = []
    batch_size = len(companies) // num_threads
    for i in range(num_threads):
        start = i * batch_size
        end = (i + 1) * batch_size if i < num_threads - 1 else len(companies)
        thread = threading.Thread(target=scrape_thread, args=(start, end, companies))
        thread_list.append(thread)
        thread.start()
    for thread in thread_list:
        thread.join()
    logging.info("Finished scraping with threads.")


def main():
    companies = load_companies()
    scrape_with_threads(companies)


if __name__ == "__main__":
    main()
