import json
from subbots import Fomobot, Bolbot
from constructors import Constructor
import pandas as pd

c = Constructor()


class TestClass:
    def __init__(self) -> None:
        self.bao = "hihi"

    def print(self):
        print(self.thebao)


class Subtestclass(TestClass):
    def __init__(self) -> None:
        super().__init__()
        self.thebao = "haha"


df = pd.read_csv(
    "reports/Janice_the_naughty/Janice_the_naughty_trade_history.csv", index_col=0
)
df = df.sort_values("pnl", ascending=False).dropna()
ls = df["trade_count"].head(10).to_list()
print(df)
print(ls)
