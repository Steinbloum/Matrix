import json
from subbots import Fomobot, Bolbot
from constructors import Constructor

c = Constructor()

cfg = c.create_bot_config(Fomobot('ETHUSDT15m', 'Fomobot', 1, '5xornothing'))
c.add_to_json('bot_config.json', cfg, 'Fomobot')
