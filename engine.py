import logging
import unicodedata

LOG_FORMAT = "%(filename)s - %(lineno)d - %(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="log.log", level=logging.INFO, format=LOG_FORMAT, filemode="a+")

import os
import json
import sys
from threading import Thread
from collections import deque
from functools import wraps

from .xyzKeyModules import keyboardListenerThread, mouseListenerThread

from pynput.keyboard import Key, KeyCode


class xKey:
    def __init__(self, name, key):
        try:
            self.name = name
            self.key = key
            self.vk = self.key._value_.vk
        except Exception as e:
            logging.exception(e)
            print(e)


class mouseGesture:
    def __init__(self, callback):
        self.callback = callback


class keyboardCombo:
    def __init__(self, combo, callback):
        self.combo = combo
        self.callback = callback

    def keyInCombo(self, key):
        return key in self.combo

    def keyMatchAll(self, check_set):
        return all(keys in check_set for keys in self.combo)


class modifierCombo:
    def __init__(self, modifier_key, key, callback):
        self.modifier_key = modifier_key
        self.key = key
        self.callback = callback


class xyZkey(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.threads = []

        self.onMove = None
        self.onTick = None
        self.onModifierRelease = None
        self.onModifierPress = None

        self.xKeyDown = None
        self.xKeyKeys = []

        self.keyboardPress = lambda x: self.xKeyKeyboard.controller.press(x)

        self.mouseGestures = {}
        self.modifierCombos = []
        self.keyCombos = []
        self.doublePressBinds = {}

        self.console_history = deque([], 30)

    def run(self):
        self.xKeyMouse = mouseListenerThread(self)
        self.xKeyKeyboard = keyboardListenerThread(self)
        self.threads.append(self.xKeyMouse)
        self.threads.append(self.xKeyKeyboard)
        for thread in self.threads:
            thread.start()

    def __kill__(self):
        self.xKeyMouse.join()
        self.xKeyKeyboard.__kill__()
        print("killed xyzKey.")

    def DisplayLoop(self):
        os.system("cls")
        print("xyZkey v1.0 - wumbl3.xyz")
        print("Combo set:", list(self.xKeyKeyboard.combo_set))
        print("Keyboard Supressing inputs:", self.xKeyKeyboard.listener._suppress)
        for log_item in list(self.console_history):
            print(log_item)

    ############################## EXECS ##############################

    # When a key is pressed while modifier key is down.
    def execModifier(self, key):
        # self.consolelog("modifier key!", key, "mod key", self.xKeyDown)
        for bind in self.modifierCombos:
            if bind.key == key and bind.modifier_key == self.xKeyDown.key:
                bind.callback()

    # When a key combination is completed.
    def execCombo(self, combo_obj):
        # self.consolelog("combo!", combo_obj)
        combo_obj.callback()

    # When a key was pressed twice (in under 250ms)
    def execDoublePress(self, key):
        if key in self.doublePressBinds:
            self.doublePressBinds[key]()

    def execMoveTick(self, tick):
        # self.consolelog(tick_dir, self.xKeyDown)

        if self.xKeyDown.key not in self.mouseGestures:
            return False

        modifier_mouseGestures = self.mouseGestures[self.xKeyDown.key]

        if tick in modifier_mouseGestures.keys():
            modifier_mouseGestures[tick].callback()

    ############################## BINDING ##############################

    def bind(self, event_type, **decorated_args):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)

            self.funcBind(event_type, func=func, **decorated_args)
            return wrapper

        return decorator

    def funcBind(self, bind_type, **binded_args):

        if "func" not in binded_args:
            self.consolelog("function must be provided")

        func = binded_args["func"]

        if bind_type in vars(self):
            setattr(self, bind_type, func)

        if bind_type == "doubleTap":

            if "key" in binded_args:
                key = binded_args["key"]
            else:
                self.consolelog("doubleTap binding error", "modifier_key must be provided.")

            self.doublePressBinds[key] = func

        if bind_type == "modifier":

            if "modifier_key" in binded_args:
                modifier_key = binded_args["modifier_key"]
            else:
                self.consolelog("Modifier binding error", "modifier_key must be provided.")
            if "key" in binded_args:
                key = binded_args["key"]
            else:
                self.consolelog("Modifier binding error", "key must be provided.")

            self.modifierCombos.append(
                modifierCombo(
                    modifier_key=modifier_key,
                    key=key,
                    callback=func,
                )
            )

        if bind_type == "combo":

            if "combo" in binded_args:
                combo = binded_args["combo"]
            else:
                self.consolelog("Combo binding error", "combo must be provided.")

            self.keyCombos.append(
                keyboardCombo(
                    combo=combo,
                    callback=func,
                )
            )

        if bind_type == "gesture":

            if "modifier_key" in binded_args:
                modifier_key = binded_args["modifier_key"]
            else:
                self.consolelog("Gesture binding error", "modifier_key must be provided.")
            if "direction" in binded_args:
                direction = binded_args["direction"]
            else:
                self.consolelog("Gesture binding error", "gesture direction must be provided.")

            if modifier_key not in self.mouseGestures:
                self.mouseGestures[modifier_key] = {}

            self.mouseGestures[modifier_key][direction] = mouseGesture(
                callback=func,
            )

    def consolelog(self, *log):
        self.console_history.appendleft([*log])

    def xKeyAdd(self, name, key):
        self.xKeyKeys.append(xKey(name, key))

    def get_xKey(self, key):
        for xKey in self.xKeyKeys:
            if xKey.key == key:
                self.set_xKey(xKey)
        return False

    def set_xKey(self, key):
        if key == None:
            if self.onModifierRelease:
                self.onModifierRelease()
            self.xKeyMouse.ticks.reset()
        if key != None and self.onModifierPress:
            self.onModifierPress()
        self.xKeyDown = key
