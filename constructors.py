import os
import re
from numpy import string_
import pandas as pd
import glob
import time
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
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from inputoutput import Io
import datetime as dt
from plotly.subplots import make_subplots
from wonderwords import RandomWord
import random
import shutil
import json


r = RandomWord()


# client = Client(os.getenv("PUBLICAPI"), os.getenv("PRIVATEAPI"))
path_to_data = os.getenv("PATHTODATA")
print(path_to_data)
io = Io()


class Constructor:
    def __init__(self):
        self.df = None

    def get_df(self, file):

        if os.path.isdir(file):
            print("is dir")
            df = self.get_from_dir(file)
        else:
            df = pd.read_csv(file)
        return df

    def get_from_dir(self, file):

        path = file
        all_files = glob.glob(path + "/*.csv")
        df = self.df
        for file in all_files:
            if df is None:
                df = pd.read_csv(file)
                df = df.iloc[:, :6]
                df.columns = ["Date", "open", "high", "low", "close", "volume"]

            else:
                df2 = pd.read_csv(file)
                df2 = df.iloc[:, :6]
                df2.columns = ["Date", "open", "high", "low", "close", "volume"]
                df = df.append(df2, ignore_index=True)
        df["Date"] = pd.to_datetime(df.Date, unit="ms")
        return df

    def check_format(self, df):
        ls_good = ["Date", "open", "high", "low", "close", "volume"]
        ls_inspected = list(df.columns)
        if ls_good == ls_inspected:
            print("All good")
            return df
        # print(ls_inspected)
        if len(list(ls_inspected)) != len(ls_good):
            # print("Not same lenghts")
            for term in ls_inspected:
                if term == "Adj Close":
                    df = df.drop(
                        [term],
                        inplace=True,
                        axis=1,
                    )
                    break
        # print(ls_inspected)
        df.columns = [ls_good]
        # print(df)
        return df

    def apply_indics(self, df):
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

    def set_max_rows(self, df, n):

        df = df.iloc[len(df) - n : len(df)]
        return df

    def run_all(self, file, max_rows):

        df = self.get_df(file)
        df = self.check_format(df)
        # self.save_csv(df)
        return df

    def get_max_rows(self, file):
        df = self.get_df(file)
        return len(df)

    def get_historical_klines_from_binance(
        self, ticker, tf, start_date, end_date="today", to_csv=True, overwrite=False
    ):
        client = Client(os.getenv("PUBLICAPI"), os.getenv("PRIVATEAPI"))
        if not overwrite:
            if os.path.isdir("{}/{}/{}".format(path_to_data, ticker, tf)):
                print("data already stored")
                return ""
        print("Getting klines for {}-{}".format(ticker, tf))
        klines = client.get_historical_klines(ticker, tf, start_date, end_date)
        print("processing {} klines.".format(len(klines)))

        ls = []
        for item in klines:
            item = item[0:6]
            ls.append(item)
        df = pd.DataFrame(
            ls, columns=["Date", "open", "high", "low", "close", "volume"]
        )
        df["Date"] = pd.to_datetime(df["Date"], unit="ms")
        df = df.set_index("Date")
        df = df.astype("float")
        df = df.reset_index()
        if to_csv:
            if overwrite:
                outdir = "{}/{}/{}".format(path_to_data, ticker, tf)
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                print("creating csv")
                df.to_csv(
                    "{}/{}/{}/{}_{}.csv".format(
                        path_to_data,
                        ticker,
                        tf,
                        ticker,
                        tf,
                    )
                )
            elif not overwrite:
                if os.path.isdir("{}/{}/{}".format(path_to_data, ticker, tf)):
                    print("data already stored")

            print("All done")
        return df

    def get_ticker_tf(self, string):
        pairs = ["USDT", "EUR"]
        tfs = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d", "3d", "1w"]
        for pair in pairs:
            if string.find(pair) != -1:
                string = string.replace(pair, "")
                break
        for tf in tfs:
            if string.find(tf) != -1:
                string = string.replace(tf, "")
                break
        coin = string
        return {"coin": coin, "pair": pair, "tf": tf}

    def check_for_data(self, call_name, max_klines):
        call = self.get_ticker_tf(call_name)
        ticker = "{}{}".format(call["coin"], call["pair"])
        tf = call["tf"]
        path_to_file = "{}/{}/{}/{}_{}.csv".format(path_to_data, ticker, tf, ticker, tf)
        if os.path.isfile(path_to_file):
            # print("Data on {} found".format(call_name))
            df = pd.read_csv(path_to_file)
            if len(df) > max_klines:
                return True
        else:
            print("NO SUFFICIENT DATA FOR {}!".format(call_name))
            return False

    def load_df(self, name, max_rows):
        call = self.get_ticker_tf(name)
        ticker = "{}{}".format(call["coin"], call["pair"])
        tf = call["tf"]

        df = pd.read_csv(
            "{}/{}/{}/{}_{}.csv".format(path_to_data, ticker, tf, ticker, tf),
            index_col=0,
        )
        if len(df) > max_rows:
            df = self.set_max_rows(df, max_rows)
            # print("Resizing DF")
            return df
        else:
            return df

    def get_fees(self, amount, type="MARKET"):
        if type == "MARKET":
            amount *= 0.0004
            return amount
        elif type == "LIMIT":
            amount *= 0.0002
            return amount

    def get_chart_graph(self, df, start_index, end_index, trade_history, trade_number):
        # print(df)
        df = df.iloc[start_index:end_index]
        trade_history = trade_history.loc[trade_history["trade_count"] == trade_number]
        # print(trade_history)
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df["Date"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                )
            ]
        )
        fig.update_layout(xaxis_rangeslider_visible=False)

        fig.add_trace(
            go.Scatter(
                x=trade_history["Date"],
                y=trade_history["price"],
                mode="markers",
                marker=dict(color="green", symbol="triangle-up-open", size=12),
            )
        )

        trade_history = None
        fig.write_image("testi/test.png")

    def get_size_and_value(self, sim, value, side):
        price = sim.get_last("close")
        size = value / price
        return {"size": size, "value": value}

    def update_position_infos(self, sim, trade_history, trade_count):
        price = sim.get_last("close")
        if trade_history is not None:
            df = trade_history.loc[trade_history["trade_count"] == trade_count]
            if df is not None:
                # resets if size =0 : position closed
                if sum(df["size"]) == 0:
                    return {
                        "initial value": 0,
                        "initial size": 0,
                        "price": price,
                        "position value": 0,
                        "position size": 0,
                    }

                initial_value = df["value"].iloc[0]
                initial_size = df["size"].iloc[0]
                position_value = df["size"].iloc[-1] * price
                position_size = df["size"].iloc[-1]

                return {
                    "initial value": initial_value,
                    "initial size": initial_size,
                    "price": price,
                    "position value": position_value,
                    "position size": position_size,
                }
        else:
            return {
                "initial value": 0,
                "initial size": 0,
                "price": price,
                "position value": 0,
                "position size": 0,
            }

    def create_name(self, custom=False):
        if custom == False:
            name = "{}_{}".format(
                r.word(include_parts_of_speech=["adjectives"]),
                r.word(include_parts_of_speech=["nouns"]),
            )
        else:
            name = input()
        return name

    def create_dir(self, dirpath):
        path = dirpath
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def get_random_sim_list(self, amount, max_klines, conditions=True):
        ls = []
        while len(ls) < amount:
            for n in range(amount):
                lssimis = random.choice(os.listdir(path_to_data))
                tfs = random.choice(["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
                pair = lssimis + tfs
                if not pair in ls:
                    if conditions:
                        if self.check_for_data(pair, max_klines):
                            ls.append(pair)
                        else:
                            io.print_warning("NO DATA FOR {}".format(pair))

        print(ls)
        return ls

    def get_pair_list(self, pair="USDT"):
        ls = []
        client = Client(os.getenv("PUBLICAPI"), os.getenv("PRIVATEAPI"))
        exchange_info = client.get_exchange_info()
        for s in exchange_info["symbols"]:
            if (
                pair in s["symbol"]
                and "DOWN" not in s["symbol"]
                and "UP" not in s["symbol"]
            ):
                ls.append(s["symbol"])
        return ls

    def delete_up_down(self, up="up", down="down"):
        ls = os.listdir(path_to_data)
        for pair in ls:
            if "UP" in pair:
                shutil.rmtree("{}/{}".format(path_to_data, pair))
                print("{} is deleted".format(pair))
            if "DOWN" in pair:
                shutil.rmtree("{}}/{}".format(path_to_data, pair))
                print("{} is deleted".format(pair))

    def add_to_json(self, json_file, new_config, bot_type):
        ls = []
        with open(json_file, "r") as file:
            if os.stat(json_file).st_size == 0:
                ls.append(new_config)
                print("appending config")
                with open(json_file, "w") as file:
                    json.dump(json.dumps(ls), file)
                    print("config stored")
                    return new_config
            else:
                stock = json.load(file)
                ls = json.loads(stock)
                for item in ls:
                    print(item)
                    try:
                        item[bot_type]["preset"] == new_config[bot_type]["preset"]
                    except KeyError:
                        ls.append(new_config)
                        print("appending config")
                        with open(json_file, "w") as file:
                            json.dump(json.dumps(ls), file)
                            print("config stored")
                            break
                    if item[bot_type]["preset"] == new_config[bot_type]["preset"]:
                        print("preset already stored")
                    else:
                        ls.append(new_config)
                        print("appending config")
                        with open(json_file, "w") as file:
                            json.dump(json.dumps(ls), file)
                            print("config stored")
                            break

    def create_bot_config(self, bot):
        """set the paramters and return a dict to append to json"""
        params = bot.get_params_dict()
        print(params)
        for key, value in params[bot.style].items():
            if key != "preset":
                params[bot.style][key] = input("enter the param for {}\n".format(key))

        return params

    def see_json(self, json_file):
        with open(json_file, "r") as file:
            stock = json.load(file)
            ls = json.loads(stock)
            print(stock)


c = Constructor()


class Plotter:
    def __init__(self):

        pass

    def get_index_range(self, raw_df, start, end, delta=75):
        """get the index of the delta candles in the raw DF for the plotting
        Date is str format"""
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        df = raw_df
        stdt = df.index[df["Date"] == start].to_list()
        # print(stdt)
        stdt = stdt[0] - delta
        endt = df.index[df["Date"] == end].to_list()
        endt = endt[0] + delta

        return {"start": stdt, "end": endt}

    def get_chart_graph(
        self, df, start_index, end_index, trade_history, path, name, trade_count
    ):

        df = df.loc[start_index:end_index]

        trade_history = trade_history.loc[trade_history["trade_count"] == trade_count]
        buy = trade_history.loc[trade_history["side"] == "buy"]
        sell = trade_history.loc[trade_history["side"] == "sell"]

        # print(trade_history)
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df["Date"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                )
            ]
        )
        side = trade_history["position side"].iloc[0].upper()
        value = round(trade_history["value"].iloc[0], 2)
        pnl = round(sum(trade_history["pnl"]), 2)
        roi = round(sum(trade_history["pnl"]) / trade_history["value"].iloc[0] * 100, 2)
        if side == "SHORT":
            value *= -1
            roi *= -1
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            showlegend=False,
            title="{} - Value : {}$, PNL : {}, ROI : {}%".format(side, value, pnl, roi),
        )

        fig.add_trace(
            go.Scatter(
                x=sell["Date"],
                y=sell["price"],
                mode="markers",
                marker=dict(
                    color="red", size=15, line=dict(width=2, color="DarkSlateGrey")
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=buy["Date"],
                y=buy["price"],
                mode="markers",
                marker=dict(
                    color="green", size=15, line=dict(width=2, color="DarkSlateGrey")
                ),
            )
        )

        fig.write_image("{}/{}.png".format(path, name))
        return fig

    def make_chart_report(self, trade_history, raw_df, path):
        """Get the top 10 best trades and worst 10 to graph"""
        top = trade_history["pnl"].sort_values(ascending=False).head(10).index.tolist()
        worst = (
            trade_history["pnl"].sort_values(ascending=False).tail(10).index.tolist()
        )
        toppairs = []
        worstpairs = []
        for n in range(len(top)):

            toppairs.append([top[n] - 1, top[n]])
            worstpairs.append([worst[n] - 1, worst[n]])
        n = 1
        for indexes in toppairs:
            idx = self.get_index_range(
                raw_df,
                trade_history["Date"].iloc[indexes[0]],
                trade_history["Date"].iloc[indexes[1]],
            )
            # print(idx)
            trade_count = trade_history["trade_count"].iloc[indexes[0]]
            # print("tradect {}".format(trade_count))
            self.get_chart_graph(
                raw_df,
                idx["start"],
                idx["end"],
                trade_history,
                trade_count=trade_count,
                path=path,
                name="top{}".format(n),
            )
            fig = None
            n += 1
        n = 1
        worstpairs = reversed(worstpairs)
        for indexes in worstpairs:
            idx = self.get_index_range(
                raw_df,
                trade_history["Date"].iloc[indexes[0]],
                trade_history["Date"].iloc[indexes[1]],
            )
            # print(idx)
            trade_count = trade_history["trade_count"].iloc[indexes[0]]
            # print("tradect {}".format(trade_count))
            self.get_chart_graph(
                raw_df,
                idx["start"],
                idx["end"],
                trade_history,
                trade_count=trade_count,
                path=path,
                name="worst{}".format(n),
            )
            fig = None
            n += 1

    def perf_chart(
        self, trade_hist, raw, max_klines, bot_name, asset, initial_wallet, path
    ):
        """make a line chart asset perf vs bot perf"""
        td = trade_hist[trade_hist["motive"].isin(["tp", "sl", "close"])]
        raw = raw[["Date", "close"]]
        raw = raw.iloc[-max_klines:]
        # print("making report for {}".format(bot_name))
        asset_start_price = raw["close"].iloc[0]
        asset_end_price = raw["close"].iloc[-1]
        asset_roi = round(asset_end_price / asset_start_price * 100 - 100, 2)
        bot_roi = round(td["wallet"].iloc[-1] / initial_wallet * 100 - 100, 2)
        if bot_roi >= asset_roi:
            msg = "Good bot beat the market !"
        else:
            msg = "Bad bot did not outperform the market"
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=raw["Date"], y=raw["close"], name=asset))
        fig.add_trace(
            go.Scatter(x=td["Date"], y=td["wallet"], name=bot_name),
            secondary_y=True,
        )
        fig.update_layout(
            title="Asset ROI : {}% bot ROI : {}%\n" "{}".format(asset_roi, bot_roi, msg)
        )
        fig.update_yaxes(title_text="<b>Asset price</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Bot balance</b>", secondary_y=True)
        fig.write_image("/reports/{}/perfo.png".format(bot_name, path))
