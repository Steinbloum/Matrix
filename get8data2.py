from constructors import Constructor
import os
import time
from datetime import datetime

start = datetime.now()
c = Constructor()
path = "raw_files"

ls = c.get_pair_list()
print(ls)
lstf = ["1h", "30m"]

for pair in ls:
    for tf in lstf:
        c.get_historical_klines_from_binance(pair, tf, "01/01/2015")
print("done")
end = datetime.now()
print("Done in {}".format(end - start))
