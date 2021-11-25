from ta.volume import money_flow_index
from ta.trend import ema_indicator, macd, EMAIndicator, macd_signal
from ta.volatility import (
    bollinger_mavg,
    bollinger_hband,
    bollinger_lband,
    bollinger_lband_indicator,
    bollinger_hband_indicator,
)
import os
import pandas as pd
import names
from wonderwords import RandomWord
import json


r = RandomWord()

path_to_data = os.getenv("PATHTODATA")


class Constructor:
    """A class for everything relative to construction"""

    def __init__(self):
        pass

    def break_call_name(self, call_name):
        """Returns a dict for the call_name of the simulation
        ex: 'ETHUSDT15m returns
        {"pair": USDT, "tf": 15m, "coin": ETH, "ticker": ETHUSDT}
        """
        pairs = ["USDT", "EUR"]
        tfs = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d", "3d", "1w"]
        for pair in pairs:
            if pair in call_name:
                call_name = call_name.replace(pair, "")
                break
            else:
                print("PAIR ERROR")
        for tf in tfs:
            if tf in call_name:
                if tf == "5m":
                    if call_name[call_name.find(tf) - 1] != "1":
                        call_name = call_name.replace(tf, "")
                        break
                else:
                    call_name = call_name.replace(tf, "")
                    break

        coin = call_name
        return {"pair": pair, "tf": tf, "coin": coin, "ticker": coin + pair}

    def get_path_to_raw_file(self, call_name):
        """returns the path to the raw data"""
        call = self.break_call_name(call_name)
        ticker = call["ticker"]
        tf = call["tf"]
        path = "{}/{}/{}/{}.csv".format(
            path_to_data, ticker, tf, "{}_{}".format(ticker, tf)
        )
        if os.path.isfile(path):
            return path
        else:
            print("NO DATA")
            return False


class DataFrame_manager:
    def __init__(self):
        pass

    def check_for_df_size(self, call_name, size):
        """checks if file has the right amount of rows"""
        if len(self.load_df_from_raw_file(call_name)) >= size:
            return True
        else:
            return False

    def load_df_from_raw_file(self, call_name):
        """returns de dataframe for the selected path"""
        path_to_raw_file = c.get_path_to_raw_file(call_name)
        if path_to_raw_file:
            df = pd.read_csv(path_to_raw_file, index_col=0)
            return df
        else:

            return False

    def resize_df(self, df, size, from_end=True):

        """returns a resized dataframe,
        reformats the Date column to a date format.
        if from end=False will resize from the first available data"""
        # Disables the warning because on s'en bat les couilles de pas récup le str,
        # voir : https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
        pd.options.mode.chained_assignment = None  # default='warn'
        if from_end:
            df = df.iloc[-size:]
            df["Date"] = pd.to_datetime(df["Date"])
            return df
        else:
            df = df.iloc[:size]
            return df

    def apply_indics(self, df):
        """Applies indicators to the df
        WARNING : make sure to apply to a resized DF els it might take forever"""

        df["mfi"] = money_flow_index(df.high, df.low, df.close, df.volume)
        df["macd"] = macd(df.close)
        df["macds"] = macd_signal(df.close)
        df["bolup"] = bollinger_hband(df.close)
        df["bolupcross"] = bollinger_hband_indicator(df.close)
        df["bolmav"] = bollinger_mavg(df.close)
        df["boldown"] = bollinger_lband(df.close)
        df["boldowncross"] = bollinger_lband_indicator(df.close)
        df["EMA10"] = ema_indicator(df.close, window=10)
        df["EMA25"] = ema_indicator(df.close, window=25)
        df["EMA50"] = ema_indicator(df.close, window=50)
        df["EMA100"] = ema_indicator(df.close, window=100)
        df["EMA200"] = ema_indicator(df.close, window=200)
        return df

    def get_row(self, df, row):
        """returns the last row of the dataframe"""
        df = df.iloc[row]
        return df


class Bot_manager:
    def __init__(self):
        pass

    def name_bot(self):
        name = "{}_the_{}".format(
            names.get_first_name(gender="female"),
            r.word(include_parts_of_speech=["adjectives"]),
        )
        return name

    def load_attributes(self, config_file, style):
        with open(config_file, "r") as jsonfile:
            configs = json.load(jsonfile)
            configs = json.loads(configs)
            for item in configs:
                for key, value in item.items():
                    if style == key:
                        if value["preset"] == self.preset:
                            return value
                        else:
                            print("WARNING NO CONFIG FOUND")
                            return False

    def init_history(self, sim, wallet):
        """Initalises the trade history Dataframe"""
        df = pd.DataFrame(
            {
                "Date": sim.get_last("Date"),
                "price": sim.get_last("close"),
                "size": None,
                "value": None,
                "side": None,
                "motive": "INIT",
                "pnl": None,
                "fees": None,
                "wallet": wallet,
                "trade_count": 0,
                "position side": None,
            },
            index=[0],
        )
        return df

    def buy_market(self, value, size, position_info):
        """appends to the position dict"""
        if value < 0:
            value *= -1
            size *= -1
        print(position_info["side"])
        position_info["value"] += value
        position_info["size"] += size
        position_info["fees"] = self.get_fees(value)
        return {"value": value, "size": size, "fees": self.get_fees(value)}

    def sell_market(self, value, size, position_info):
        size = -size
        """appends to the position dict"""
        print(position_info["side"])
        position_info["value"] -= value
        position_info["size"] += size
        position_info["fees"] = self.get_fees(-value)
        print(value)
        return {"value": value, "size": size, "fees": self.get_fees(value)}

    def store_transaction(
        self,
        sim,
        trade_history,
        position_info,
        order,
        motive,
        side,
        fees,
        balance,
        trade_count,
        pnl=None,
    ):
        if pnl:
            df = trade_history.loc[
                trade_history["trade_count"] == position_info["trade count"]
            ]
            if position_info["side"] == "long":
                pnl = order["value"] - df["value"].iloc[-1]
            elif position_info["side"] == "short":
                pnl = df["value"].iloc[-1] - order["value"]

        ls = [
            sim.get_last("Date"),
            sim.get_last("close"),
            order["size"],
            order["value"],
            side,
            motive,
            pnl,
            fees,
            position_info["value"] + balance,
            trade_count,
            position_info["side"],
        ]
        trade_history.loc[len(trade_history)] = ls

    def get_fees(self, amount, market=True):
        if market:
            amount *= 0.0004
        else:
            amount *= 0.0002
        return amount

    def update_value(self, sim, position_info):
        position_info["value"] = position_info["size"] * sim.get_last("close")

    def get_entry_value(self, trade_history, trade_count):
        """returns the initila position value"""
        df = trade_history.loc[trade_history["trade_count"] == trade_count]
        return df.iloc[0]


c = Constructor()
d = DataFrame_manager()
b = Bot_manager()

# df = d.apply_indics(d.resize_df(d.load_df_from_raw_file("ETHUSDT5m"), 5000))

# print(df["Date"].iloc[-1])
# print(type(df["Date"].iloc[-1]))
# print(df["Date"].iloc[-1] - df["Date"].iloc[-50])
# print(b.name_bot())


# print(b.init_history())
