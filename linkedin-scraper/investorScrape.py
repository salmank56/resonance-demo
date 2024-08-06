import os
import sys
import json
import logging
import threading
from os import listdir
import concurrent.futures
from termcolor import colored
from os.path import isfile, join
from linkedin import process_company

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

def get_files_in_directory(directory):
    return [
        f for f in listdir(directory) if isfile(join(directory, f))
    ]

def process_investor(i, linkedin_value, count, folder_name):
    with SEMAPHORE:
        logging.info(f"Processing {i} - {count} - {linkedin_value}")
        process_company(i, linkedin_value, folder_name=folder_name)

def main():
    print(colored("Started !", "green"))

    files = get_files_in_directory(f"../crunchbase-scraper/investors")
    investors = [i.replace(".json", "") for i in files if i != ".DS_Store" and "partner" not in i]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for count, investor in enumerate(investors):
            with open(f"../crunchbase-scraper/investors/{investor}.json", "r") as outfile:
                temp = json.load(outfile)

            try:
                linkedin_value = temp["cards"]["social_fields"]["linkedin"]["value"]
                logging.info(f"LinkedIn value for {investor}: {linkedin_value}")
                if linkedin_value:
                    future = executor.submit(
                        process_investor, investor, linkedin_value, count, folder_name='investors'
                    )
                    futures.append(future)
                else:
                    print(colored(f"{investor} is not on LinkedIn - Skipping", "yellow"))
            except Exception as e:
                print(colored(f"Exception for {investor}: {e}", "red"))
                print(colored(f"{investor} is not on LinkedIn - Skipping", "yellow"))

        # Wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()

if __name__ == "__main__":
    # Init 4 semaphores for 4 concurrent threads
    SEMAPHORE = threading.Semaphore(4)
    main()