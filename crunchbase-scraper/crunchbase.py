import os
import sys
import csv
import time
import json
import json
import random
import logging
import pathlib
import requests
import traceback
from pathlib import Path
import concurrent.futures
import concurrent.futures
from base64 import b64decode
from urllib.parse import unquote

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import setup_logging

setup_logging()

ZYTE_API_KEY = os.environ.get("ZYTE_API_KEY")
CRUNCHBASE_KEY = os.environ.get("CRUNCHBASE_KEY")

# region DECORATORS
def retry_on_failure(func):
    def wrapper(*args, **kwargs):
        MAX_ATTEMPTS = 5
        attempts = MAX_ATTEMPTS
        while attempts > 0:
            try:
                response = func(*args, **kwargs)
                if response.status_code == 200:
                    return response
                else:
                    logging.error(f"Request failed with status code {response.status_code}.")
                    logging.error(
                        f"Retrying {MAX_ATTEMPTS - attempts + 1}/{MAX_ATTEMPTS} attempts."
                    )
                    attempts -= 1
                    time.sleep(10)
            except Exception as e:
                logging.error(
                    f"An error occurred - Exception: {e}. Retrying {MAX_ATTEMPTS - attempts + 1}/{MAX_ATTEMPTS} attempts."
                )
                attempts -= 1
                time.sleep(10)
        logging.warning(f"All attempts failed. Unable to make successful request.")
        return None
    return wrapper
# endregion


