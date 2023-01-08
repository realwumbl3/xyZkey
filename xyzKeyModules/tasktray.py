import pystray
from PIL import Image
from threading import Thread


class taskbarIconThread(Thread):
    def __init__(self, exit_func):
        Thread.__init__(self)
        self.exit_func = exit_func

        self.engine_path = __file__.split("\\xyzKeyModules\\tasktray.py")[0]

        self.taskbar_ico = Image.open(f"{self.engine_path}\\icon.ico")

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

    def __kill__(self):
        self.taskicon.stop()
