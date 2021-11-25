import json
from subbots import Fomobot, Bolbot
from constructors import Constructor

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


tst = Subtestclass()
tst.print()

str = "True"
str2 = "False"
str3 = "qsfqdsf"

print("{}{}".format(eval(str), eval(str2)))
position = None
if position:
    print(True)
else:
    print(False)
