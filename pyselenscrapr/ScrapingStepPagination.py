import random
import time
from typing import Callable

from pyselenscrapr.ScrapingLogic import ScrapingLogic
from pyselenscrapr.ScrapingStep import ScrapingStep, IScrapingStep


class ScrapingStepPaginationMode:
    RandomPages = 1
    AllPages = 2

class ScrapingStepPagination(ScrapingStep):
    def __init__(self, name: str,
                 execute: Callable[[IScrapingStep], any],
                 goto_page: Callable[[IScrapingStep, int], None],
                validate_page: Callable[[IScrapingStep, int], bool],
                 pagination_mode: ScrapingStepPaginationMode,
                 page_count: Callable[[IScrapingStep], int]):
        super().__init__(name, execute)
        self._executionList = []
        self._goto_page = goto_page
        self._pagination_mode = pagination_mode
        self._validate_page = validate_page
        self._page_count = page_count
        self._min_wait_time = 2
        self._max_wait_time = 10

    def _fill_all_pages(self):
        list = []
        # generate a list of random page numbers until _page_count_value
        for i in range(0, self._page_count_value+1):
            list.append(None)
        return list

    def finished(self):
        for i in self._executionList:
            if i is None:
                return False
        return True

    def _get_next_page(self):
        for i in range(1, len(self._executionList)):
            if self._pagination_mode == ScrapingStepPaginationMode.RandomPages:
                r = random.randint(1, len(self._executionList)-1)
                if self._executionList[r] is None:
                    return r
            else:
                if self._executionList[i] is None:
                    return i
        return None

    def _sleep(self, t):
        time.sleep(t)

    def sleep_random(self):
        t = random.randint(self._min_wait_time, self._max_wait_time)
        self._sleep(t)

    def execute(self, logic):
        self._page_count_value = self._page_count(logic)
        self._executionList = self._fill_all_pages()

        while not self.finished():
            next_page = self._get_next_page()
            self.log("Scraping page " + str(next_page) + " of " + str(self._page_count_value) + " pages")
            self.log("Pages left: " + str(len([x for x in self._executionList if x is None])))

            if next_page is None:
                break

            l = ScrapingLogic(logic._driver, logic._bot)
            for i in range(0, 3):
                try:
                    self._goto_page(l, next_page)
                    l.sleep(1)
                    if self._validate_page(l, next_page):
                        break
                except Exception as e:
                    print(e)
                    l.sleep(1)

            try:
                l = ScrapingLogic(logic._driver, logic._bot)
                self._execute(l)
                l.take_screenshot(self)
                l.sleep(1)
            except Exception as e:
                print(e)

            self._executionList[next_page] = True
            self.sleep_random()





