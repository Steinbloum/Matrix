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
        self.params = self.load_attributes("bot_config.json")
        self.trigger_buy = float(self.params["trigger_buy"])
        self.trigger_sl = float(self.params["trigger_sl"])
        self.trigger_sell = float(self.params["trigger_sell"])
        self.period = int(self.params["period"])

    def get_buy_signal(self):
        if (
            self.sim.df["close"]
            > self.sim.raw_df["close"].iloc[self.row - self.period] * self.trigger_buy
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
                "period": "",
            }
        }
        return params_dict


class Bolibot(Bot):

    """Bollinger bands based bot.
    params:
    trigger_sl :  will trigger SL if position value is n times the inital value, ex = 0.9 is 10% loss
    wait for reentry : will wait for the close to reenter in the bollinger bands range, bool
    bias : bull, bear, or neutral
    trade amount :  will enter with x times the balance on each trade, ex : 0.2"""

    def __init__(self, sim, style, balance, preset):
        super().__init__(sim, style, balance, preset)

        self.buy = False
        self.sell = False
        self.out_of_bands_up = False
        self.out_of_bounds_down = False
        self.params = self.load_attributes("bot_config.json")
        self.reentry = eval(self.params["wait for reentry"])
        self.trigger_sl = float(self.params["trigger_sl"])
        self.bias = self.params["bias"]
        self.trigger_buy = False
        self.trigger_sell = False
        self.updated_infos = c.update_position_infos(
            self.sim, self.trade_history, self.trade_count
        )
        print(self.preset)
        print(self.reentry)
        print(type(self.reentry))
        print(self.params["wait for reentry"])
        input()

    def get_buy_signal(self):

        if self.reentry == False:
            if self.sim.df["boldowncross"] > 0:
                return True
            else:
                return False
        elif self.reentry == True:
            if not self.out_of_bounds_down:
                if self.sim.df["boldowncross"] > 0:
                    self.out_of_bounds_down = True
                    print("out of bounds down")
                else:
                    return False
            elif self.out_of_bounds_down:
                if self.sim.df["boldowncross"] == 0:
                    self.out_of_bounds_down = False
                    print("reentry in bounds")

                    return True
                else:
                    return False

    def get_sell_signal(self):

        if self.reentry == False:
            if self.sim.df["bolupcross"] > 0:
                return True
            else:
                return False
        elif self.reentry == True:
            if not self.out_of_bands_up:
                if self.sim.df["bolupcross"] > 0:
                    self.out_of_bands_up = True
                    print("out of bands up")
                else:
                    return False
            elif self.out_of_bands_up:
                if self.sim.df["bolupcross"] == 0:
                    self.out_of_bands_up = False
                    print("reentry in bounds")
                    return True
                else:
                    return False

    def run_main(self):
        self.updated_infos = c.update_position_infos(
            self.sim, self.trade_history, self.trade_count
        )
        self.buy_signal = self.get_buy_signal()
        self.sell_signal = self.get_sell_signal()
        self.run()

    def get_params_dict(self):
        params_dict = {
            self.style: {
                "preset": self.preset,
                "trigger_sl": "",
                "wait for reentry": "",
                "bias": "",
                "trade amount": "",
            }
        }
        return params_dict


# new = c.create_bot_config(Bolibot("ETHUSD5m", "Bolibot", 10, "waiter"))
# print(new)
# c.add_to_json("bot_config.json", new, "Bolibot")
