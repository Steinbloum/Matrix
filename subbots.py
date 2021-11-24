import re
from defbot import Bot
import time
from constructors import Constructor


c = Constructor()


class Bolbot(Bot):
    def __init__(self, sim, style, balance, preset):
        super().__init__(sim, style, balance, preset)
        self.buy_ON = False
        self.sell_ON = False

    def get_buy_signal(self):
        if self.sim.df["boldowncross"] > 0:
            if self.buy_ON:
                return False
            elif not self.buy_ON:
                self.buy_ON = True

        else:
            return False

    def get_sell_signal(self):

        if self.sim.df["bolupcross"] > 0:
            return True
        else:
            return False

    def run_main(self):
        self.position_value = self.position_size * self.sim.get_last("close")
        self.buy_signal = self.get_buy_signal()
        self.sell_signal = self.get_sell_signal()
        self.run()


class Fomobot(Bot):
    def __init__(self, sim, style, balance, preset):
        super().__init__(sim, style, balance, preset)
        self.buy = False
        self.sell = False
        self.period = None
        self.trigger_buy = None
        self.trigger_sl = None
        self.trigger_sell = None

    def get_buy_signal(self):
        if (
            self.sim.df["close"]
            > self.sim.raw_df["close"].iloc[self.row - self.trigger_sl]
            * self.trigger_buy
        ):
            return True
        else:
            return False

    def get_sell_signal(self):
        if self.position_value != 0:
            if self.position_value < self.initial_balance * self.trigger_sl:
                return True
            elif self.position_value >= self.initial_balance * self.trigger_sell:
                return True
            else:
                return False

    def run_main(self):
        self.position_value = self.position_size * self.sim.get_last("close")
        self.buy_signal = self.get_buy_signal()
        self.sell_signal = self.get_sell_signal()
        self.run()

    def get_params_dict(self):
        params_dict = {
            self.style: {
                "preset": self.preset,
                "trigger_buy": "",
                "trigger_sl": "",
                "trigger_sell": "",
            }
        }
        return params_dict


new = c.create_bot_config(Fomobot("ETHUSD5m", "Fomobot", 10, "standard"))
print(new)
c.add_to_json("bot_config.json", new, "Fomobot")
