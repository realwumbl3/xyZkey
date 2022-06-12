import os
import sys
from threading import Thread
from time import sleep
import json
import logging

LOG_FORMAT = "%(filename)s - %(lineno)d - %(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename="log.log", level=logging.INFO, format=LOG_FORMAT, filemode="a+")


from engine import xyZkey, keyboardKeys, KeyCode

from pynput.mouse import Controller as mouseController, Button as mouseButtons

############################################################################
"""

XyZkey.xKeyAdd("f13", keyboardKeys.f13)
XyZkey.xKeyAdd("f14", keyboardKeys.f14)
XyZkey.xKeyAdd("pause", keyboardKeys.pause)


@XyZkey.bind("modifier", modifier_key=keyboardKeys.pause, key=keyboardKeys.esc)
def _():
    XyZkey.consolelog("main.py: esc!")


@XyZkey.bind("combo", combo=[keyboardKeys.alt_l, keyboardKeys.delete])
def _():
    XyZkey.consolelog("main.py: combo!")


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="left")
def _():
    Mouse.click(mouseButtons.x1)
    XyZkey.consolelog("main.py: f13 + left gesture !")


@XyZkey.bind("onMove")
def _(x, y):
    print("onMove", x, y)

"""
############################################################################


XyZkey = xyZkey()

XyZkey.consolelog = lambda *x: ping_selenium(*x)

XyZkey.xKeyAdd("f13", keyboardKeys.f13)
XyZkey.xKeyAdd("pause", keyboardKeys.pause)

Mouse = mouseController()

VOL_UP = KeyCode.from_vk(0xAF)
VOL_DOWN = KeyCode.from_vk(0xAE)


@XyZkey.bind("modifier", modifier_key=keyboardKeys.pause, key=keyboardKeys.esc)
def _():
    global RUNNING
    RUNNING = False


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="left")
def _():
    Mouse.click(mouseButtons.x1)
    overlay_electron.seleniumJsExecute("onExec", {"bind": "back"})


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="right")
def _():
    Mouse.click(mouseButtons.x2)
    overlay_electron.seleniumJsExecute("onExec", {"bind": "forward"})


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="up")
def _():
    for i in range(3):
        XyZkey.simKey(VOL_UP)
    overlay_electron.seleniumJsExecute("onExec", {"bind": "volume up"})


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="down")
def _():
    for i in range(3):
        XyZkey.simKey(VOL_DOWN)
    overlay_electron.seleniumJsExecute("onExec", {"bind": "volume down"})


@XyZkey.bind("onTick")
def _(ticks):
    overlay_electron.seleniumJsExecute("onTick", ticks)


@XyZkey.bind("onModifierRelease")
def _():
    overlay_electron.seleniumJsExecute("onModifierRelease")


@XyZkey.bind("onModifierPress")
def _():
    overlay_electron.seleniumJsExecute("onModifierPress")



######################## DEBUG ########################


def ping_selenium(*x):
    print(*x)
    overlay_electron.seleniumJsExecute(
        "ping", json.dumps({*x}, default=lambda x: list(x) if isinstance(x, set) else x)
    )


@XyZkey.bind("modifier", modifier_key=keyboardKeys.pause, key=KeyCode.from_char("r"))
def _():
    overlay_electron.refresh()


@XyZkey.bind("modifier", modifier_key=keyboardKeys.pause, key=keyboardKeys.f12)
def _():
    overlay_electron.JsExecute("window.electron.send('openDevTools')")


############################################################################

############################################################################

from lightSelenium import lightSelenium

from tasktray import taskbarIconThread


def KILL_APP():
    global RUNNING
    RUNNING = False


RUNNING = True

if __name__ == "__main__":
    try:
        XyZkey.start()
        overlay_electron = lightSelenium(
            browser_executable=".\\electron\\release-builds\\electron-client-win32-ia32\\electron-client.exe",
            chrome_version="102",
        )
        taskbarIcon = taskbarIconThread(kill_func=KILL_APP)
        while RUNNING:
            sleep(1)
        XyZkey.__kill__()
        overlay_electron.__kill__()
        taskbarIcon.taskicon.stop()
        sys.exit(0)
    except Exception as e:
        logging.exception(e)

############################################################################