class Crunchbase:
    def __init__(self) -> None:
        logging.info("CRUNCHBASE SCRIPT...")
        self.CLIENT = None

    def make_session(self, headers=None):
        s = requests.Session()
        if headers is not None:
            s.headers.update(headers)

        return s

    @retry_on_failure
    def make_request(self, url, method="GET", data=None, auth=None):
        logging.info(f"Requesting URL: {url}")
        res = None
        if method == "GET":
            res = self.CLIENT.get(url, timeout=60)
        elif (method == "POST") and (data is not None) and (auth is None):
            res = self.CLIENT.post(url, json=data, timeout=120)
        elif (method == "POST") and (data is not None) and (auth is not None):
            res = self.CLIENT.post(url, json=data, auth=auth, timeout=120)
        return res

    def fetch_cookies(self):
        logging.info("Fetching cookies....")
        url = "https://www.crunchbase.com"
        payload = {"url": url, "browserHtml": True, "responseCookies": True, }
        
        api_response = self.make_request(url = "https://api.zyte.com/v1/extract", method = "POST", data = payload, auth = (ZYTE_API_KEY, ""))

        cookies = ''

        if api_response:
            logging.info(f"Cookies response : {api_response}")
            cookies = api_response.json()["responseCookies"]

        else:
            logging.error("Something went wrong while fetching cookies.")

        return cookies

    def getCompany(self, company_name: str, isPerson=False):

        self.CLIENT = self.make_session()
        logging.info(f"Calling getCompany for company name : {company_name}")

        if company_name == "":
            return None
        
        url = (
            self.__genURLPeople(company_name)
            if isPerson
            else self.__genURL(company_name)
        )

        cookies = self.fetch_cookies()
        response = self.__requestZyteAPI(url, cookies)

        if response is None:
            logging.info("There is something wrong with getCompany, trying again ...")
            cookies = self.fetch_cookies()
            response = self.__requestZyteAPI(url, cookies)

        return response

    def get_company_details(self, company_name: str, isPerson=False) -> dict:
        company_json = self.getCompany(company_name, isPerson)
        if company_json == None:
            return None
        return company_json  # Return only the dictionary

    def get_investor_details(self, company_name: str, isPerson=False) -> dict:
        company_json = self.getCompany(company_name, isPerson)
        if company_json == None:
            return None
        return company_json

    def getCrunchbaseIDs(self, company_names):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.getCrunchbaseID, name) for name in company_names
            }
            results = {}
            for future in concurrent.futures.as_completed(futures):
                name, result = future.result()
                results[name] = result
            return results

    def getCrunchbaseID(self, company_name: str) -> str:

        max_retries = 5  # Maximum number of retries
        backoff_factor = 2  # Factor by which the delay increases
        initial_delay = 5  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                # Set API endpoint URL
                endpoint_url = "https://api.crunchbase.com/api/v4/autocompletes"

                # Set API request parameters
                params = {
                    "query": company_name,
                    "entity_def_ids": "organization",
                    "collection_ids": "organizations,categories",
                }

                # Set API request headers with the API key
                headers = {"X-cb-user-key": f"{CRUNCHBASE_KEY}"}

                # Make API GET request with headers and params
                
                response = requests.get(endpoint_url, params=params, headers=headers)
                time.sleep(initial_delay)
                response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX

                # Extract entity ID from response
                entity_id = response.json()["entities"][0]["identifier"]["uuid"]
                return company_name, (
                    entity_id,
                    False,
                )  # Assuming all entities are organizations for simplicity

            except Exception as e:
                logging.error(f"Error while fetching Crunchbase ID, {e}")
                
                if e.response.status_code == 429:
                    delay = initial_delay * (backoff_factor ** attempt)

                    logging.info(
                        f"Rate limit exceeded. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)

        # Log the error if all retries fail
        with open("error-logs.txt", "a") as error_file:
            error_file.write(
                f"Error in getCrunchbaseID for {company_name}: Exceeded maximum retries\n"
            )

        return company_name, ("", False)

    def __genURL(self, company_name: str) -> str:
        return f'http://www.crunchbase.com/v4/data/entities/organizations/{company_name}?field_ids=["identifier","layout_id","facet_ids","title","short_description","is_locked"]&layout_mode=view_v2'

    def __genURLPeople(self, company_name: str) -> str:
        return f'http://www.crunchbase.com/v4/data/entities/people/{company_name}?field_ids=["identifier","layout_id","facet_ids","title","short_description","is_locked"]&layout_mode=view_v2'

    def __requestZyteAPI(self, url: str, cookies: dict) -> dict:
        
        session_context = [
                            {
                                "name": "id",
                                "value": "fetch_content",
                            },
                        ]
        
        session_context_parameters = {
                                        "actions": [
                                            {
                                                "action": "waitForSelector",
                                                "selector": {
                                                    "type": "css",
                                                    "value": "body",
                                                },
                                            },
                                        ],
                                    }
        
        payload = {"url": url, "requestCookies": cookies, "httpResponseBody": True, 
                   "sessionContext": session_context,
                    "sessionContextParameters": session_context_parameters,
                    }

        api_response = self.make_request(url = "https://api.zyte.com/v1/extract", method = "POST", data= payload, auth = (ZYTE_API_KEY, ""))

        if api_response:
            status = api_response.status_code
        
        else:
            # Log the error if all retries fail
            with open("error-logs.txt", "a") as error_file:
                error_file.write(
                    f"Error in __requestZyteAPI for {url}:"
                )

            return None
        
        http_response_body: bytes = b64decode(api_response.json()["httpResponseBody"])

        return json.loads(http_response_body)

    def __extractRelevantInfo(self, json: dict) -> dict:
        newJSON = {}

        fields = [
            "identifier",
            "short_description",
            "long_description",
            "funding_overview",
            "funding_rounds",
            "investors",
            "website",
            "linkedin",
            "twitter",
            "facebook",
            "more_info",
        ]
        
        for field in fields:
            try:
                newJSON[field] = (
                    json["properties"][field]
                    if field in json["properties"]
                    else json["cards"][field]
                )
            except:
                pass
        return newJSON

    def __extractCrunchbaseID(self, search_results: list, company_name: str) -> tuple:
        for a in search_results:
            if a.url.startswith("https://www.crunchbase.com/organization/"):
                u = a.url[len("https://www.crunchbase.com/organization/") :]
                return (unquote(u[: u.find("/") if u.find("/") > 0 else len(u)]), False)
            elif a.url.startswith("https://www.crunchbase.com/person/"):
                u = a.url[len("https://www.crunchbase.com/person/") :]
                return (unquote(u[: u.find("/") if u.find("/") > 0 else len(u)]), True)
        logging.info(f"Cannot find {company_name} in Crunchbase.")
        with open("crunchbase_not_found.txt", "a") as f:
            f.write(f"{company_name}\n")
        return ("", False)

    