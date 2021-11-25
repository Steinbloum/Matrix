from simulators import Simulator
from inputoutput import io
from constructor2 import Constructor, Bot_manager, DataFrame_manager

c = Constructor()
b = Bot_manager()
d = DataFrame_manager()


class Bot:
    def __init__(self, sim, style, preset, wallet=1000):
        self.sim = sim
        self.style = style
        self.preset = preset
        self.wallet = wallet
        self.name = b.name_bot()

        self.position = None
        self.buy_signal = True
        self.sell_signal = False
        self.sl_signal = False
        self.sl_value = None
        self.trade_history = b.init_history(self.sim, self.wallet)
        self.trade_count = 0
        self.trade_amount = 0.5

    def welcome(self):
        io.print_bull(
            "Hello, I'm {}, a {}, I'm trading on {}".format(
                self.name,
                self.style,
                self.sim.name,
            )
        )

    def run(self):

        if not self.position:
            if self.buy_signal:
                self.open("long")
                buy = b.buy_market(
                    self.trade_amount * self.wallet,
                    (self.trade_amount * self.wallet) / self.sim.get_last("close"),
                    self.position,
                )
                self.exec_order(buy)
                print(self.wallet)
                b.store_transaction(
                    self.sim,
                    self.trade_history,
                    self.position,
                    buy,
                    "open",
                    "buy",
                    b.get_fees(buy["value"]),
                    self.wallet,
                    self.trade_count,
                )
            elif self.sell_signal:
                self.open("short")
                sell = b.sell_market(
                    self.trade_amount * self.wallet,
                    (self.trade_amount * self.wallet) / self.sim.get_last("close"),
                    self.position,
                )
                self.exec_order(sell)
                b.store_transaction(
                    self.sim,
                    self.trade_history,
                    self.position,
                    sell,
                    "open",
                    "sell",
                    sell["fees"],
                    self.wallet,
                    self.trade_count,
                )

        else:

            if self.position["side"] == "long":

                if self.sl_signal:
                    sell = b.sell_market(
                        self.position["value"], self.position["size"], self.position
                    )
                    # print(sell)
                    # print(self.position)
                    self.exec_order(sell)
                    print(self.position)
                    b.store_transaction(
                        self.sim,
                        self.trade_history,
                        self.position,
                        sell,
                        "sl",
                        "sell",
                        sell["fees"],
                        self.wallet,
                        self.trade_count,
                        pnl=True,
                    )
                    self.close()

                elif self.sell_signal:
                    sell = b.sell_market(
                        self.position["value"], self.position["size"], self.position
                    )
                    # print(sell)
                    # print(self.position)
                    self.exec_order(sell)
                    print(self.position)
                    b.store_transaction(
                        self.sim,
                        self.trade_history,
                        self.position,
                        sell,
                        "tp",
                        "sell",
                        sell["fees"],
                        self.wallet,
                        self.trade_count,
                        pnl=True,
                    )
                    self.close()
                

            elif self.position["side"] == "short":
                if self.sl_signal:
                    buy = b.buy_market(
                        self.position["value"], self.position["size"], self.position
                    )
                    self.exec_order(buy)
                    b.store_transaction(
                        self.sim,
                        self.trade_history,
                        self.position,
                        buy,
                        "sl",
                        "buy",
                        buy["fees"],
                        self.wallet,
                        self.trade_count,
                        pnl=True,
                    )
                    self.close()

                elif self.buy_signal:
                    buy = b.buy_market(
                        self.position["value"], self.position["size"], self.position
                    )
                    self.exec_order(buy)
                    b.store_transaction(
                        self.sim,
                        self.trade_history,
                        self.position,
                        buy,
                        "tp",
                        "buy",
                        buy["fees"],
                        self.wallet,
                        self.trade_count,
                        pnl=True,
                    )
                    self.close()
                

    def open(self, side):
        """initialises a dict for self.position,
        adds 1 to the count"""
        self.trade_count += 1
        self.position = {
            "trade count": self.trade_count,
            "side": side,
            "value": 0,
            "size": 0,
        }

    def close(self):
        "Resets the position dict"
        self.position = None

    def exec_order(self, order):
        if order["size"] < 0:
            value = order["value"] * -1
        else:
            value = order["value"]
        self.wallet -= value
        self.wallet -= order["fees"]
