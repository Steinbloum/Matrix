from datetime import datetime
from constructors import Constructor
from inputoutput import Io
from simulators import Simulator
from subbots import Bolbot
import time
import json
import os

io = Io()
c = Constructor()


class Matrix:
    def __init__(
        self,
        sim_amount=10,
        balance=100000,
        max_klines=5000,
        save_files=True,
        random=True,
    ):

        self.name = c.create_name()
        self.sims = []
        self.active_sims = []
        self.bots = []
        self.active_bots = []
        self.balance = balance
        self.simulator = None
        self.max_klines = max_klines
        self.save = save_files
        self.random = random
        self.sim_amount = sim_amount
        c.create_dir("reports/{}".format(self.name))
        io.print_bull("SESSION {} INITIATED".format(self.name))

    def init_bots(self):
        for sim in self.active_sims:
            for bot in self.bots:
                # print(bot)
                bot = bot[0](sim, bot[1], self.balance * 0.1, bot[2])
                print(bot.style)
                print(bot.preset)
                print(bot.reentry)
                print(type(bot.reentry))
                input()
                bot.name_bot()
                self.active_bots.append(bot)
            for bot in self.active_bots:
                # bot.wake_up()
                bot.set_matrix_name(self.name)

    def add_bot(self, bot):
        self.bots.append(bot)

    def run(self):
        try:
            self.init_sims()
            self.init_bots()

            for n in range(self.max_klines):
                if n % 100 == 0:
                    io.print_statement("analasing kline {}".format(n))
                for sim in self.active_sims:
                    sim.update_df(n)
                    for bot in self.active_bots:
                        bot.set_row(n)
                        bot.run_main()
            for bot in self.active_bots:

                if bot.position_open:
                    updated = c.update_position_infos(
                        bot.sim, bot.trade_history, bot.trade_count
                    )
                    if bot.position_side == "long":
                        value = updated["position value"]
                        size = updated["position size"]
                        bot.market_trade(value, size, "tp", "sell", get_pnl=True)

                        if (
                            c.update_position_infos(
                                bot.sim, bot.trade_history, bot.trade_count
                            )["position size"]
                            == 0
                        ):
                            bot.close()
                    elif bot.position_side == "short":

                        value = updated["position value"]
                        size = updated["position size"]
                        bot.market_trade(-value, -size, "tp", "buy", get_pnl=True)

                        if (
                            c.update_position_infos(
                                bot.sim, bot.trade_history, bot.trade_count
                            )["position size"]
                            == 0
                        ):
                            bot.close()

            self.get_matrix_results()
            io.print_statement("Generating reports, can take a while")
            for bot in self.active_bots:
                bot.get_reports()
        except IndexError as e:
            print(e)
            os.open("reports/{}".format(self.name))

    def get_matrix_results(self):
        df = None
        for bot in self.active_bots:
            if df is None:
                df = bot.get_results(self.name)
            else:
                df = df.append(bot.get_results(self.name), ignore_index=True)

                df.to_csv("reports/{}/{}_report.csv".format(self.name, self.name))
                df = df.sort_values(by="adjusted_roi", ascending=False)
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

    def add_bot_to_json(self):
        for bot in self.active_bots:
            bot_params = json.dumps(
                {
                    bot.name: {
                        "type": bot.type,
                        "buy_trigger": self.buy_trigger,
                        "sell_trigger": self.sell_trigger,
                        "trade_amount": self.trade_amount,
                        "value_sl": self.value_sl,
                        "set_side": self.set_side,
                    }
                }
            )

    def init_sims(self):
        if self.random:
            print("random choosing")
            self.sims = c.get_random_sim_list(
                self.sim_amount, conditions=True, max_klines=self.max_klines
            )
        print(self.sims)

        for sim in self.sims:
            if c.check_for_data(sim, self.max_klines):
                sim = Simulator(sim, max_rows=self.max_klines)
                self.active_sims.append(sim)
            else:
                io.print_warning("NO DATA ON {}".format(sim))
