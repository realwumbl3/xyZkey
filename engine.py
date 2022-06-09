import logging

LOG_FORMAT = "%(filename)s - %(lineno)d - %(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="log.log", level=logging.INFO, format=LOG_FORMAT, filemode="a+")

import math
from collections import deque
import os
import json
import sys
from pathlib import Path
from time import sleep, time
from threading import Thread

from functools import wraps

from pynput import mouse
from pynput import keyboard
from pynput.keyboard import Controller as keyboardController
from pynput.mouse import Controller as mouseController

from pynput.keyboard import Key as keyboardKeys, KeyCode
from pynput.mouse import Button as mouseButtons


class xKey:
    def __init__(self, name, key):
        self.name = name
        self.key = key


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


class mouseGesture:
    def __init__(self, modifier_key, direction, callback):
        self.modifier_key = modifier_key
        self.direction = direction
        self.callback = callback


class xyZkey(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.threads = []

        self.xKeyDown = None
        self.xKeyKeys = []

        self.mouseGestures = {}
        self.modifierCombos = []
        self.keyCombos = []
        self.doublePressBinds = {}

        self.console_history = deque([], 30)

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

    def execMoveTick(self, tick_dir):
        # self.consolelog(tick_dir, self.xKeyDown)
        if self.xKeyDown.key not in self.mouseGestures:
            return False

        modifier_mouse_gestures = self.mouseGestures[self.xKeyDown.key]

        for gesture in modifier_mouse_gestures:
            if tick_dir == gesture.direction:
                gesture.callback()

    ############################## BINDING ##############################

    def bind(self, event_type, **decorated_args):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)

            self.funcBind(event_type, func=func, **decorated_args)
            return wrapper

        return decorator

    def funcBind(self, event_type, **binded_args):
        if "func" not in binded_args:
            self.consolelog("General binding error", "func must be provided.")

        if event_type == "doubleTap":

            if "key" in binded_args:
                key = binded_args["key"]
            else:
                self.consolelog("doubleTap binding error", "modifier_key must be provided.")

            self.doublePressBinds[key] = binded_args["func"]

        if event_type == "modifier":

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
                    callback=binded_args["func"],
                )
            )

        if event_type == "combo":

            if "combo" in binded_args:
                combo = binded_args["combo"]
            else:
                self.consolelog("Combo binding error", "combo must be provided.")

            self.keyCombos.append(
                keyboardCombo(
                    combo=combo,
                    callback=binded_args["func"],
                )
            )

        if event_type == "gesture":

            if "modifier_key" in binded_args:
                modifier_key = binded_args["modifier_key"]
            else:
                self.consolelog("Gesture binding error", "modifier_key must be provided.")
            if "direction" in binded_args:
                direction = binded_args["direction"]
            else:
                self.consolelog("Gesture binding error", "gesture direction must be provided.")

            if modifier_key not in self.mouseGestures:
                self.mouseGestures[modifier_key] = []
            self.mouseGestures[modifier_key].append(
                mouseGesture(
                    modifier_key=modifier_key,
                    direction=direction,
                    callback=binded_args["func"],
                )
            )

    def consolelog(self, *log):
        self.console_history.appendleft([*log])

    def xKeyAdd(self, name, key):
        self.xKeyKeys.append(
            xKey(name, key),
        )

    def get_xKey(self, key):
        for xKey in self.xKeyKeys:
            if xKey.key == key:
                self.set_xKey(xKey)
        return False

    def set_xKey(self, key):
        self.xKeyDown = key

    def default_gestures(self):
        for default_command_bind in [
            ["right", lambda: self.controller.press(KeyCode.from_vk(0xB3))],  # play/pause
            ["up", lambda: self.controller.press(KeyCode.from_vk(0xAF))],  # volup
            ["down", lambda: self.controller.press(KeyCode.from_vk(0xAE))],  # voldown
        ]:
            print(default_command_bind[0], default_command_bind[1])

    # KEYBOARD LOGIC ###############################

    def run(self):
        # MOUSE
        self.mouseThread = mouseListenerThread(self)
        # KEYBOARD
        self.keyBoardThread = keyboardListenerThread(self)
        self.threads.append(self.mouseThread)
        self.threads.append(self.keyBoardThread)

        for thread in self.threads:
            thread.start()
            # thread.join()

    ######################## DEBUG ########################

    def DisplayLoop(self):
        os.system("cls")
        print("xyZkey v1.0 - wumbl3.xyz")
        print(
            "Combo set:",
            list(self.keyBoardThread.combo_set),
        )
        print(
            "Keyboard Supressing inputs:",
            self.keyBoardThread.listener._suppress,
        )
        for log_item in list(self.console_history):
            print(log_item)


