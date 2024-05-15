PySelenScrapr
=============

Here is a sample code for a good scraper logic with some validation
logic. It helps to build a good scraper with validation steps and repeat
logic.

Installation
------------

.. code:: bash

    pip install pyselenscrapr


Usage
-----

.. code:: python

    from pyselenscraper.ScrapingBot import ScrapingBot, TakeScreenshotModes
    from pyselenscraper.ScrapingLogic import ScrapingLogic
    from pyselenscraper.ScrapingStep import ScrapingStep, ScrapingStepInterval, ScrapingStepErrorHandling

    ...
    # Initialize selenium driver
    driver = webdriver.Remote("http://localhost:4444/wd/hub", options=ff_options)
    ...

    robot = ScrapingBot(driver, take_screenshots_mode=TakeScreenshotModes.Always)

    try:

       search_command = "wikipedia matrix movies"

       robot.add_step(ScrapingStep("Check if there is a visible 'Accept all' or 'decline all' button",
                                   lambda l: l.get_best_element("//button//div[contains(text(), 'All')]").click(),
                                   interval=ScrapingStepInterval.BeforeAnyStep,
                                   error_handling=ScrapingStepErrorHandling.Ignore,
                                   can_execute=lambda l: l.current_url and "google" in l.current_url and l.is_visible("//button//div[contains(text(), 'All')]"),
                                   was_executed=lambda l: not l.is_visible("//button//div[contains(text(), 'All')]"),),
                      step_group="default")

       ...
       # Your scraper Logic here
       ...

       finished_success = robot.run()

       if finished_success:
           print("The robot finished successfully")
       else:
           print("The robot did not finish successfully")

    except Exception as e:
       log.error(e)
    finally:
       driver.quit()


Documentation
~~~~~~~~~~~~~

The documentation is available at https://pyselenscrapr.readthedocs.io/.

License
-------

This project is licensed under the MIT License - see the
`LICENSE.md <LICENSE.md>`__ file for details