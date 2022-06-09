from time import sleep
import os

from engine import xyZkey, keyboardKeys, mouseButtons, KeyCode

from pynput.keyboard import Controller as keyboardController
from pynput.mouse import Controller as mouseController

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


"""
############################################################################

Mouse = mouseController()
Keyboard = keyboardController()

XyZkey = xyZkey()

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


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="right")
def _():
    Mouse.click(mouseButtons.x2)
    XyZkey.consolelog("main.py: f13 + right gesture !")


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="up")
def _():
    for i in range(4):
        Keyboard.press(KeyCode.from_vk(0xAF))
    XyZkey.consolelog("main.py: f13 + left gesture !")


@XyZkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="down")
def _():
    for i in range(4):
        Keyboard.press(KeyCode.from_vk(0xAE))
    XyZkey.consolelog("main.py: f13 + right gesture !")


######################## DEBUG ########################
# print(vars(XyZkey))
# XyZkey.consolelog = lambda *x: print(*x)
############################################################################


if __name__ == "__main__":
    XyZkey.start()
    while True:
        sleep(0.1)
        # XyZkey.DisplayLoop()

############################################################################
