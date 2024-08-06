import os
import json
import logging
import subprocess
from logger_config import setup_logging

setup_logging()

def run_crunchbase_scraper():
    logging.info("Running Crunchbase scraper...")
    subprocess.run(["python", "main.py"], cwd="crunchbase-scraper")
    logging.info("Crunchbase scraping completed.")


def run_crunchbase_investor_scraper():
    logging.info("Running Crunchbase investor scraper...")
    subprocess.run(["python", "investorScrape.py"], cwd="crunchbase-scraper")
    logging.info("Crunchbase investor scraping completed.")


def run_linkedin_scraper():
    logging.info("Running LinkedIn scraper...")
    subprocess.run(["python", "main.py"], cwd="linkedin-scraper")
    logging.info("LinkedIn scraping completed.")


def run_linkedin_investor_scraper():
    logging.info("Running LinkedIn investor scraper...")
    subprocess.run(["python", "investorScrape.py"], cwd="linkedin-scraper")
    logging.info("LinkedIn investor scraping completed.")


def run_website_scraper():
    logging.info("Running website scraper...")
    subprocess.run(["python", "main.py"], cwd="website-scraper")
    logging.info("Website scraping completed.")

def run_csv_to_json():
    #logging.info("Converting csv file to json...")
    subprocess.run(["python", "companies_csv_to_json.py"], cwd=".")
    #logging.info("Conversion completed.")


def main():
    logging.info("Starting all scraping processes...")
    # Run CSV to JSON
    run_csv_to_json()

    # Run Crunchbase scraper
    run_crunchbase_scraper()

    # Run Crunchbase investor scraper
    # run_crunchbase_investor_scraper()

    # Run LinkedIn scraper
    # run_linkedin_scraper()

    # Run LinkedIn investor scraper
    # run_linkedin_investor_scraper()

    # Run website scraper
    #run_website_scraper()

    logging.info("All scraping processes completed.")


if __name__ == "__main__":
    main()
