import os
import sys
import time
import random
import logging
import traceback
from crunchbase import Crunchbase

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

class Scraper:
    def __init__(self):
        self.crunchbase = Crunchbase()
        
    def scrape_company(self, company):
        logging.info(f"Scraping company {company} ...")
        time.sleep(random.randint(1, 5))
        try:
            logging.info(f"Scraping company: {company['Company Name']}...")
            _, (company["crunchbase_id"], is_person) = self.crunchbase.getCrunchbaseID(
                company["Company Name"]
            )
            if "/" in company["crunchbase_id"]:
                company["crunchbase_id"] = company["crunchbase_id"].split("/")[0]
            company_json = self.crunchbase.get_company_details(
                company["crunchbase_id"], is_person
            )
            logging.info(f"Got data for {company['Company Name']}.")
            return company_json
        except Exception as e:
            logging.error(f"Error while scraping company {company['Company Name']}: {e}")
            with open("error-logs.txt", "a") as error_file:
                error_file.write(
                    f"Error in scrape_company for {company['Company Name']}: {str(e)}\n"
                )
                error_file.write(traceback.format_exc() + "\n")
            return None

    def scrape_investor(self, investor):
        time.sleep(random.randint(1, 5))
        try:
            logging.info(f"Scraping investor: {investor['Investor Name']}...")
            _, (investor["crunchbase_id"], is_person) = self.crunchbase.getCrunchbaseID(
                investor["Investor Name"]
            )
            if "/" in investor["crunchbase_id"]:
                investor["crunchbase_id"] = investor["crunchbase_id"].split("/")[0]
            investor_data = self.crunchbase.get_investor_details(
                investor["crunchbase_id"], is_person
            )
            logging.info(f"Got data for {investor['Investor Name']}.")
            return investor_data
        except Exception as e:
            logging.error(f"Error while scraping investor {investor['Investor Name']}: {e}")
            with open("error-logs.txt", "a") as error_file:
                error_file.write(
                    f"Error in scrape_investor for {investor['Investor Name']}: {str(e)}\n"
                )
                error_file.write(traceback.format_exc() + "\n")
            return None

