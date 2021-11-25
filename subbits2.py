from bot import Bot
from simulators import Simulator
from constructor2 import*

class Bolbot(Bot):
    '''Enters on one range on bolinger, exits on the other, 
    config is :
    trade amount : how much of the wallet you go for each position ex 0.5
    sl trigger : how much before selling in red ex : 0.98
    wait reentry : trade market when the candles reenter the range, bool'''
    def __init__(self, sim, style, preset, wallet=1000):
        super().__init__(sim, style, preset, wallet=wallet)


    def get_signal(self):
        if 




    def run(self):
        
        b.update_value(self.sim, self.position)
        signal = self.get_signal()
        self.buy_signal = signal['buy']
        self.sell_signal = signal['sell']
        self.sl_signal = signal['sl']


