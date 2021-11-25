from constructor2 import *


class Bot:
    def __init__(self, sim, style, preset):
        self.sim = sim
        self.style = style
        self.preset = preset
        self.name = b.name_bot()
        self.params = b.load_attributes("bot_config.json", self.style)

        self.open_position = False
        self.buy_signal = False
        self.sell_signal = False
        self.sl_signal = False
        self.sl_value = None
