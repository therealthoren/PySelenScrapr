import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from pyselenscrapr.ScrapingBot import ScrapingBot, TakeScreenshotModes
import logging as log

from pyselenscrapr.ScrapingLogic import ScrapingLogic
from pyselenscrapr.ScrapingStep import ScrapingStep, ScrapingStepInterval, ScrapingStepErrorHandling

ff_options = webdriver.FirefoxOptions()
ff_options.add_argument('--no-sandbox')
ff_options.add_argument("--lang=en-GB")
ff_options.add_argument('--disable-dev-shm-usage')

"""
# set proxy to firefox
ff_options.set_preference('network.proxy.type', 1)
ff_options.set_preference('network.proxy.socks', "localhost")
ff_options.set_preference('network.proxy.socks_port', 9050)
"""

driver = webdriver.Remote("http://localhost:4444/wd/hub", options=ff_options)

log.basicConfig(level=log.DEBUG)
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

    step1 = robot.add_step(ScrapingStep("Go to google.de and check if textarea is ready",
                                        lambda l: l.get("https://www.google.de"),
                                        was_executed=lambda l: l.element_exists("//textarea")),
                           step_group="default")

    step2 = step1.next_step(ScrapingStep("Send the search command to the textarea",
                                         lambda l: l.send_keys_to_element("//textarea", search_command),
                                            was_executed=lambda l: l.element_text("//textarea") == search_command)
)

    step3 = step2.next_step(ScrapingStep("Send the ENTER key to the textarea",
                                            lambda l: l.send_keys_to_element("//textarea", Keys.ENTER),
                                            was_executed=lambda l: l.element_count("//h3") > 3))


    step4 = step3.next_step(ScrapingStep("Click on the first search result",
                                            lambda l: l.get_best_element("//h3").click(),
                                            was_executed=lambda l: "google" not in l.current_url))

    step5 = step4.next_step(ScrapingStep("Extrac tall tables from the page",
                                            lambda l: l.set_data("tables", l.convert_tables_to_df(l.get_all_elements("//table"))),
                                            was_executed=lambda l: l.has_data("tables"))
                            )

    robot.set_warning_handler(lambda w: log.warning("Warning: ", w))
    robot.set_exception_handler(lambda e: log.error("Exception: ", e))

    finished_success = robot.run()

    if finished_success:
        print(robot.get_data("tables"))
    else:
        print("The robot did not finish successfully")

except Exception as e:
    log.error(e)
finally:
    driver.quit()