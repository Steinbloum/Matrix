from simulators import Simulator
from subbits2 import Bolbot
from constructor2 import c, p, d, b,m
from inputoutput import Io

io = Io()


class Matrix:
    def __init__(
        self,
        sim_amount=5,
        balance=10000,
        min_loop=5000,
        save_files=True,
        random_list=True,
    ):

        self.name = c.random_name()
        self.sim_amount = sim_amount
        self.sims = []
        self.bots = []
        self.active_bots = []
        self.balance = balance
        self.min_loop = min_loop
        self.results = None
        c.create_dir("reports/{}".format(self.name))
        io.print_bull("SESSION {} ACTIVE".format(self.name.upper()))

    def run(self):

        # init sims
        for sim in c.get_random_sim_list(self.sim_amount, self.min_loop):
            sim = Simulator(sim, self.min_loop)
            self.sims.append(sim)
        # init bots
        for sim in self.sims:
            for bot in self.bots:
                bot = bot[0](self, sim, bot[1], bot[2])
                self.active_bots.append(bot)
                # print(bot.name)
        for n in range(self.min_loop):
            if n%100 ==0 :
                print('analysing candle {}'.format(n))
            for sim in self.sims:
                sim.update_df(n)
                for bot in self.active_bots:
                    bot.run_main()

        for bot in self.active_bots:
            b.close_all(bot, bot.position, bot.trade_history)
            p.make_chart_trades_report(
                matrix.name, bot.sim.ticker + bot.sim.tf, bot.name, bot.trade_history, bot
            )
        m.get_session_results(self)
        print(matrix.name)


matrix = Matrix(min_loop=1000, sim_amount=10)
matrix.bots = [[Bolbot, "Bolbot", "standard"]]
matrix.run()
