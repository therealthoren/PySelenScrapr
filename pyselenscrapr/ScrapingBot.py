import logging as log
import time
from typing import Callable

import numpy as np
import pandas as pd
from typing import Union
from pyselenscrapr.ScrapingBackend import IScrapingBackend
from pyselenscrapr.ScrapingLogic import ScrapingLogic
from pyselenscrapr.ScrapingStep import ScrapingStep, ScrapingStepInterval, ScrapingStepErrorHandling
from pyselenscrapr.ScrapingStepGroup import ScrapingStepGroup

class TakeScreenshotModes:
    """
    This enum is used to define when the bot should take a screenshot of the current page.
    """
    OnError = 2 # take a screenshot when an error occurs
    Always = 1 # take a screenshot for each step
    Never = 0 # never take a screenshot


class ScrapingBot:
    """

    The ScrapingBot class is the main class to be used for creating a scraping bot. It is used to define the steps and
    groups of steps that the bot should execute. The bot can be run by calling the run() method.

    """
    _data = {}
    _driver = None
    _warning_handler = None
    _current_group = None
    _exception_handler = None
    _take_screenshot_on_error = None
    _retry_count = 0
    _repeat_count_till_error = 5
    _repeat_count = 0
    _stepGroups = []
    _max_retries = 3
    _take_screenshots_mode = TakeScreenshotModes.Never
    _screenshot_path = "."
    _backend : IScrapingBackend = None

    def __init__(self, driver, max_retries=3,
                 take_screenshots_mode=TakeScreenshotModes.Never,
                 backend : IScrapingBackend = None,
                 repeat_count_till_error=5):
        self._repeat_count_till_error = repeat_count_till_error
        self._driver = driver
        self._backend = backend
        self._max_retries = max_retries
        self._take_screenshots_mode = take_screenshots_mode

    def _on_warning(self, w):
        if self._warning_handler is not None:
            self._warning_handler(w)
        else:
            log.warning(w)

    def group_name(self):
        return self._current_group.name

    def backend_notify(self, message):
        if self._backend is not None:
            self._backend.notify(message)

    def _take_screenshot(self, step):
        try:
            self._driver.save_screenshot(self._screenshot_path+self.group_name()+"_"+step.name()+".png")
        except:
            pass

    def _on_exception(self, e, step):
        if self._take_screenshots_mode == TakeScreenshotModes.OnError or \
                self._take_screenshots_mode == TakeScreenshotModes.Always:
            self._take_screenshot(step)
        if self._exception_handler is not None:
            self._exception_handler(e)
        else:
            log.error(e)
        if self._backend is not None:
            self._backend.errorHandling(e)

    def set_warning_handler(self, param):
        self._warning_handler = param

    def set_exception_handler(self, param):
        self._exception_handler = param

    def take_screenshot_on_error(self, path):
        self._take_screenshot_on_error = path

    def add_step_group(self, group_name: str):
        group = ScrapingStepGroup(group_name)
        self._stepGroups.append(group)
        return group


    def add_step(self, step_or_callback: ScrapingStep,
                 step_group: ScrapingStepGroup = None,
                 before_validation: Callable[[ScrapingLogic], None]  = None,
                 after_validation: Callable[[ScrapingLogic], None]  = None) -> ScrapingStep:
        group = None
        if isinstance(step_or_callback, ScrapingStep):
            step_or_callback.before_validation = before_validation
            step_or_callback.after_validation = after_validation
        step_or_callback.robot = self

        if step_group is None:
            step_group = "default"
        if step_group is not None and isinstance(step_group, str):
            if len(self._stepGroups) > 0:
                group = next((x for x in self._stepGroups if x.name == step_group), None)
        elif step_group is not None and isinstance(step_group, ScrapingStepGroup):
            group = step_group


        if group is None:
            group = ScrapingStepGroup("default")
            self._stepGroups.append(group)

        group.add_step(step_or_callback)

        return step_or_callback

    def _run_step(self, step, retryInterval=0):
        try:
            if step.can_execute is not None and not step.can_execute(ScrapingLogic(self._driver, self)):
                return
        except Exception as e:
            if step.error_handling() != ScrapingStepErrorHandling.Ignore:
                self._on_exception(e, step)

        try:
            if step.previous_step() is not None and not step.previous_step().was_executed():
                return
        except Exception as e:
            if step.error_handling() != ScrapingStepErrorHandling.Ignore:
                self._on_exception(e, step)

        if step.before_validation is not None:
            try:
                step.before_validation()
            except Exception as e:
                if step.error_handling() != ScrapingStepErrorHandling.Ignore:
                    self._on_exception(e, step)
                else:
                    self._on_warning(e)

        for i in range(self._max_retries):
            try:
                l = ScrapingLogic(self._driver, self)
                step.execute(l)
                if step.is_executed(l):
                    step.set_executed()
                break
            except Exception as e:
                if step.error_handling() != ScrapingStepErrorHandling.Ignore:
                    self._on_exception(e, step)
                else:
                    self._on_warning(e)
                step.retry()


        if step.after_validation is not None:
            step.after_validation()

    def sleep(self, seconds):
        time.sleep(seconds)

    def _on_debug(self, msg, *args):
        msg = msg+" ".join([str(x) for x in args])
        log.debug(msg)

    def all_groups_executed(self):
        for group in self._stepGroups:
            for step in group._steps:
                if not step.was_executed():
                    return False
        return True

    def get_next_step(self, step):
        for s in self._current_group._steps:
            if s.interval() != ScrapingStepInterval.Order:
                continue
            if s.was_executed():
                continue
            if s.previous_step() is None:
                return s
            if s.previous_step().was_executed():
                return s


        return None

    def set_current_group(self, group):
        self._current_group = group

    def finished(self):
        return self.all_groups_executed()

    def get_all_steps_by_interval(self, interval):
        steps = []
        for step in self._current_group._steps:
            if step.interval() == interval and not step.was_executed():
                steps.append(step)
        return steps

    def _run_before_step(self, step):
        steps = self.get_all_steps_by_interval(ScrapingStepInterval.BeforeAnyStep)
        for s in steps:
            self._run_step(s)

    def get_next_group(self):
        for i, group in enumerate(self._stepGroups):
            if group == self._current_group:
                if i+1 < len(self._stepGroups):
                    return self._stepGroups[i+1]
        return None

    def _run_after_step(self, step):
        if self._take_screenshots_mode == TakeScreenshotModes.Always:
            self._take_screenshot(step)
        steps = self.get_all_steps_by_interval(ScrapingStepInterval.AfterAnyStep)
        for s in steps:
            self._run_step(s)

    def _run_after_group(self, group):
        pass

    def _is_group_finished(self, group):
        for step in group._steps:
            if not step.was_executed():
                return False
        return True

    def run(self, first_group: Union[str , ScrapingStepGroup]  = None):
        """
        Run the bot and execute all steps in the defined groups.

        :param first_group: This is the name of the first group to start. If it is None we use "default" as the first group.
        :return: True if the bot finished successfully, False otherwise.
        """
        if first_group is None:
            first_group = "default"
        if first_group is not None and isinstance(first_group, str):
            if len(self._stepGroups) > 0:
                group = next((x for x in self._stepGroups if x.name == first_group), None)
        elif first_group is not None and isinstance(first_group, ScrapingStepGroup):
            group = first_group

        if group is None:
            raise Exception("Group not found - please enter a valid group name or object to start the execution from.")
        self.set_current_group(group)
        next_step = None
        while not self.finished():
            last_step = next_step

            if self._repeat_count > self._repeat_count_till_error:
                self._on_exception("The same step was repeated too many times", last_step)
                return False

            while not self._is_group_finished(self._current_group):
                next_step = self.get_next_step(next_step)

                if next_step is None:
                    break

                if next_step == last_step:
                    self._repeat_count += 1
                else:
                    self._repeat_count = 0

                self._run_before_step(next_step)

                try:
                    self._on_debug("Running step: ", next_step.name())
                    self._run_step(next_step)
                except Exception as e:
                    self._on_debug("Exception: ", e)
                    if next_step.error_handling() != ScrapingStepErrorHandling.Ignore:
                        self._on_exception(e, next_step)

                self._run_after_step(next_step)

                self.sleep(3)
                self._on_debug("Finished step: ", next_step.name())

            self._run_after_group(self._current_group)

            self.sleep(1)
            self.set_current_group(self.get_next_group())

        self.sleep(1)
        return True

    ##############################################################################################################
    # Data handling
    ##############################################################################################################

    def get_converted_data(self, data):
        retdata = {}
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                retdata[key] = value.replace({np.nan:None}).to_dict(orient='records')
            else:
                retdata[key] = value

        return retdata

    def save_backend_data(self, data):
        try:
            if self._backend is not None:
                d_converted = self.get_converted_data(data)
                self._backend.saveData(d_converted)
        except Exception as e:
            self._on_warning(e)

    def send_error_to_backend(self, error):
        if self._backend is not None:
            self._backend.errorHandling(error)

    def send_data_to_backend(self, key=None, data=None):
        if data is None:
            data = self._data
        if key is not None:
            data = data[key]

        self.save_backend_data(data)

    def set_data(self, key, value, send_to_backend=False):
        self._data[key] = value
        if send_to_backend:
            self.save_backend_data({key: value})

    def append_data(self, key, value, send_to_backend=False):
        if key in self._data:
            # pandas dataframe
            if isinstance(self._data[key], pd.DataFrame):
                # append elements to the dataframe
                self._data[key] = self._data[key]._append(value, ignore_index=True)
            elif isinstance(self._data[key], list):
                self._data[key].append(value)
            elif isinstance(self._data[key], str):
                self._data[key] = [self._data[key], value]
            elif isinstance(self._data[key], int):
                self._data[key] = [self._data[key], value]
            elif isinstance(self._data[key], float):
                self._data[key] = [self._data[key], value]
            elif isinstance(self._data[key], dict):
                self._data[key] = [self._data[key], value]
            elif isinstance(self._data[key], tuple):
                self._data[key] = [self._data[key], value]
            elif isinstance(self._data[key], set):
                self._data[key] = [self._data[key], value]
            # pandas dataframe
            elif isinstance(self._data[key], pd.DataFrame):
                # append elements to the dataframe
                self._data[key] = self._data[key].append(value)
        else:
            self._data[key] = value

        if send_to_backend:
            self.save_backend_data({key: value})

    def has_data(self, key):
        if key in self._data:
            return True
        return False

    def get_data(self, key):
        if key in self._data:
            return self._data[key]
        return None
