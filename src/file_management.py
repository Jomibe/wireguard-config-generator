"""
Enthält häufig verwendete Funktionen beim Umgang mit Dateien.
"""

# Imports aus Standardbibliotheken
import os  # Für Dateisystemzugriffe
from pathlib import Path  # Für Dateipfadangaben

# Imports von Drittanbietern
from colorama import Fore, Style  # Für vom Betriebssystem unabhängige farbige Ausgaben


def check_file(filename):
    """
    Prüft, ob ein übergebener Pfad zu einer Datei weiter verarbeitet werden kann.
    """
    # Prüfung, ob der Pfad existiert.
    if not Path(filename).exists():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {filename} existiert nicht.{Style.RESET_ALL}")

    # Prüfung, ob der Pfad auf eine Datei zeigt.
    if not Path(filename).is_file():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {filename} ist keine Datei.{Style.RESET_ALL}")

    # Prüfung, ob die Datei gelesen werden kann.
    if os.access(Path(filename), os.R_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Die Datei {filename} ist nicht lesbar.{Style.RESET_ALL}")

    # Prüfung, ob in die Datei geschrieben werden kann.
    if os.access(Path(filename), os.W_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Die Datei {filename} ist nicht beschreibbar.{Style.RESET_ALL}")


def check_dir(dirname):
    """
    Prüft, ob ein übergebener Pfad zu einem Ordner weiter verarbeitet werden kann.
    """
    # Prüfung, ob der Pfad existiert.
    if not Path(dirname).exists():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {dirname} existiert nicht.{Style.RESET_ALL}")

    # Prüfung, ob der Pfad auf ein Verzeichnis zeigt.
    if not Path(dirname).is_dir():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {dirname} ist kein Ordner.{Style.RESET_ALL}")

    # Prüfung, ob das Verzeichnis gelesen werden kann.
    if os.access(Path(dirname), os.R_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Das Verzeichnis {dirname} ist nicht lesbar.{Style.RESET_ALL}")

    # Prüfung, ob in das Verzeichnis geschrieben werden kann.
    if os.access(Path(dirname), os.W_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Das Verzeichnis {dirname} ist nicht beschreibbar.{Style.RESET_ALL}")
