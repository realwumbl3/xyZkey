import pystray
from PIL import Image
from threading import Thread


class taskbarIconThread(Thread):
    def __init__(self, exit_func):
        Thread.__init__(self)
        self.exit_func = exit_func
        self.taskbar_ico = Image.open("icon.ico")

        self.taskicon = pystray.Icon(
            "xyzKey",
            self.taskbar_ico,
            menu=pystray.Menu(
                pystray.MenuItem("exit", self.exit_app),
            ),
        )
        self.start()

    def exit_app(self, icon, item):
        self.exit_func()

    def run(self):
        self.taskicon.run()
