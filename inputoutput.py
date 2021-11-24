from rich.console import Console
import os
import glob

console = Console()

class Io:

    """Une classe pour manager tous les inputs et outputs"""

    def var_selector(self, titre, *args):

        """Crée un menu de selection pour des variables, return la variable selectionnée
        titre = Le message a diplay
        args = les variables"""
        # print(args)
        if type(args) is list:
            print("arg is list")
        """clear()"""
        console.print(titre, style="bold yellow")
        dicta = {}
        dicta[0] = "Annuler"
        a = 1
        for var in args:
            dicta[a] = var
            a += 1
        dicta[0] = dicta.pop(0)
        for key, value in dicta.items():
            print("{} ({})".format(value, key))
        choice_run = True
        while choice_run:
            choice = input("")
            try:
                choice = int(choice)
            except ValueError:
                print("Entrer un des choix proposés")
                continue
            choice = int(choice)
            if choice > len(dicta) - 1:
                print("Entrer un des choix proposés")
                continue
            choice_run = False
            return dicta[choice]

    def func_selector(self, titre, *args):
        """Crée un menu de selection pour des fonctions, return la fonction
        titre = le message a display
        args = (le nom de la fction pour le choix,la fction)"""
        # clear()
        console.print(titre, style="yellow bold")
        dicta = {}
        dicta[0] = ("Annuler", "Annuler")
        a = 1
        for item in args:
            dicta[a] = (item[0], item[1])
            a += 1
        dicta[0] = dicta.pop(0)
        for key, value in dicta.items():
            print("{} ({})".format(value[0], key))
        choice_run = True
        while choice_run:
            choice = input("")
            try:
                choice = int(choice)
            except ValueError:
                print("Entrer un des choix proposés")
                continue
            choice = int(choice)
            if choice > len(dicta) - 1:
                print("Entrer un des choix proposés")
                continue
            choice_run = False
            if choice == 0:
                return "Annuler"
            else:
                return dicta[choice][1]()

    def input_hours(self, poste):

        """Verifie aue l' input est au bon format, arg = poste"""
        run = True
        while run:
            _input = input("Entrer le nombre d'heures de {} : ".format(poste))
            try:
                input == float(_input)
            except ValueError:
                print("Entrer une valeur numerique, ducon\n")
                continue
            _input = float(_input)
            return _input

    def input_int(self):
        """Verifie que l'input est un int"""
        run = True
        while run:
            _input = input()
            try:
                _input == int(_input)
            except ValueError:
                print("Entrer une valeur numerique\n")
                continue
            _input = int(_input)
            run = False
            # print("input is {}".format(_input))
        return _input

    def input_str(self):
        _input = str(input())
        return _input

    def input_float(self):
        """Verifie que l'input est un float"""
        run = True
        while run:
            _input = input()
            try:
                _input == float(_input)
            except ValueError:
                print("Entrer une valeur numerique\n")
                continue
            _input = float(_input)
            return _input

    def separator(self):
        print("\n" "***\n")

    def valider_infos(self):
        """Prompt un message de confirmation, retourne bool"""
        _input = io.var_selector("Valider les infos ?", "Oui", "non")
        if _input == "Oui":
            _input = True
        else:
            _input = False
        return _input

    def print_choice(self, msg):
        """Print un texte en bold yellow"""
        console.print(msg, style="yellow bold")

    def print_statement(self, msg):
        """Print un texte en bold cyan"""
        console.print(msg, style="cyan bold")

    def print_warning(self, msg):
        """Print un texte en bold cyan"""
        console.print(msg, style="red bold")

    def print_bear(self, msg):
        """Print un texte en bold red"""
        console.print(msg, style="red bold")

    def print_bull(self, msg):
        """Print un texte en bold green"""
        console.print(msg, style="green bold")


io = Io()