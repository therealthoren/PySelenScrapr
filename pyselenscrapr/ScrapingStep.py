from typing import Callable

from pyselenscrapr import ScrapingLogic

class ScrapingStepErrorHandling:
    ThrowException = 0
    RetryAndThrowException = 1
    Ignore = 2

#ScrapintStepInterval is an enum
class ScrapingStepInterval:
    Order = 0
    BeforeAnyStep = 1
    AfterAnyStep = 2
    BeforeValidation = 3
    AfterValidation = 4
    BeforeRetry = 5
    AfterRetry = 6
    BeforePagination = 7
    AfterPagination = 8

class ScrapingStepRepeat:
    Repeat = 0
    NoRepeat = 1

# interface IScrapingStep
class IScrapingStep:
    def __init__(self):
        pass

class ScrapingStep(IScrapingStep):
    """
    ScrapingStep is a class that represents a single step in a scraping process.
    """
    childGroups = []
    _hasExecuted = False
    _previous_step = None
    _interval = ScrapingStepInterval.Order
    robot = None
    _repeat = ScrapingStepRepeat.NoRepeat
    _error_handling = ScrapingStepErrorHandling.RetryAndThrowException

    def __init__(self, name: str,
                 execute: Callable[[ScrapingLogic], None],
                 can_execute: Callable[[ScrapingLogic], bool] = None,
                 was_executed: Callable[[ScrapingLogic], bool] = None,
                 before_validation: Callable[[ScrapingLogic], None] = None,
                 retry: Callable[[ScrapingLogic], None] = None,
                 previous_step: IScrapingStep = None,
                 error_handling: ScrapingStepErrorHandling = ScrapingStepErrorHandling.RetryAndThrowException,
                 interval: ScrapingStepInterval = ScrapingStepInterval.Order,
                 repeat: ScrapingStepRepeat = ScrapingStepRepeat.NoRepeat,
                 retry_count: int = 3):
        """
        Constructor for ScrapingStep

        :param name: a string representing the name of the step - it is used later for debugging purposes
        :param execute: a function that will be executed when the step is executed
        :param can_execute: a function that will be executed to check if the step can be executed
        :param was_executed: a function that will be executed to check if the step was executed
        :param before_validation: a function that will be executed before the step is validated
        :param retry: a function that will be executed if the step fails
        :param previous_step: the previous step in the scraping process
        :param error_handling: an enum representing the error handling strategy
        :param interval: an enum representing the interval at which the step will be executed
        :param repeat: an enum representing if the step should be repeated
        :param retry_count: an integer representing the number of retries
        """
        self._name = name
        self._error_handling = error_handling
        self._repeat = repeat
        self.can_execute = can_execute
        self._previous_step = previous_step
        self._interval = interval
        self._execute = execute
        self._was_executed = was_executed
        self.before_validation = before_validation
        self.retry = retry
        self.retry_count = retry_count

    def __str__(self):
        return self._name + " " + str(self._interval) + " " + str(self._repeat)


    def name(self) -> str:
        return self._name

    def interval(self) -> ScrapingStepInterval:
        return self._interval

    def next_step(self, step):
        if self.robot is not None:
            step.set_previous_step(self)
            self.robot.add_step(step)
        else:
            raise Exception("The robot is not set")
        return step

    def set_previous_step(self, step):
        self._previous_step = step

    def add_child_group(self, group):
        self.childGroups.append(group)

    def previous_step(self) -> IScrapingStep:
        return self._previous_step

    def can_execute(self) -> bool:
        pass

    def was_executed(self) -> bool:
        return self._hasExecuted

    def execute(self, logic):
        retData = self._execute(logic)
        return retData

    def set_executed(self):
        self._hasExecuted = True

    def before_validation(self):
        pass

    def retry(self):
        pass

    def reset(self):
        self._hasExecuted = False

    def log(self, message):
        if self.robot is not None:
            self.robot._on_debug(message)

    def is_executed(self, logic):
        if self._was_executed is not None:
            return self._was_executed(logic)
        return True

    def error_handling(self) -> ScrapingStepErrorHandling:
        return self._error_handling

class ScrapingStepConditional(ScrapingStep):
    pass

