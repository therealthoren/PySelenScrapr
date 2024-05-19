import json
import logging
from abc import ABC
import requests

# interface IScrapingBackend with the method "saveData" and "errorHandling" and "notify"
class IScrapingBackend(ABC):
    """
    This is a interface that represents a backend for the scraping process.
    """
    def saveData(self, data: dict, key: str = None):
        raise NotImplementedError

    def errorHandling(self, error: Exception):
        raise NotImplementedError

    def notify(self, message: str):
        pass


class ScrapingBackendWebhook(IScrapingBackend):
    """
    This class is used to send the data you scraped to a webhook.
    """
    _url = None
    def __init__(self, url, error_route="/error", notify_route="/notify", data_route="/data"):
        self._url = url
        self._error_route = url + error_route
        self._notify_route = url + notify_route
        self._data_route = url + data_route

    def saveData(self, data: dict, key: str = None):
        try:
            d = json.dumps(data)
            ret = requests.post(self._data_route, data=d, headers={"Content-Type": "application/json", "Accept": "application/json"})
            logging.debug("data return")
            logging.debug(ret.status_code)
            logging.debug(ret)
        except Exception as e:
            print(e)
            raise e

    def errorHandling(self, error: Exception):
        try:
            d = json.dumps({"error": str(error)})
            ret = requests.post(self._error_route, data=d, headers={"Content-Type": "application/json", "Accept": "application/json"})
            logging.debug("data return")
            logging.debug(ret.status_code)
            logging.debug(ret)
        except Exception as e:
            print(e)
            raise e

    def notify(self, message: str):
        try:
            d = json.dumps({"message": str(message)})
            ret = requests.post(self._notify_route, data=d, headers={"Content-Type": "application/json", "Accept": "application/json"})
            logging.debug("data return")
            logging.debug(ret.status_code)
            logging.debug(ret)
        except Exception as e:
            print(e)
            raise e