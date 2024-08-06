import os
import sys
import json
import logging
from pathlib import Path
from termcolor import colored
from linkedin import process_company
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()


# Constants
FOLDER_NAME = "linkedin_scrapes/company"
COMPANIES_JSON_PATH = "../companies_list.json"
CRUNCHBASE_DIRECTORY = f"../crunchbase/{FOLDER_NAME}"
BLACKLISTED_WORDS = [
    "Linkedin not found",
    "nan",
    "linkedin not found",
    "linkedin not foun",
    "Linkedin not found",
    "null",
]


def load_companies():
    """Load companies from the JSON file."""
    with open(COMPANIES_JSON_PATH, "r") as file:
        companies = json.load(file)["companies"]
    logging.info(f"Loaded {len(companies)} companies")
    return companies


def filter_companies(companies):
    """Filter out companies based on blacklist and already scraped."""
    filtered = []
    for company in companies:
        linkedin_url = company.get("Linkedin", "")
        logging.info(
            f"Processing company {company['Company Name']} with LinkedIn URL {linkedin_url}"
        )
        if (
            linkedin_url
            and linkedin_url.lower() in BLACKLISTED_WORDS
            or is_already_scraped(company["Company Name"])
        ):
            logging.info(f"Skipping company {company['Company Name']}")
            continue
        filtered.append(company)
    return filtered


def is_already_scraped(company_name):
    """Check if the company has already been scraped."""
    file_path = Path(FOLDER_NAME) / f"{company_name}.json"
    if file_path.exists():
        print(colored(f"{company_name} - Already Scrapped!", "green"))
        return True
    return False


def scrape_companies(companies):
    """Scrape companies using multiple threads."""
    logging.info(f"Starting to scrape {len(companies)} companies")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                process_company,
                company["Company Name"],
                company["Linkedin"],
                FOLDER_NAME,
            )
            for company in companies
        ]
        for future in futures:
            future.result()  # Wait for all futures to complete
    logging.info("Finished scraping companies")


def main():
    print(colored("Started!", "green"))
    companies = load_companies()
    companies = filter_companies(companies)
    print(colored(f"Going to scrape {len(companies)} LinkedIn URLs", "yellow"))
    scrape_companies(companies)
    print(colored("Finished!", "green"))


if __name__ == "__main__":
    main()
