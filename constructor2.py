from numpy import add
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
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
from inputoutput import Io

r = RandomWord()
io = Io()
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
            # print("NO DATA")
            return False

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

    def create_dir(self, dirpath):
        path = dirpath
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def create_csv_from_df(self, df, path):
        """creates a csv to the selected path"""

        df.to_csv("{}".format(path))

    def random_name(self):

        name = "{}_{}".format(
            r.word(include_parts_of_speech=["adjectives"]),
            r.word(include_parts_of_speech=["nouns"]),
        )
        return name

    def get_random_sim_list(self, amount, max_klines, conditions=True):
        ls = []
        while len(ls) < amount:
            for n in range(amount):
                lssimis = random.choice(os.listdir(path_to_data))
                tfs = random.choice(["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
                pair = lssimis + tfs
                if not pair in ls:
                    # print(pair)
                    if conditions:
                        if self.get_path_to_raw_file(pair):
                            # print("YES")
                            if len(d.load_df_from_raw_file(pair)) >= max_klines:
                                # print("APPEDING")
                                ls.append(pair)
                        else:
                            io.print_warning("NO DATA FOR {}".format(pair))

        # print(ls)
        return ls


class DataFrame_manager:
    def __init__(self):
        pass

    def check_for_df_size(self, call_name, size):
        """checks if file has the right amount of rows"""
        if len(self.load_df_from_raw_file(call_name)) >= size:
            return True

    def load_df_from_raw_file(self, call_name):
        """returns de dataframe for the selected path"""
        path_to_raw_file = c.get_path_to_raw_file(call_name)
        if path_to_raw_file:
            df = pd.read_csv(path_to_raw_file, index_col=0)
            # print(df)
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

    def add_df_to_df(self, df, df_to_add):

        df.append(df_to_add)

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

    def load_attributes(self, config_file, style, preset):
        with open(config_file, "r") as jsonfile:
            configs = json.load(jsonfile)
            configs = json.loads(configs)
            for item in configs:
                print(item)
                for key, value in item.items():
                    if style == key:
                        if value["preset"] == preset:
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
        # print(position_info["side"])
        position_info["value"] += value
        position_info["size"] += size
        position_info["fees"] = self.get_fees(value)
        return {"value": value, "size": size, "fees": self.get_fees(value)}

    def sell_market(self, value, size, position_info):
        size = -size
        """appends to the position dict"""
        # print(position_info["side"])
        position_info["value"] -= value
        position_info["size"] += size
        position_info["fees"] = self.get_fees(-value)
        # print(value)
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
        """updates the value of the position"""
        try:
            position_info["value"] = position_info["size"] * sim.get_last("close")
        except TypeError:
            ("NO POSITION")

    def get_entry_value(self, trade_history, trade_count):
        """returns the initila position value"""
        df = trade_history.loc[trade_history["trade_count"] == trade_count]
        # print(df['value'].iloc[0])
        # print(type(df['value'].iloc[0]))
        return df["value"].iloc[0]

    def create_config(self, config_file, bot, save=True):
        """set the paramters, return a dict to append to json"""
        """COMMENT THE INIT SECTION OF THE SUBBOT BEFORE RUNNING"""
        params = bot.get_params_dict()
        print(params)
        for key, value in params[bot.style].items():
            if key != "preset":
                params[bot.style][key] = input("enter the param for {}\n".format(key))
        if save:
            c.add_to_json(config_file, params, bot.style)
        return params

    def get_results(self, matrix,bot, trade_history, name, style, preset, raw_df):
        if len(trade_history.loc[trade_history["motive"] != " INIT"]) == 0:
            print("no trades for {}".format(name))
            return False
        else:
            trades = trade_history["trade_count"].iloc[-1]
            wt = len(trade_history.loc[trade_history["pnl"] > 0])
            lt = trades - wt
            wr = wt / trades * 100
            pnl = sum(
                filter(
                    None, trade_history["pnl"].loc[trade_history["motive"] != "INIT"]
                )
            )
            fees = sum(trade_history["fees"].loc[trade_history["motive"] != "INIT"])
            roi = pnl / trade_history["wallet"].iloc[0] * 100
            tspan = raw_df["Date"].iloc[-1] - raw_df["Date"].iloc[0]
            df = pd.DataFrame(
                {
                    "name": name,
                    "type": style,
                    "preset": preset,
                    "time-span": tspan,
                    "trades": trades,
                    "won": wt,
                    "win_rate": wr,
                    "pnl": pnl,
                    "roi": roi,
                    "fees": fees,
                    "adj_pnl": pnl - fees,
                    "adj_roi": trade_history["wallet"].iloc[-1]
                    / trade_history["wallet"].iloc[0]
                    * 100
                    - 100,
                    "ticker": bot.sim.ticker,
                    "tf":bot.sim.tf
                },
                index=[0],
            )
            # print(df)
            c.create_csv_from_df(
                trade_history,
                "{}/{}/{}/{}_trade_history.csv".format("reports",matrix.name, name, name),
            )

            return df

    def close_all(self, bot, position_info, trade_history):
        if position_info:
            if position_info["side"] == "long":
                sell = self.sell_market(
                    bot.position["value"], bot.position["size"], bot.position
                )
                # print(sell)
                # print(bot.position)
                bot.exec_order(sell)
                # print(bot.position)
                self.store_transaction(
                    bot.sim,
                    bot.trade_history,
                    bot.position,
                    sell,
                    "END",
                    "sell",
                    sell["fees"],
                    bot.wallet,
                    bot.trade_count,
                    pnl=True,
                )
                bot.close()
            elif position_info["side"] == "short":
                buy = self.buy_market(
                    bot.position["value"], bot.position["size"], bot.position
                )
                bot.exec_order(buy)
                self.store_transaction(
                    bot.sim,
                    bot.trade_history,
                    bot.position,
                    buy,
                    "END",
                    "buy",
                    buy["fees"],
                    bot.wallet,
                    bot.trade_count,
                    pnl=True,
                )
                bot.close()
        trade_history = trade_history.round(
            {"size": 2, "value": 2, "pnl": 2, "fees": 2, "wallet": 2}
        )
        # print(trade_history)


class Plotter:
    def __init__(self):
        pass

    def get_raw_file_for_chart(
        self,
        call_name,
        trade_hist,
        count,
        delta=50,
    ):
        """Returns the Dataframe to make the single trade chart
        input the index OF THE TRADE HISTORY
        dict {raw:raw df for the candlestick, trade : df of the trade FOR THAT COUNT}"""

        raw_file = d.load_df_from_raw_file(call_name)
        # print(raw_file)
        raw_file["Date"] = pd.to_datetime(raw_file["Date"])

        st = trade_hist["Date"].loc[trade_hist["trade_count"] == count].iloc[0]
        end = trade_hist["Date"].loc[trade_hist["trade_count"] == count].iloc[-1]
        td = trade_hist.loc[trade_hist["trade_count"] == count]
        idxst = raw_file["Date"].index[raw_file["Date"] == st].to_list()[0] - delta
        idxend = raw_file["Date"].index[raw_file["Date"] == end].to_list()[0] + delta
        df = d.apply_indics(raw_file.iloc[idxst:idxend])
        return {"raw": df, "trade": td}

    def make_single_trade_graph(self, raw, trade_history, *args):
        """Makes a chart for every trade, takes as inpuut the already formated raw DF and trade DF
        args = the list of indicators to be displayed (BETA)"""
        sell = trade_history.loc[trade_history["side"] == "sell"]
        buy = trade_history.loc[trade_history["side"] == "buy"]
        count = trade_history["trade_count"].iloc[-1]
        pnl = pnl = sum(
            filter(None, trade_history["pnl"].loc[trade_history["motive"] != "INIT"])
        )
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=raw["Date"],
                    open=raw["open"],
                    high=raw["high"],
                    low=raw["low"],
                    close=raw["close"],
                )
            ],
        )
        # fig.show()
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            showlegend=False,
        )
        fig.update_layout(
            title="{} - Value : {} , PNL : {} , ROI : {}%".format(
                trade_history["position side"].iloc[0].upper(),
                round(trade_history["value"].iloc[0], 2),
                round(pnl, 2),
                round(pnl / trade_history["value"].iloc[0] * 100, 2),
            )
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
        for arg in args:
            fig.add_trace(go.Scatter(x=raw["Date"], y=raw[arg], name=arg))
        # fig.show()

        return fig

    def make_chart_trades_report(
        self, matrix_name,call_name, name, trade_history, bot, top=10, save=True
    ):

        """makes a chart for top and worst n trades in the trade history"""
        # Make the ls top and worst HERE
        df = trade_history.sort_values("pnl", ascending=False).dropna()
        lstop = df["trade_count"].head(10).tolist()
        lswor = df["trade_count"].tail(10).tolist()
        lswor = reversed(lswor)
        n = 1
        for count in lstop:
            ch = self.get_raw_file_for_chart(call_name, trade_history, count)
            ch = self.make_single_trade_graph(ch["raw"], ch["trade"])
            if save:
                ch.write_image("reports/{}/{}/top{}.png".format(matrix_name, name, n))
                n += 1
        n = 1
        for count in lswor:
            ch = self.get_raw_file_for_chart(call_name, trade_history, count)
            ch = self.make_single_trade_graph(ch["raw"], ch["trade"])
            if save:
                ch.write_image("reports/{}/{}/worst{}.png".format(matrix_name, name, n))
                n += 1
        fig = self.make_balance_chart(
            bot.sim.raw_df, bot.trade_history, bot.sim.ticker, bot.name
        )
        fig.write_image("reports/{}/{}/perfo.png".format(matrix_name ,name))

    def make_balance_chart(self, raw, trade_history, ticker, name):

        bot_roi = round(
            (trade_history["wallet"].iloc[-1] / trade_history["wallet"].iloc[0] * 100)
            - 100,
            2,
        )
        asset_roi = round((raw["close"].iloc[-1] / raw["close"].iloc[0] * 100) - 100, 2)
        if bot_roi >= asset_roi:
            msg = "Good bot beat the market !"
        else:
            msg = "Bad bot did not outperform the market"
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=raw["Date"], y=raw["close"], name=ticker))
        fig.add_trace(
            go.Scatter(x=trade_history["Date"], y=trade_history["wallet"], name=name),
            secondary_y=True,
        )
        fig.update_layout(
            title="Asset ROI : {}% bot ROI : {}%\n" "{}".format(asset_roi, bot_roi, msg)
        )
        fig.update_yaxes(title_text="<b>Asset price</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Bot balance</b>", secondary_y=True)
        fig.update_layout(
            legend=dict(yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )

        return fig


class Matrix_manager:
    '''For all that is relative to the Matrix'''
    def __init__(self):
        pass

    def name_matrix(self):
        return c.random_name()


    def get_session_results(self, matrix):
        df = None
        for bot in matrix.active_bots:
            if df is None:
                df = b.get_results(matrix, bot, bot.trade_history
                , bot.name, bot.style, bot.preset, bot.sim.raw_df)
            else:
                df = df.append(b.get_results(matrix, bot, bot.trade_history
                , bot.name, bot.style, bot.preset,bot.sim.raw_df), ignore_index=True)

                df.to_csv("reports/{}/{}_report.csv".format(matrix.name, matrix.name))
                df = df.sort_values(by="adj_roi", ascending=False)
        df = df.round(
            {
                "win_rate": 2,
                "pnl": 2,
                "roi": 2,
                "fees": 2,
                "adjusted_pnl": 2,
                "ajusted_roi": 2,
            }
        )
        print(df)

        return df







c = Constructor()
d = DataFrame_manager()
b = Bot_manager()
p = Plotter()
m = Matrix_manager()