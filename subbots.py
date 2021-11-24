from defbot import Bot
import time


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
