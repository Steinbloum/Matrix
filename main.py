from matrix import Matrix
from datetime import datetime
from subbots import Bolbot
from inputoutput import Io


io = Io()
start_time = datetime.now()
matrix = Matrix(max_klines=2000, sim_amount=8)
matrix.bots = [
    [Bolbot, "Bolbot", "tight"],
    [Bolbot, "Bolbot", "loose"],
]

matrix.run()
end_time = datetime.now()
print(
    "Analysed {} candles in {}.".format(2000 * len(matrix.sims), end_time - start_time)
)
io.print_warning("SESSION {} TERMINATED".format(matrix.name))
