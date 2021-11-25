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
        pass

    def run(self):

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
