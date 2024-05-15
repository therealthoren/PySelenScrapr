import time
from typing import Callable

from pyselenscrapr.ScrapingLogic import ScrapingLogic
from pyselenscrapr.ScrapingStep import ScrapingStep

class ScrapingLogicIterator(ScrapingLogic):
    def __init__(self, logic: ScrapingLogic, element, index):
        super().__init__(logic._driver, logic._bot)
        self._element = element
        self._index = index

    def index(self):
        return self._index

    def element(self):
        return self._element

class ScrapingStepIteration(ScrapingStep):
    pass



class ScrapingStepLoop(ScrapingStep):
    def __init__(self, name: str,
                 iteration_callback: Callable[[ScrapingLogic], any],
                 iteration_steps: list[ScrapingStep],
                 iterations: int =None,
                 retry_count: int = 3):
        super().__init__(name, lambda x: self.execute(x))
        self._iteration_callback = iteration_callback
        self._iteration_steps = iteration_steps
        self.current_iteration = 0

    def execute(self, logic: ScrapingLogic):
        self.elements = self._iteration_callback(logic)

        index = 0
        for element in self.elements:
            try:
                for step in self._iteration_steps:
                    l = ScrapingLogicIterator(logic, element, index)
                    step.execute(l)
                    time.sleep(2)
            except Exception as e:
                logic._on_exception(e, step)
            index += 1