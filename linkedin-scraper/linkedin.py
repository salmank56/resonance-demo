import re
import os
import sys
import json
import logging
import requests
from bs4 import BeautifulSoup
from termcolor import colored
from googlesearch import search
from urllib.parse import unquote

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")
ZYTE_PROXY_KEY = os.getenv("ZYTE_PROXY_KEY")

class Linkedin:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        
    def get_linkedin_id(self, cname):
        s = search(
            f"{cname} linkedin",
            num_results=3,
            advanced=True,
            proxy=f"http://{ZYTE_PROXY_KEY}:@proxy.crawlera.com:8011/",
            timeout=5,
        )
        for a in s:
            if "linkedin.com/company" in a.url:
                return a.url
        raise Exception("Company not found on linkedin")

    def get_info(self, url):
        response = requests.get(url, headers=self.headers)
        website_url = None

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            img_tag = soup.find("img", {"class": re.compile("^datalet-bpr-guid")})
            if img_tag:
                match = re.search(r'"url":"(http[^"]*)"', str(img_tag))
                if match:
                    website_url = match.group(1)
            info_script = soup.find("script", {"type": "application/ld+json"})
            if info_script:
                info = info_script.string
                return website_url + info if website_url else info

        raise Exception("Failed to retrieve information from LinkedIn")


def process_company(company_name, linkedin_url, folder_name):
    logging.info(f"Processing {company_name} - {linkedin_url}")
    linkedin = Linkedin()
    try:
        info = json.loads(linkedin.get_info(linkedin_url))
        # Determine the file path based on the folder_name
        if folder_name == "investors":
            file_path = f"linkedin_scrapes/investors/{company_name}.json"
        else:
            file_path = f"linkedin_scrapes/company/{company_name}.json"
        with open(file_path, "w") as outfile:
            json.dump(info, outfile)
        print(colored(f"Scrapped {company_name} - {linkedin_url}", "green"))
    except Exception as e:
        print(
            colored(
                f"Error processing {company_name} - {linkedin_url}: {str(e)}", "red"
            )
        )
