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


class seleniumOverlay:
    def __init__(self):

        self.options = Options()
        self.options.add_argument(f"user-data-dir=.\\profiles\\artDeck\\")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--disk-cache-size=0")

        self.module_path = __file__.split("\\seleniumOverlay.py")[0]

        self.service = ChromeService(f"{self.module_path}\\chromedriver\\chromedriver102.exe")

        self.service.creationflags = CREATE_NO_WINDOW

        self.options.binary_location = f"{self.module_path}\\electron\\release-builds\\electron-client-win32-ia32\\electron-client.exe"

        self.browser = webdriver.Chrome(service=self.service, options=self.options)

    def __kill__(self):
        self.service.stop()
        self.browser.close()
        self.browser.quit()

    def go(self, url):
        self.browser.get(url)

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
