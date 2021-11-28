from numpy import busday_count
import pandas as pd
from bot import Bot
from simulators import Simulator

from constructor2 import c, d, b, p, path_to_data


class Bolbot(Bot):
    """Enters on one range on bolinger, exits on the other,
    config is :
    trade amount : how much of the wallet you go for each position ex 0.5
    sl trigger : how much before selling in red ex : 0.98
    wait reentry : trade market when the candles reenter the range, bool
    bias : 'bull' neutral' or 'bear'"""

    def __init__(self, matrix, sim, style, preset, wallet=1000):
        super().__init__(sim, style, preset, wallet=wallet)
        self.params = b.load_attributes("bot_config.json", self.style, preset)
        self.trade_amount = float(self.params["trade amount"])
        self.sl_trigger = float(self.params["trigger_sl"])
        self.wait = eval(self.params["wait for reentry"])
        self.bias = self.params["bias"]
        c.create_dir("reports/{}/{}".format(matrix.name, self.name))

    def get_signal(self):
        """checks for signals, including SL. , must return Bool"""

        dicta = {}

        if self.position is not None:
            if self.position["size"] < 0:
                # print(self.position)
                # print(self.position["value"]*-1)
                # print(1-self.sl_trigger+1)
                # print(b.get_entry_value(self.trade_history, self.trade_count) * (1-self.sl_trigger+1))
                # input()
                if self.position["value"] * -1 >= b.get_entry_value(
                    self.trade_history, self.trade_count
                ) * (1 - self.sl_trigger + 1):
                    # print
                    dicta["sl"] = True
                    return {"sl": True, "buy": False, "sell": False}
                else:
                    dicta["sl"] = False

            elif self.position["value"] > 0:
                if (
                    self.position["value"]
                    <= b.get_entry_value(self.trade_history, self.trade_count)
                    * self.sl_trigger
                ):
                    dicta["sl"] = True
                    return {"sl": True, "buy": False, "sell": False}
            else:
                dicta["sl"] = False
        dicta["sl"] = False
        if self.sim.get_last("bolupcross") != 0:
            dicta["sell"] = True
            dicta["buy"] = False
        elif self.sim.get_last("boldowncross") != 0:
            dicta["buy"] = True
            dicta["sell"] = False
        else:
            dicta["sell"] = False
            dicta["buy"] = False
        return dicta

    def run_main(self):

        b.update_value(self.sim, self.position)
        signal = self.get_signal()
        self.buy_signal = signal["buy"]
        self.sell_signal = signal["sell"]
        self.sl_signal = signal["sl"]
        self.run()

    def get_params_dict(self):
        params_dict = {
            self.style: {
                "preset": self.preset,
                "trade amount": "",
                "trigger_sl": "",
                "wait for reentry": "",
                "bias": "",
                "order_type": "market",
                "charting options": ["bolup", "boldown", "bolmav"],
            }
        }
        return params_dict


class EmaBot(Bot):
    def __init__(self, matrix, sim, style, preset, wallet=1000):
        super().__init__(sim, style, preset, wallet=wallet)
        self.params = b.load_attributes("bot_config.json", self.style, preset)
        c.create_dir("reports/{}/{}".format(matrix.name, self.name))
        self.trade_amount = float(self.params["trade amount"])
        self.sl_trigger = float(self.params["trigger_sl"])
        self.emas = self.params["emas"]
        self.counter = 0
        self.trend = None

    def get_signal(self):

        dicta = {}
        emad = {}
        self.sim.df = self.sim.df.fillna(False)
        lsval = []
        for ema in self.emas:
            lsval.append(self.sim.df[ema])
        if False not in lsval:
            if lsval == sorted(lsval):
                if self.trend == "bear":
                    self.counter += 1
                else:
                    self.counter = 0

                self.trend = "bear"
            elif lsval == sorted(lsval, reverse=True):

                if self.trend == "bull":
                    self.counter += 1
                else:
                    self.counter = 0
                    self.trend = "bull"
            else:
                self.trend = False
                self.counter = 0
        print("trend {} for {} candles".format(self.trend, self.counter))

        # input()

        return {
            "trend": self.trend,
            "counter": self.counter,
            "emas": lsval,
            # on wich ema of the lsval its gonna set the trade
            "trade_on": 0,
        }

    def set_orders(self, signal):

        if not signal["trend"]:
            return {None}
        elif signal["trend"] == "bull" and signal["counter"] > 7:
            # set the opening order
            price = signal["emas"][signal["trade_on"]]
            value = self.trade_amount * self.wallet
            size = value / price
            side = "buy"
            motive = "open"
            open = {
                "price": price,
                "value": value,
                "size": size,
                "side": side,
                "motive": motive,
            }
            # set a STATIC stop order
            price = open["price"] * self.params["trigger_sl"]
            value = price * open["size"]
            side = "sell"
            motive = "stop"
            stop = {
                "price": price,
                "value": value,
                "size": size,
                "side": side,
                "motive": motive,
            }

            # set a STATIC tp

            price = signal["emas"][0] + ((signal["emas"][0] - signal["emas"][1]) * 2)
            value = price * open["size"]
            side = "sell"
            motive = "tp"
            tp = {
                "price": price,
                "value": value,
                "size": size,
                "side": side,
                "motive": motive,
            }

            return {"open": open, "stop": stop, "tp": tp}

    def run_main(self):

        b.update_value(self.sim, self.position)
        signal = self.get_signal()
        print(self.set_orders(signal))
        input()
        self.run()

    def get_params_dict(self):
        params_dict = {
            self.style: {
                "preset": "standard",
                "trade amount": 0.5,
                "trigger_sl": 0.9,
                "emas": ["EMA25", "EMA50", "EMA100"],
                "bias": "neutral",
                "order_type": "limit",
                "charting options": ["EMA25", "EMA50", "EMA100"],
            }
        }
        return params_dict


# sim = Simulator('ETHUSDT15m', 1000)
# b.create_config('bot_config.json', EmaBot(matrix=None, sim=sim, style='Emabot', preset='standard'))
