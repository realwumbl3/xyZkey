from threading import Thread
import logging

from time import time

from collections import deque

from pynput.keyboard import Listener as keyboardListener, Controller as keyboardController, Key


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
        self.listener = keyboardListener(
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

    def win32Filter(self, msg, data):
        vk_code = data.vkCode
        for xKey in self.xyZkey_engine.xKeyKeys:
            if vk_code == xKey.vk:
                self.setSuppress(True)
        return True

    def setSuppress(self, state=None):
        self.listener._suppress = state

    def unsuppressed(self, key):
        was_suppressed = bool(self.listener._suppress)
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
        # print("keydown supressed self.listener._suppress:", self.listener._suppress)

        self.rollover.add(key)

        # HISTO STUFFS
        key_press_time = time()
        for histo_key in self.histo:
            if histo_key[0] == key:  # IF KEY IS SAME AS LAST PRESS
                difference = key_press_time - histo_key[1]  # CALCULATE DIFFERENCE IN PRESS TIME
                if (
                    difference < 0.35 and difference > 0.08
                ):  # IF LESS THAN 250MS BUT MORE THAN 80MS (hold)
                    self.xyZkey_engine.execDoublePress(key)  # EXECUTE REPEAT
                    return True
        self.histo.append([key, key_press_time])

        # MODIFIER STUFFS
        if self.xyZkey_engine.xKeyDown == None:  # IF NO MOD KEY PRESSED YET
            if self.xyZkey_engine.get_xKey(key):
                return True
        else:  # A MOD KEY IS DOWN
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


def showWin32Data(data):
    print("data.vkCode", data.vkCode)
    print("data.scanCode", data.scanCode)
    print("data.time", data.time)
    print("data.flags", data.flags)
