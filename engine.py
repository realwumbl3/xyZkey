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

from mouse import hook as mouseHook, ButtonEvent, MoveEvent


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
    def __init__(self, callback):
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

        self.simKey = lambda x: self.xKeyKeyboard.simUnsuppressed(x)

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

    def execMoveTick(self, tick):
        # self.consolelog(tick_dir, self.xKeyDown)
        print("exec tick", tick)

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
        self.xKeyKeys.append(
            xKey(name, key),
        )

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
        self.xKeyMouse = mouseListenerThread(self)
        # KEYBOARD
        self.xKeyKeyboard = keyboardListenerThread(self)
        self.threads.append(self.xKeyMouse)
        self.threads.append(self.xKeyKeyboard)

        for thread in self.threads:
            thread.start()

    def __kill__(self):
        self.xKeyMouse.join()
        self.xKeyKeyboard.__kill__()
        print("killed xyzKey.")

    ######################## DEBUG ########################

    def DisplayLoop(self):
        os.system("cls")
        print("xyZkey v1.0 - wumbl3.xyz")
        print(
            "Combo set:",
            list(self.xKeyKeyboard.combo_set),
        )
        print(
            "Keyboard Supressing inputs:",
            self.xKeyKeyboard.listener._suppress,
        )
        for log_item in list(self.console_history):
            print(log_item)


class ticks:
    def __init__(self):
        self.ticks = {"up": 0, "right": 0, "down": 0, "left": 0}

    def reset(self):
        for val in self.ticks.keys():
            self.ticks[val] = 0

    def check(self):
        for key, val in self.ticks.items():
            if val >= 4:
                self.reset()
                return key

    def incr(self, key):
        self.ticks[key] += 1


class position:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.set = False

    def set_pos(self, x, y):
        self.x, self.y = x, y
        self.set = True


class mouseListenerThread(Thread):
    def __init__(self, xyZkey_engine):
        Thread.__init__(self)
        self.xyZkey_engine = xyZkey_engine
        self.set = set([])
        self.position = position()
        self.ticks = ticks()

        self.active = False
        self.tick_dist = 30

    def run(self):
        self.hook = mouseHook(self.onMouseEvent)

    def onMouseEvent(self, event):
        if type(event) == MoveEvent:
            return self.onMouseMove(event)
        elif type(event) == ButtonEvent:
            if event.event_type == "up":
                return self.onMouseRelease(event)
            elif event.event_type == "down" or event.event_type == "double":
                return self.onMousePress(event)

    def onMousePress(self, event):
        self.set.add(event.button)

    def onMouseRelease(self, event):
        self.set.clear()

    def onMouseMove(self, event):
        if self.xyZkey_engine.onMove:
            self.xyZkey_engine.onMove(event.x, event.y)

        if self.xyZkey_engine.xKeyDown:
            if not self.active:
                self.active = True
                self.position.set_pos(event.x, event.y)
            self.onModMouseMove(event.x, event.y)
        else:
            self.active = False

    def onModMouseMove(self, x, y):

        if self.position.x - x > self.tick_dist:
            self.ticks.incr("left")
        elif self.position.x - x < -self.tick_dist:
            self.ticks.incr("right")
        elif self.position.y - y > self.tick_dist:
            self.ticks.incr("up")
        elif self.position.y - y < -self.tick_dist:
            self.ticks.incr("down")
        else:
            return False

        self.position.set_pos(x, y)

        if self.xyZkey_engine.onTick:
            self.xyZkey_engine.onTick(self.ticks.ticks)

        if ticked := self.ticks.check():
            self.xyZkey_engine.execMoveTick(ticked)


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
            self._listener = listener
            listener.join()

    def __kill__(self):
        self._listener.stop()

    # SUPRESS
    def win32Filter(self, msg, data):
        self.setSuppress()
        return True

    def setSuppress(self, state=None):
        if state != None:
            self.supressed = state
        self.listener._suppress = self.supressed

    def simUnsuppressed(self, key):
        was_suppressed = bool(self.supressed)
        self.setSuppress(False)
        try:
            self.controller.press(key)
        except Exception as e:
            logging.exception(e)
        if was_suppressed:
            self.setSuppress(True)

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
