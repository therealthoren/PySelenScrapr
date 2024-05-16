import time

import pandas as pd
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def tocontainer(func, bot):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return ScrapingLogic(result, bot)
    return wrapper

class ScrapingLogic(object):
    """
    ScraipingLogic is a class that is the main interface between the bot and the selenium driver.
    It contains a lot of helper functions that make it easier to interact with the driver.

    You can use all driver functions and also the functions in this class.
    """
    def __init__(self, driver, bot):
        """
        Constructor for ScrapingLogic. Will be called from the bot.

        :param driver: the selenium driver
        :param bot: the bot that is using the driver
        """
        self._driver = driver
        self._bot = bot

    def __getitem__(self, item):
        result = self._driver[item]
        if isinstance(result, type(self._driver)):
            result = ScrapingLogic(result)
        return result

    def __getattr__(self, item):
        result = getattr(self._driver, item)
        if callable(result):
            result = tocontainer(result, self._bot)
        return result

    def __repr__(self):
        return repr(self._driver)

    def sleep(self, seconds):
        """
        Sleep for a given amount of seconds.
        :param seconds:  the amount of seconds to sleep
        :return:  None
        """
        time.sleep(seconds)

    def replace_input_text(self, selector, keys):
        """
        If you have an input field and you want to replace the text in it, you can use this function.. It will first
        scroll to the element, then select all text in the input field and then send the new keys to the input field.

        :param selector: CSS or XPATH selector
        :param keys:  the new text that should be in the input field
        :return: True if the operation was successful, False otherwise
        """
        e = self.get_best_element(selector)
        if e is not None:
            try:
                self.scroll_to_element_by_js(e)
                self.sleep(1)
                e.send_keys(Keys.LEFT_CONTROL + "a")
                e.send_keys(keys)
            except Exception as e:
                pass
            return True
        return False

    def clear_input_text(self, selector):
        """
        If you have an input field and you want to clear the text in it, you can use this function. It will first
        scroll to the element, then select all text in the input field and then send the DELETE key to the input field.

        :param selector:  CSS or XPATH selector
        :return:  True if the operation was successful, False otherwise
        """
        e = self.get_best_element(selector)
        if e is not None:
            try:
                self.scroll_to_element_by_js(e)
                self.sleep(1)
                e.clear()
            except Exception as e:
                pass

            try:
                self.sleep(1)
                self.scroll_to_element_by_js(e)
                self.sleep(1)
                e.focus()
                e.send_keys(Keys.Control + "a")
                e.send_keys(Keys.DELETE)
                e.blur()
            except:
                pass
            return True
        return False

    def send_keys_to_element(self, selector, keys):
        """
        Send keys to an element. This function will send the keys to a CSS or XPATH element.

        :param selector:  CSS or XPATH selector
        :param keys: the keys that should be sent to the element
        :return: True if the operation was successful, False otherwise
        """
        e = self.get_best_element(selector)

        if e is not None:
            e.send_keys(keys)
            return True
        return False


    def is_visible(self, selector):
        e = self.get_best_element(selector)
        if e is None:
            return False
        displayed = e.is_displayed()
        return displayed

    def set_data(self, key, value, send_to_backend=False):
        self._bot.set_data(key, value, send_to_backend=send_to_backend)

    def take_screenshot(self, step):
        try:
            self._bot._take_screenshot(step)
        except Exception as e:
            pass

    def append_data(self, key, value, send_to_backend=False):
        self._bot.append_data(key, value, send_to_backend=send_to_backend)

    def send_data_to_backend(self, key=None, data=None):
        return self._bot.send_data_to_backend(key, data)

    def has_data(self, key):
        return self._bot.has_data(key)

    def get_data(self, key):
        return self._bot.get_data(key)

    def notify(self, message):
        self._bot.backend_notify(message)

    def convert_table_to_df(self, t):
        df = pd.read_html(t.get_attribute("outerHTML"))
        if len(df) > 0:
            df = df[0]
        return df

    def get_number_of_content(self, selector):

        try:
            e = self.get_best_element(selector)
            if e is not None:
                return int(e.get_attribute("innerText"))
        except:
            pass
        return None

    def convert_tables_to_df(self, tables):
        dfs = []
        for table in tables:
            df = self.convert_table_to_df(table)
            dfs.append(df)
        if len(dfs) <= 0:
            return None
        if len(dfs) == 1:
            return dfs[0]
        return dfs

    def get_all_elements(self, selector):
        by = By.CSS_SELECTOR
        if selector.startswith("//"):
            by = By.XPATH
        try:
            e = self._driver.find_elements(by, selector)
            return e
        except:
            pass
        return []

    def wait_for_reload(self, timeout=40, min_wait=0.1):
        was_incomplete = False
        # set a windows javascript variable to true if the page is still loading
        self._driver.execute_script("window._incomplete_data = true")
        for i in range(int(timeout/min_wait)):
            time.sleep(min_wait)
            # check if the variable is still true
            was_incomplete = self._driver.execute_script("return window._incomplete_data")
            # if the page is not loading anymore, return
            if not was_incomplete:
                # when document readystate
                if self._driver.execute_script("return document.readyState") == "complete":
                    return True
        return False

    def get_best_element(self, selector):
        by = By.CSS_SELECTOR
        if selector.startswith("//"):
            by = By.XPATH
        try:
            e = self._driver.find_element(by, selector)
            return e
        except:
            pass
        return None

    def element_count(self, selector):
        by = By.CSS_SELECTOR
        if selector.startswith("//"):
            by = By.XPATH
        try:
            e = self._driver.find_elements(by, selector)
            return len(e)
        except:
            return 0

    def element_text(self, selector):
        """
        Get the text of an element. This function will return the text of the element if it is available.

        :param selector: CSS or XPATH selector
        :return:  the text of the element
        """
        def get_best_match( elements):
            """
            Get the best match from a list of elements. This function will return the longest element from the list.

            :param elements:  a list of elements
            :return:  the longest element
            """
            longest = ""
            for e in elements:
                if len(e) > len(longest):
                    longest = e
            return longest
        by = By.CSS_SELECTOR
        if selector.startswith("//"):
            by = By.XPATH

        e = self._driver.find_element(by, selector)
        if e is not None:
            elements = []

            if e.text is not None:
                elements.append(e.text)
            if e.get_attribute("data-value") is not None:
                elements.append(e.get_attribute("data-value"))
            if e.get_attribute("value") is not None:
                elements.append(e.get_attribute("value"))
            if e.get_attribute("innerHTML") is not None:
                elements.append(e.get_attribute("innerHTML"))
            if e.get_attribute("innerText") is not None:
                elements.append(e.get_attribute("innerText"))
            if e.get_attribute("textContent") is not None:
                elements.append(e.get_attribute("textContent"))
            if len(elements) > 0:
                return get_best_match(elements)
        return None

    def wait_until_present(self, selector, timeout=20):
        """
        Wait until an element is present. This function will wait until an element is present in the DOM.

        :param selector:  CSS or XPATH selector
        :param timeout: the timeout in seconds
        :return: True if the element is present, False otherwise
        """
        if isinstance(selector, str):
            e = self.get_best_element(selector)
        else:
            e = selector
        if e is not None:
            try:
                wait = WebDriverWait(self._driver, timeout)
                wait.until(EC.presence_of_element_located(e))
                return True
            except:
                pass
        return False

    def wait_until_clickable(self, selector, timeout=10):
        if isinstance(selector, str):
            e = self.get_best_element(selector)
        else:
            e = selector
        if e is not None:
            try:
                wait = WebDriverWait(self._driver, timeout)
                wait.until(EC.element_to_be_clickable(e))
                return True
            except:
                pass

        return False

    def element_exists(self, selector):
        try:
            e = self.get_all_elements(selector)
            if e is not None:
                if len(e) > 0:
                    return True
        except:
            return False
        return False

    def set_attribute(self, selector, attribute, value):
        if isinstance(selector, str):
            e = self.get_best_element(selector)
        else:
            e = selector
        if e is not None:
            e.set_attribute(attribute, value)
            return True
        return False

    def scroll_to_element(self, selector):
        if isinstance(selector, str):
            e = self.get_best_element(selector)
        else:
            e = selector
        if e is not None:
            self._driver.execute_script("arguments[0].scrollIntoView();", e)
            return True
        return False

    def click_on_element_by_xpath_with_jquery(self, xpath):
        self._driver.execute_script(
            "$(document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue)[0].click();",
            xpath)

    def inner_text_contains(self, selector, text):
        b = self.get_best_element(selector)
        if b is not None:
            innerTExt = b.get_attribute("innerText")
            if innerTExt is not None:
                return innerTExt.find(text) >= 0
        return False

    def click_on_best_element(self, selector):
        e = self.get_best_element(selector)
        if e is not None:
            e.click()
            return True
        return False

    def click_by_jquery_on_node(self, parent_button):
        if isinstance(parent_button, str):
            parent_button = self.get_best_element(parent_button)
        self._driver.execute_script("$(arguments[0]).click();", parent_button)
        return True

    def scroll_to_element_by_js(self, object):
        if isinstance(object, str):
            object = self.get_best_element(object)
        self._driver.execute_script(
            "window.scrollTo(arguments[0].getBoundingClientRect().left, arguments[0].getBoundingClientRect().top - (window.innerHeight/2) + document.documentElement.scrollTop);",
            object)
        return True