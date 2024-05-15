Usage
=====

.. _installation:

Installation
------------

To use pyselenscrapr, you need to install it first.

.. code-block:: console

   (.venv) $ pip install pyselenscrapr

Creating a Bot
----------------

To start a new bot, you need to create a new instance of the
:class:`pyselenscrapr.ScrapingBot` class. You pass the Selenium
driver to the constructor.

.. autofunction:: pyselenscrapr.ScrapingBot.ScrapingBot.run


For example:

.. code-block:: python

    from pyselenscrapr.ScrapingBot import ScrapingBot, TakeScreenshotModes

    bot = ScrapingBot(driver)

    ... Add your steps here ...

    bot.run()

    bot.get_data('your_saved_data')
