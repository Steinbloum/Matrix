import os
import glob
import pandas as pd
import time
from inputoutput import Io
from constructors import Constructor
from ta.momentum import rsi
from ta.volume import money_flow_index
from ta.trend import ema_indicator, macd, EMAIndicator, macd_signal
from ta.volatility import (
    bollinger_mavg,
    bollinger_hband,
    bollinger_lband,
    bollinger_lband_indicator,
    bollinger_hband_indicator,
)

io = Io()
c = Constructor()


class Wallet:
    def __init__(self, name="wallet", balance=10000):
        self.balance = balance
        self.name = name
        self.history = []
        self.upnl = 0

    def change_balance(self, amount):
        self.balance += amount
        self.history.append(amount)

    def update_upnl(self, value):
        self.upnl = value


class Simulator:

    """Takes in a folder of format Time-OHLCV, returns a df with indicator values,
    has functions to identify entries for bots
    if force reaggs, overwrtie file
    """

    def __init__(
        self,
        call_name,
        max_rows=20000,
    ):
        self.name = call_name
        call = c.get_ticker_tf(call_name)
        self.ticker = "{}{}".format(call["coin"], call["pair"])
        self.tf = call["tf"]
        self.raw_df = None
        self.df = None
        self.max_rows = max_rows
        self.raw_df = c.apply_indics(c.load_df(call_name, max_rows=self.max_rows))
        self.df = self.update_df(0)
        io.print_bull("sim {} loaded".format(self.name))

    def update_df(self, row):
        self.df = self.raw_df.iloc[row]

        return self.df

    def init_sim(self):
        dfinit = self.raw_df.iloc[0]
        self.df = dfinit
        return dfinit

    def get_last(self, var):
        return self.df[var]
