import os
import glob
import pandas as pd
import time
from inputoutput import Io
from constructor2 import *
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
d = DataFrame_manager()


class Simulator:

    """Simulates candle by candle with the update fucntion"""

    def __init__(self, call_name, min_rows):
        self.name = call_name
        self.ticker = "{}".format(c.break_call_name(self.name)["ticker"])
        self.tf = c.break_call_name(self.name)["tf"]
        self.raw_df = d.apply_indics(
            d.resize_df(d.load_df_from_raw_file(self.name), min_rows)
        )
        self.df = d.get_row(self.raw_df, 0)
        io.print_bull("sim {} loaded".format(self.name))

    def update_df(self, row):
        self.df = d.get_row(self.raw_df, row)
        return self.df

    def get_last(self, var):
        return self.df[var]
