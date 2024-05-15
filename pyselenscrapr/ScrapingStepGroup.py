from pyselenscrapr.ScrapingStep import IScrapingStep


class ScrapingStepGroup:
    _steps : [IScrapingStep] = []
    name = None

    def __init__(self, name: str, steps: [IScrapingStep]=[]):
        self._steps = steps
        self.name = name

    def add_step(self, step):
        self._steps.append(step)
        step.group = self