class mouseListenerThread(Thread):
    def __init__(self, xyZkey_engine):
        Thread.__init__(self)
        self.xyZkey_engine = xyZkey_engine
        self.set = set([])
        self.x = 0
        self.y = 0
        self.active = False
        self.tick_dist = 200

    def run(self):
        self.listener = mouse.Listener(
            # on_click=self.onMouseEvent,
            on_move=self.onMouseMove,
        )
        with self.listener as listener:
            listener.join()

    def onMouseEvent(self, x, y, which, hold):
        if not hold:
            return self.onMouseRelease(which, x, y)
        else:
            return self.onMousePress(which, x, y)

    def onMousePress(self, which, x, y):
        print("mouse Which", which)
        self.set.add(which)

    def onMouseRelease(self, which, x, y):
        self.set.clear()

    def onMouseMove(self, x, y):
        if self.xyZkey_engine.xKeyDown:
            if not self.active:
                self.active = True
                self.x, self.y = x, y
            self.onModMouseMove(x, y)
        else:
            self.active = False

    def onModMouseMove(self, x, y):
        triggered = None
        if self.x - x > self.tick_dist:
            triggered = "left"
        elif self.x - x < -self.tick_dist:
            triggered = "right"
        elif self.y - y > self.tick_dist:
            triggered = "up"
        elif self.y - y < -self.tick_dist:
            triggered = "down"
        if triggered:
            self.x, self.y = x, y
            self.xyZkey_engine.execMoveTick(triggered)


class keyboardListenerThread(Thread):
    def __init__(self, xyZkey_engine):
        Thread.__init__(self)
        self.xyZkey_engine = xyZkey_engine
        self.supressed = False
        self.combo_set = set([])

        self.rollover = set([])

        self.histo = deque([], 2)

    def run(self):
        self.controller = keyboardController()
        self.listener = keyboard.Listener(
            on_press=self.keyPress,
            on_release=self.keyRelease,
            win32_event_filter=self.win32Filter,
            suppress=False,
        )
        with self.listener as listener:
            listener.join()

    # SUPRESS
    def win32Filter(self, msg, data):
        self.setSuppress()
        return True

    def setSuppress(self, state=None):
        if state != None:
            self.supressed = state
        self.listener._suppress = self.supressed
        # self.xyZkey_engine.consolelog("self.supressed state", self.supressed)

    def runUnsuppressed(self, func):
        self.setSuppress(False)
        try:
            func()
        except Exception as e:
            logging.exception(e)

    def keyPress(self, key):

        if key in self.rollover:
            return True

        self.rollover.add(key)

        # HISTO STUFFS
        key_press_time = time()
        for histo_key in self.histo:
            if histo_key[0] == key:  # IF KEY IS SAME AS LAST PRESS
                difference = key_press_time - histo_key[1]  # CALCULATE DIFFERENCE IN PRESS TIME
                if (
                    difference < 0.25 and difference > 0.08
                ):  # IF LESS THAN 250MS BUT MORE THAN 80MS (hold)
                    self.xyZkey_engine.execDoublePress(key)  # EXECUTE REPEAT
                    return True
        self.histo.append([key, key_press_time])

        # MODIFIER STUFFS
        if self.xyZkey_engine.xKeyDown == None:  # IF NO MOD KEY PRESSED YET
            if self.xyZkey_engine.get_xKey(key):
                self.setSuppress(True)
                return True
        else:  # A MOD KEY IS DOWN
            self.setSuppress(True)
            self.xyZkey_engine.execModifier(key)
            return True

        self.comboCheck(key)

    def keyRelease(self, key):
        if key in self.rollover:
            self.rollover.remove(key)

        # print("release", key)
        if self.xyZkey_engine.xKeyDown == None:
            self.setSuppress(False)
        elif key == self.xyZkey_engine.xKeyDown.key:
            self.xyZkey_engine.set_xKey(None)
            self.setSuppress(False)

        if key in self.combo_set:
            self.combo_set.remove(key)

    def comboCheck(self, key):
        if not any(combo_obj.keyInCombo(key) for combo_obj in self.xyZkey_engine.keyCombos):
            return False

        self.combo_set.add(key)

        for binded_combo_obj in self.xyZkey_engine.keyCombos:
            if binded_combo_obj.keyMatchAll(self.combo_set):
                return self.xyZkey_engine.execCombo(binded_combo_obj)
