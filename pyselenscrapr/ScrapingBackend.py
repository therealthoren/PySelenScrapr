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
        requests.post(self._data_route, json=data)

    def errorHandling(self, error: Exception):
        requests.post(self._error_route, json={"error": str(error)})

    def notify(self, message: str):
        requests.post(self._notify_route, json={"message": message})