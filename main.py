from matrix import Matrix
from datetime import datetime
from subbots import Bolbot, Fomobot
from inputoutput import Io


io = Io()
start_time = datetime.now()
matrix = Matrix(max_klines=3000, sim_amount=8)
matrix.bots = [
    [Fomobot, "Fomobot", "standard"],
    [Fomobot, "Fomobot", "5xornothing"]
]

matrix.run()
end_time = datetime.now()
print(
    "Analysed {} candles in {}.".format(
        matrix.max_klines * len(matrix.sims), end_time - start_time
    )
)
io.print_warning("SESSION {} TERMINATED".format(matrix.name))
