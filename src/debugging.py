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


def info(*message):
    """
    Gibt die Inhalte von message in blauer Farbe auf der Konsole aus, wenn DEBUG aktiv ist.
    """
    if DEBUG:

        mode = 0  # 0 = keine Farbe, 1 = blaue Farbe

        print(f"{Fore.BLUE}Info: ", end="")

        for part in message:
            if mode == 0:
                print(f"{Fore.BLUE}", end="")
                mode = 1
            else:
                print(f"{Style.RESET_ALL}", end="")
                mode = 0

            print(part, end=" ")

        print("")  # Abschließender Zeilenumbruch


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

        print("")  # Abschließender Zeilenumbruch


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

        print("")  # Abschließender Zeilenumbruch
