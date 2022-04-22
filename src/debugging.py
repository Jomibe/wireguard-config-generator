"""
Diese Datei enthält für das Debugging notwendige Ausgabefunktionen
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken

# Imports von Drittanbietern
from colorama import Fore, Style

# Eigene Imports
from constants import DEBUG


def info(*message, end=None, quiet=None, no_space=None):
    """
    Gibt die Inhalte von message in abwechselnd in blauer und weißer Farbe auf der Konsole aus, wenn DEBUG aktiv ist.
    end gibt das Zeilenende für print() an.
    Wenn quiet=True, dann wird Info: weggelassen.
    Wenn no_space=True, werden keine Leerzeichen zwischen den Parametern ausgegeben
    """
    if DEBUG:

        mode = 0  # 0 = keine Farbe, 1 = blaue Farbe

        if quiet is not True:
            print(f"{Fore.BLUE}Info: ", end="")

        for part in message:
            if mode == 0:
                print(f"{Fore.BLUE}", end="")
                mode = 1
            else:
                print(f"{Style.RESET_ALL}", end="")
                mode = 0

            if no_space:
                print(part, end="")
            else:
                print(part, end=" ")

        # Zeilenende kann durch den Parameter end beeinflusst werden
        if end is None:
            print(f"{Style.RESET_ALL}")  # Abschließender Zeilenumbruch
        else:
            print(f"{Style.RESET_ALL}", end=end)  # Parameter end wird an print() weitergegeben


def warn(*message):
    """
    Gibt die Inhalte von message in gelber Farbe auf der Konsole aus, wenn DEBUG aktiv ist.
    """
    if DEBUG:

        mode = 0  # 0 = keine Farbe, 1 = gelbe Farbe

        print(f"{Fore.YELLOW}Warnung: ", end="")

        for part in message:
            if mode == 0:
                print(f"{Fore.YELLOW}", end="")
                mode = 1
            else:
                print(f"{Style.RESET_ALL}", end="")
                mode = 0

            print(part, end=" ")

        print(f"{Style.RESET_ALL}")  # Abschließender Zeilenumbruch


def err(*message):
    """
    Gibt die Inhalte der Liste message in roter Farbe auf der Konsole aus, wenn DEBUG aktiv ist.
    """
    if DEBUG:

        mode = 0  # 0 = keine Farbe, 1 = rote Farbe

        print(f"{Fore.RED}Fehler: ", end="")

        for part in message:
            if mode == 0:
                print(f"{Fore.RED}", end="")
                mode = 1
            else:
                print(f"{Style.RESET_ALL}", end="")
                mode = 0

            print(part, end=" ")

        print(f"{Style.RESET_ALL}")  # Abschließender Zeilenumbruch


def erfolg(*message):
    """
    Gibt die Inhalte von message in blauer Farbe auf der Konsole aus, wenn DEBUG aktiv ist.
    """
    if DEBUG:

        mode = 0  # 0 = keine Farbe, 1 = blaue Farbe

        print(f"{Fore.GREEN}Erfolg: ", end="")

        for part in message:
            if mode == 0:
                print(f"{Fore.GREEN}", end="")
                mode = 1
            else:
                print(f"{Style.RESET_ALL}", end="")
                mode = 0

            print(part, end=" ")

        print(f"{Style.RESET_ALL}")  # Abschließender Zeilenumbruch
