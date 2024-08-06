import re
import os
import csv
import sys
import json
import time
import pathlib
import logging
import requests
import threading
import concurrent.futures
from termcolor import colored
from bs4 import BeautifulSoup
from urllib.parse import unquote
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

def getDomain(url):
    pattern = r"https://[^/]+"
    match = re.search(pattern, url)
    if match:
        top_level_link = match.group(0)
        return top_level_link
    return ""


def extract_middle_part(url):
    parsed_url = urlparse(url)
    parts = parsed_url.netloc.split(".")
    if len(parts) >= 2:
        middle_part = parts[-2]
    else:
        middle_part = parts[-1]
    return middle_part


class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        

    def getText(self, url, to_scan=None, all_text=[]):
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text()
                all_text.append({url: text})
                elems = soup.find_all("a", href=True)
                if to_scan is None:
                    to_scan = []
                    for elem in elems:
                        elem_url = elem["href"]
                        if str(extract_middle_part(url)) in extract_middle_part(
                            str(elem_url)
                        ):
                            if str(elem_url) not in to_scan:
                                to_scan.append(elem_url)
                                to_scan = to_scan[:5]
                if to_scan:
                    to_scan.pop(0)
                    if len(to_scan) != 0:
                        return self.getText(to_scan[0], to_scan, all_text)
                    if len(to_scan) == 0:
                        return all_text
                    to_scan = to_scan[:5]
                    return self.getText(to_scan[0], to_scan, all_text)
            else:
                print(
                    colored(
                        f"{url} - Failed with status code {response.status_code}",
                        "yellow",
                    )
                )
        except requests.exceptions.RequestException as e:
            print(colored(f"{url} - {str(e)}", "yellow"))
        return all_text


def process_investor(each, url, count, folderName):
    try:
        with open(f"{folderName}/{each}.json", "r") as outfile:
            print(colored(f"Already scrapped {each}", "green"))
            return None
    except:
        s = Scraper()
        text = s.getText(url, to_scan=None, all_text=[])
        if len(text) != 0:
            each = each.replace("/", "-")
            with open(f"{folderName}/{each}.json", "w", encoding="utf-8") as outfile:
                json.dump({"text": text}, outfile, ensure_ascii=False)
            print(colored(f"{url} - Success !", "green"))
            if (count % 10) == 0:
                print(colored(f"{count+1} - Completed !", "green"))
            return
        print(colored(f"{url} - Failed !", "red"))


def process_company(each, url, count, folderName):
    logging.info(f"Starting process_company for {each}")
    try:
        with open(f"{folderName}/{each}.json", "r") as outfile:
            print(colored(f"Already scrapped {each}", "green"))
            return None
    except:
        logging.info(f"Starting new scrape for {each}")
        s = Scraper()
        logging.info(f"Getting text for {each}")
        text = s.getText(url, to_scan=None, all_text=[])
        logging.info(f"Got Text for {each} ...")
        if len(text) != 0:
            each = each.replace("/", "-")
            logging.info(f"Writing data for {each} to file")
            with open(f"website_scrapes/{each}.json", "w", encoding="utf-8") as outfile:
                json.dump({"text": text}, outfile, ensure_ascii=False)
            print(colored(f"{url} - Success !", "green"))
            return
        print(colored(f"{url} - Failed !", "red"))


if __name__ == "__main__":
    pass
