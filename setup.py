"""Setup script for pyselenscraper."""
import os.path
from setuptools import setup
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.rst")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="pyselenscrapr",
    version="0.0.1",
    description="Create your scraping bot with Selenium and Python.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/donnercody/PySelenScrapr",
    author="donnercody86",
    author_email="donnercody86@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(include=('pyselenscrapr*',)),
    include_package_data=True,
    install_requires=[
        "selenium",
        "pandas",
        "numpy",
        "beautifulsoup4",
        "requests",
    ],
    entry_points={"console_scripts": ["pyselenscrapr=index:main"]},
)
