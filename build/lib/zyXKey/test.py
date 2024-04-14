from mouse import hook as mouseHook, MoveEvent
from time import sleep
from math import hypot, atan2, degrees, floor
from threading import Thread


class ticker:
    def __init__(self):
        self.x = None
        self.y = None

    def __set__(self, x, y):
        self.x, self.y = x, y

    def hypotThreshold(self, sensitivity, x, y):
        past_threshold = hypot(self.x - x, self.y - y) > sensitivity
        return past_threshold


class ticks:
    def __init__(self, section_names):
        self.ticks = {}
        for section_name in section_names:
            self.ticks[section_name] = 0

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


def rotateDegree(initial: int, transform: int) -> int:
    initial += transform
    if initial > 360:
        while initial > 360:
            initial -= 360
    elif initial < -360:
        while initial < -360:
            initial += 360
    if initial < 0:
        initial = 360 + initial
    return initial


class mouseListenerThread(Thread):
    def __init__(self, xyZkey_engine):
        Thread.__init__(self)
        self.xyZkey_engine = xyZkey_engine
        self.set = set([])

        self.last_tick = ticker()
        self.tick_dist = 20
        self.section_names = [
            "up",
            "rightup",
            "right",
            "rightdown",
            "down",
            "leftdown",
            "left",
            "leftup",
        ]
        self.directions = len(self.section_names)
        self.ticks = ticks(self.section_names)
        self.slices = 360 / self.directions

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
            if self.last_tick.x == None:
                return self.last_tick.__set__(event.x, event.y)
            if self.last_tick.hypotThreshold(self.tick_dist, event.x, event.y):
                self.tick(event.x, event.y)
                self.last_tick.__set__(event.x, event.y)
        else:
            self.last_tick.__set__(None, None)

    def sectionNames(self, i):
        return self.section_names[i]

    def tick(self, x, y):
        radian = atan2(y - self.last_tick.y, x - self.last_tick.x)
        radian_to_degrees = degrees(radian) + 180
        corrected_degrees = rotateDegree(radian_to_degrees, -90)
        which_section = round(corrected_degrees / self.slices)
        if which_section == self.directions:
            which_section = 0
        self.ticks.incr(self.sectionNames(which_section))
        if self.xyZkey_engine.onTick:
            self.xyZkey_engine.onTick(self.ticks.ticks)
        if ticked := self.ticks.check():
            self.xyZkey_engine.execMoveTick(ticked)


class dummyEngine:
    def __init__(self):
        self.xKeyDown = True

    def execMoveTick(self, ticked):
        # pass
        print("ticked", ticked)

    def onTick(self, tick):
        # pass
        print("onTick", tick)

    def onMove(self, x, y):
        pass
        # print("onMove", x, y)


xyZkey_engine = dummyEngine()

mouse_hook = mouseListenerThread(xyZkey_engine).start()

while True:
    sleep(1)
