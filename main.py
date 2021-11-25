from matrix import Matrix
from datetime import datetime
from subbots import *
from inputoutput import Io


io = Io()
start_time = datetime.now()
matrix = Matrix(max_klines=1500, sim_amount=2)
matrix.bots = [[Bolibot, "Bolibot", "standard"], [Bolibot, "Bolibot", "waiter"]]

matrix.run()
end_time = datetime.now()
print(
    "Analysed {} candles in {}.".format(
        matrix.max_klines * len(matrix.sims), end_time - start_time
    )
)
io.print_warning("SESSION {} TERMINATED".format(matrix.name))
