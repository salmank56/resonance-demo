import os
import sys
import json
import logging
import threading
import pandas as pd
from os import listdir
import concurrent.futures
from termcolor import colored
from os.path import isfile, join
from wscrape import Scraper, process_company

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

def is_already_scraped(company_name):
    folderName = "website_scrapes"
    return os.path.exists(os.path.join(folderName, company_name + ".json"))


def load_companies():
    logging.info("Loading companies...")
    with open("../companies_list.json", "r") as outfile:
        companies = json.load(outfile)["companies"]
    logging.info(f"Loaded {len(companies)} companies.")

    companies = [
        company
        for company in companies
        if not is_already_scraped(company["Company Name"])
    ]
    logging.info(f"{len(companies)} companies left to scrape.")

    return companies

semaphore = threading.Semaphore(4)

def load_companies_from_json():
    with open("../companies_list.json", "r") as file:
        data = json.load(file)
    return data["companies"]

companies_data = load_companies_from_json()

folderName = "website_scrapes"
if not os.path.exists(folderName):
    os.makedirs(folderName)

with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
    futures = []
    for company_data in companies_data:
        company = company_data.get("Company Name")
        url = company_data.get("Website")

        if not url:
            continue

        logging.info(f"Processing company {company} with website {url}")

        try:
            logging.info(
                f"Submitting task for company {company} with website {url} to executor"
            )
            future = executor.submit(
                process_company, company, url, semaphore, folderName=folderName
            )
            futures.append(future)
            logging.info(f"Task for company {company} with website {url} submitted")

        except Exception as e:
            print(
                colored(
                    f"Exception occurred while submitting task for {company} with website {url}: {e}",
                    "red",
                )
            )

    for future in concurrent.futures.as_completed(futures):
        try:
            logging.info("Getting result of future")
            result = future.result()
            logging.info(f"Future completed with result: {result}")
        except Exception as e:
            print(
                colored(
                    f"Exception occurred while getting result of future: {e}", "red"
                )
            )
