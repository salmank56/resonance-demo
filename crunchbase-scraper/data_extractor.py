import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

class DataExtractor:
    def __init__(self, folderName):
        self.folderName = folderName
        
    def get_investors(self, file):
        investors = []
        with open(f"{self.folderName}/{file}", "r") as outfile:
            try:
                temp = json.loads(outfile.read())["cards"]["investors_list"]
            except:
                logging.info("Cannot find investors_list. Skipping.")
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

        return investors

    def get_funding_rounds(self, file):
        funding_rounds = []
        with open(f"{self.folderName}/{file}", "r") as outfile:
            try:
                temp = json.loads(outfile.read())["cards"]["funding_rounds_list"]
            except:
                logging.info("Cannot find funding_rounds_list. Skipping.")
                return funding_rounds

            for each in temp:
                funding_rounds.append(each["funding_round_identifier"]["value"])

        return funding_rounds

if __name__ == "__main__":
    logging.info("STARTING DATA EXTRACTION...")