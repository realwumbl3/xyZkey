class ticks:
    def __init__(self):
        self.reset()

    def reset(self):
        self.up, self.right, self.down, self.left = 0, 0, 0, 0


tickss = ticks()

for tick in vars(tickss):
    print(tick)
