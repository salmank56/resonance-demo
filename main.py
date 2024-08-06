import os
import json
import logging
import subprocess
from logger_config import setup_logging

setup_logging()

'''
def run_scraper(script_name, cwd):
    process = subprocess.Popen(
        ["python", script_name],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    for stdout_line in iter(process.stdout.readline, ""):
        logging.info(stdout_line.strip())
        #print(stdout_line, end="")
    for stderr_line in iter(process.stderr.readline, ""):
        logging.error(stderr_line.strip())
        #print(stderr_line, end="")

    process.stdout.close()
    process.stderr.close()
    process.wait()
'''

def run_scraper(script_name, cwd):
    process = subprocess.Popen(
        ["python", script_name],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    def handle_line(line, log_function):
        # Check if the line contains a logging format (based on your specific format)
        if ' - ' in line and line.count(' - ') >= 3:
            log_function(line.strip())
        else:
            log_function(line.strip())

    for stdout_line in iter(process.stdout.readline, ""):
        handle_line(stdout_line, logging.info)
    for stderr_line in iter(process.stderr.readline, ""):
        handle_line(stderr_line, logging.error)

    process.stdout.close()
    process.stderr.close()
    process.wait()

def run_crunchbase_scraper():
    logging.info("Running Crunchbase scraper...")
    run_scraper("main.py", "crunchbase-scraper")
    logging.info("Crunchbase scraping completed.")


def run_crunchbase_investor_scraper():
    logging.info("Running Crunchbase investor scraper...")
    run_scraper("investorScrape.py", "crunchbase-scraper")
    logging.info("Crunchbase investor scraping completed.")


def run_linkedin_scraper():
    logging.info("Running LinkedIn scraper...")
    run_scraper("main.py", "linkedin-scraper")
    logging.info("LinkedIn scraping completed.")


def run_linkedin_investor_scraper():
    logging.info("Running LinkedIn investor scraper...")
    run_scraper("investorScrape.py", "linkedin-scraper")
    logging.info("LinkedIn investor scraping completed.")


def run_website_scraper():
    logging.info("Running website scraper...")
    run_scraper("main.py", "website-scraper")
    logging.info("Website scraping completed.")


def run_csv_to_json():
    logging.info("Converting CSV file to JSON...")
    run_scraper("companies_csv_to_json.py", ".")
    logging.info("Conversion completed.")


def main():
    logging.info("Starting all scraping processes...")
    # Run CSV to JSON
    run_csv_to_json()

    # Run Crunchbase scraper
    run_crunchbase_scraper()

    # Run Crunchbase investor scraper
    #run_crunchbase_investor_scraper()

    # Run LinkedIn scraper
    # run_linkedin_scraper()

    # Run LinkedIn investor scraper
    # run_linkedin_investor_scraper()

    # Run website scraper
    # run_website_scraper()

    logging.info("All scraping processes completed.")


if __name__ == "__main__":
    main()
