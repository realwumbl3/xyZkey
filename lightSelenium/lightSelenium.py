import os
import json
import sys
from pathlib import Path
from threading import Thread

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service as ChromeService

from subprocess import CREATE_NO_WINDOW

import time
import logging

LOG_FORMAT = "%(filename)s - %(lineno)d - %(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename="log.log", level=logging.INFO, format=LOG_FORMAT, filemode="a+")


class lightSelenium:
    def __init__(self, browser_executable, chrome_version):

        self.options = Options()
        self.options.add_argument(f"user-data-dir=.\\profiles\\artDeck\\")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--disk-cache-size=0")

        self.lightSeleniumPath = __file__.split("\\lightSelenium.py")[0]

        self.service = ChromeService(
            f"{self.lightSeleniumPath}\\chromedriver\\chromedriver{chrome_version}.exe"
        )

        self.service.creationflags = CREATE_NO_WINDOW

        self.options.binary_location = browser_executable

        self.browser = webdriver.Chrome(service=self.service, options=self.options)

    def __kill__(self):
        print("killing selenium?")
        self.browser.close()
        self.browser.quit()
        print("browser closed?")
        self.service.stop()
        print("killed selenium?")

    def refresh(self):
        self.browser.refresh()

    def seleniumJsExecute(self, action, dict_data=None):
        if not dict_data:
            dict_data = {}
        js_code = f"seleniumJsExecute('{action}',{json.dumps(dict_data)})"
        self.browser.execute_script(
            f"""try{{{js_code}}}catch(e){{console.error('Selenium JS execution.', e)}}"""
        )

    def JsExecute(self, function_code):
        self.browser.execute_script(
            f"""try{{{function_code}}}catch(e){{console.error('Selenium JS execution.', e)}}"""
        )
