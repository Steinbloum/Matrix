from bot import Bot
from simulators import Simulator
from constructor2 import c, d, b


class Bolbot(Bot):
    """Enters on one range on bolinger, exits on the other,
    config is :
    trade amount : how much of the wallet you go for each position ex 0.5
    sl trigger : how much before selling in red ex : 0.98
    wait reentry : trade market when the candles reenter the range, bool
    bias : 'bull' neutral' or 'bear'"""

    def __init__(self, sim, style, preset, wallet=1000):
        super().__init__(sim, style, preset, wallet=wallet)
        self.params = b.load_attributes("bot_config.json", self.style, preset)
        self.trade_amount = self.params["trade amount"]
        self.sl_trigger = self.params["trigger_sl"]
        self.wait = eval(self.params["wait for reentry"])
        self.bias = self.params["bias"]

    def get_signal(self):
        dicta = {}
        if self.position is not None:
            if (
                self.position["value"]
                <= b.get_entry_value(self.trade_history, self.trade_count)
                * self.params["trigger_sl"]
            ):
                dicta['sl'] = True
            else:
                dicta['sl'] = False
        dicta['sl' = False
        if self.sim.get_last("bolupcross") != 0:
            dicta['sell'] = True
        elif self.sim.get_last("boldowncross") != 0:
            dicta['buy'] = True
        else:
            dicta['sell'] = False
            dicta['buy'] = False
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
            }
        }
        return params_dict


sim = Simulator("ETHUSDT15m", 2000)

# c.add_to_json(
#     "bot_config.json",
#     b.create_config("bot_config.json", Bolbot(sim, "Bolbot", "standard", 0)),
#     "Bolbot",
# )

bot = Bolbot(sim, "Bolbot", "standard")
print(bot.sl_trigger)
print(sim.df)
print(sim.get_last("close"))
for n in range(500):
    sim.update_df(n)
    bot.run_main()
    print(bot.trade_history)
