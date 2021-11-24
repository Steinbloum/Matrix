import json
from os import close, error, name

from numpy import short
from simulators import Simulator
from constructors import Constructor, Plotter
from inputoutput import Io
import pandas as pd
import names
from wonderwords import RandomWord
import time
import os

r = RandomWord()
c = Constructor()
io = Io()
ch = Plotter()


class Bot:
    """For the execution of the trades and reporting"""

    def __init__(self, sim, style, balance, preset):
        self.matrix_name = None
        self.sim = sim
        self.initial_balance = balance
        self.balance = balance
        self.style = style
        self.preset = preset
        self.name = self.name_bot()
        self.sl = None
        # POSITION INFO
        self.position_open = False
        self.initial_position_size = 0
        self.initial_position_value = 0
        self.position_size = 0
        self.position_value = 0
        self.marg_bal = self.position_value + self.balance
        self.position_side = None
        self.trade_count = 0
        #
        self.buy_signal = False
        self.sell_signal = False

        self.trade_history = None
        self.name = name
        self.load_attributes("bot_config.json")
        self.row = None

    def name_bot(self, custom=False):
        if custom == False:
            self.name = "{}_the_{}".format(
                names.get_first_name(gender="female"),
                r.word(include_parts_of_speech=["adjectives"]),
            )
        else:
            name = input("enter a name")
            self.name = "{}{}{}".format(name, self.sim.ticker, self.sim.tf)

    def wake_up(self):

        io.print_bull("BOT {} AWAKE".format(self.name))

    def buy_market(self, motive, value, pnl=False):
        order_size = value / self.sim.get_last("close")
        self.position_value = self.position_size * self.sim.get_last("close")
        self.balance -= value
        fees = c.get_fees(value)
        self.balance -= fees
        if pnl:
            pnl = value + self.initial_position_value
        else:
            pnl = 0
        self.store_history(value, order_size, "buy", motive, pnl, fees)

    def sell_market(self, motive, value, pnl=False):
        order_value = value
        order_size = order_value / self.sim.get_last("close")
        self.balance += order_value
        self.position_size -= order_size
        if pnl:
            pnl = order_value - self.initial_position_value
        else:
            pnl = 0
        if self.position_size == 0:
            self.position_value = 0
            self.position_open = False
            self.initial_position_value = 0
            self.initial_position_size = 0
        fees = c.get_fees(order_value)
        self.balance -= fees

        self.store_history(order_value, order_size, "sell", motive, pnl, fees)

    def close(self):
        self.position_open = False

    def open(self, side):

        self.trade_count += 1
        self.position_open = True
        self.position_side = side

    def get_results(self, matrix_name, save=True):
        path = c.create_dir("reports/{}/{}".format(self.matrix_name, self.name))
        df = self.trade_history
        print(df.round({"wallet": 2, "pnl": 2, "fees": 2}))
        if not os.path.exists(path):
            os.makedirs(path)
        df.to_csv("{}/{}_t_hist.csv".format(path, self.name))

        df = df.loc[df["motive"] != "INIT"]
        self.sim.raw_df["Date"] = pd.to_datetime(self.sim.raw_df["Date"])
        time_span = self.sim.raw_df["Date"].iloc[-1] - self.sim.raw_df["Date"].iloc[0]

        trades = len(df.loc[df["motive"] == "open"])

        wt = len(df.loc[df["motive"] == "tp"])
        lt = trades - wt
        wr = wt / trades * 100
        pnl = sum(df["pnl"])
        roi = pnl / self.initial_balance * 100
        fees = sum(df["fees"])

        dfr = pd.DataFrame(
            {
                "name": self.name,
                "class": self.style,
                "preset": self.preset,
                "date": time_span,
                "trades": trades,
                "won": wt,
                "lost": lt,
                "win_rate": wr,
                "pnl": pnl,
                "roi": roi,
                "fees": fees,
                "adjusted_pnl": pnl - fees,
                "adjusted_roi": round((pnl - fees) / self.initial_balance * 100, 2),
                "pair": self.sim.ticker,
                "tf": self.sim.tf,
            },
            index=[0],
        )

        if not os.path.exists(path):
            os.makedirs(path)
        dfr.to_csv("{}/{}.csv".format(path, self.name))

        return dfr

    def store_history(self, value, size, side, motive, pnl, fees):
        time = self.sim.df["Date"]
        price = self.sim.get_last("close")
        wallet = self.balance
        trade_count = self.trade_count
        if self.trade_history is None:
            df = pd.DataFrame(
                columns=[
                    "Date",
                    "price",
                    "size",
                    "value",
                    "side",
                    "motive",
                    "pnl",
                    "fees",
                    "wallet",
                    "trade_count",
                    "position side",
                ]
            )
        else:
            df = self.trade_history
        ls = [
            time,
            price,
            size,
            value,
            side,
            motive,
            pnl,
            fees,
            wallet,
            trade_count,
            self.position_side,
        ]
        df.loc[len(df)] = ls
        self.trade_history = df

    def run(self):

        updated = c.update_position_infos(
            self.sim, self.trade_history, self.trade_count
        )

        if not self.position_open:

            if self.buy_signal:
                self.open("long")
                value = self.balance * 0.5
                size = c.get_size_and_value(self.sim, self.balance * 0.5, "buy")["size"]
                self.market_trade(value, size, "open", side="buy")

            elif self.sell_signal:
                self.open("short")
                value = self.balance * 0.5
                size = c.get_size_and_value(self.sim, self.balance * 0.5, "sell")[
                    "size"
                ]
                self.market_trade(value, size, "open", side="sell")

        elif self.position_open:
            if self.position_side == "long":
                if self.sell_signal:
                    value = updated["position value"]
                    size = updated["position size"]
                    self.market_trade(value, size, "tp", "sell", get_pnl=True)
                elif updated["position value"] < updated["initial value"] * self.sl:
                    value = updated["position value"]
                    size = updated["position size"]
                    self.market_trade(value, size, "sl", "sell", get_pnl=True)

                if (
                    c.update_position_infos(
                        self.sim, self.trade_history, self.trade_count
                    )["position size"]
                    == 0
                ):
                    self.close()
            elif self.position_side == "short":
                if self.buy_signal:
                    value = updated["position value"]
                    size = updated["position size"]
                    self.market_trade(-value, -size, "tp", "buy", get_pnl=True)
                elif updated["position value"] < updated["initial value"] * (
                    (1 - self.sl) + 1
                ):

                    # print(self.trade_history)
                    # print(
                    #     "pos_val = {}, po init val={}, sl {}= ".format(
                    #         updated["position value"],
                    #         updated["initial value"],
                    #         updated["initial value"] * ((1 - self.sl) + 1),
                    #     )
                    # )
                    # input()
                    value = updated["position value"]
                    size = updated["position size"]
                    self.market_trade(-value, -size, "sl", "buy", get_pnl=True)

                if (
                    c.update_position_infos(
                        self.sim, self.trade_history, self.trade_count
                    )["position size"]
                    == 0
                ):
                    self.close()

    def market_trade(self, value, size, motive, side, get_pnl=False):
        fees = c.get_fees(value)
        if side == "sell":
            uvalue = -value
            usize = -size
        else:
            uvalue = value
            usize = size

        if fees < 0:
            fees *= -1
        if side == "sell":
            if get_pnl:
                pnl = (
                    uvalue * -1
                    - c.update_position_infos(
                        self.sim, self.trade_history, self.trade_count
                    )["initial value"]
                )
            else:
                pnl = 0
        if side == "buy":
            if get_pnl:
                pnl = (
                    -uvalue
                    - c.update_position_infos(
                        self.sim, self.trade_history, self.trade_count
                    )["initial value"]
                )

            else:
                pnl = 0
        self.balance -= uvalue
        self.balance -= fees
        self.store_history(uvalue, usize, side, motive, pnl, fees)

    def get_reports(self):
        path = c.create_dir("reports/{}/{}".format(self.matrix_name, self.name))
        df = self.sim.raw_df
        ch.make_chart_report(self.trade_history, df, path)
        ch.perf_chart(
            self.trade_history,
            self.sim.raw_df,
            len(self.sim.raw_df),
            self.name,
            self.sim.ticker,
            self.initial_balance,
            path,
        )

    def load_attributes(self, config_file):
        with open(config_file, "r") as jsonfile:
            configs = json.load(jsonfile)
            configs = json.loads(configs)
            for item in configs:
                for key, value in item.items():
                    if self.style == key:
                        if value["preset"] == self.preset:
                            # print("preset found")
                            self.sl = value["sl"]

    def set_matrix_name(self, name):
        self.matrix_name = name

    def set_row(self, row):
        self.row = row
