from time import sleep
import os

from engine import megaXkey, keyboardKeys, mouseButtons

from pynput.keyboard import Controller as keyboardController
from pynput.mouse import Controller as mouseController

Mouse = mouseController()

MegaXkey = megaXkey()

MegaXkey.xKeyAdd("f13", keyboardKeys.f13)
MegaXkey.xKeyAdd("f14", keyboardKeys.f14)
MegaXkey.xKeyAdd("pause", keyboardKeys.pause)

############################################################################
"""

@MegaXkey.bind("modifier", keyboardKeys.esc)
def test_bind():
    MegaXkey.consolelog("esc!")


@MegaXkey.bind("combo", [keyboardKeys.alt_l, keyboardKeys.delete])
def test_bind():
    MegaXkey.consolelog("combo!")



"""
############################################################################


@MegaXkey.bind("modifier", modifier_key=keyboardKeys.pause, key=keyboardKeys.esc)
def _():
    MegaXkey.consolelog("main.py: esc!")


@MegaXkey.bind("combo", combo=[keyboardKeys.alt_l, keyboardKeys.delete])
def _():
    MegaXkey.consolelog("main.py: combo!")


@MegaXkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="left")
def _():
    Mouse.click(mouseButtons.x1)
    MegaXkey.consolelog("main.py: f13 + left gesture !")


@MegaXkey.bind("gesture", modifier_key=keyboardKeys.f13, direction="right")
def _():
    Mouse.click(mouseButtons.x2)
    MegaXkey.consolelog("main.py: f13 + right gesture !")


MegaXkey.start()

######################## DEBUG ########################
# print(vars(MegaXkey))
############################################################################

# MegaXkey.consolelog = lambda *x: print(*x)

if __name__ == "__main__":
    while True:
        sleep(0.1)
        MegaXkey.DisplayLoop()

############################################################################
