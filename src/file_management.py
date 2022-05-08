"""
Enthält häufig verwendete Funktionen beim Umgang mit Dateien.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import os  # Für Dateisystemzugriffe
from pathlib import Path  # Für Dateipfadangaben

# Imports von Drittanbietern

# Eigene Imports
from debugging import console  # Für farbliche Ausgaben auf der Konsole


def check_file(filename):
    """
    Prüft, ob ein übergebener Pfad zu einer Datei weiter verarbeitet werden kann.
    """
    # Prüfung, ob der Pfad existiert.
    if not Path(filename).exists():
        raise FileNotFoundError(console("Der Pfad", filename, "existiert nicht.", mode="err", perm=True))

    # Prüfung, ob der Pfad auf eine Datei zeigt.
    if not Path(filename).is_file():
        raise FileNotFoundError(console("Der Pfad", filename, "ist keine Datei.", mode="err", perm=True))

    # Prüfung, ob die Datei gelesen werden kann.
    if os.access(Path(filename), os.R_OK) is not True:
        raise PermissionError(console("Die Datei", filename, "ist nicht lesbar.", mode="err", perm=True))

    # Prüfung, ob in die Datei geschrieben werden kann.
    if os.access(Path(filename), os.W_OK) is not True:
        raise PermissionError(console("Die Datei", filename, "ist nicht beschreibbar.", mode="err", perm=True))


def check_dir(dirname):
    """
    Prüft, ob ein übergebener Pfad zu einem Ordner weiter verarbeitet werden kann.
    """
    # Prüfung, ob der Pfad existiert.
    if not Path(dirname).exists():
        raise FileNotFoundError(console("Der Pfad", dirname, "existiert nicht.", mode="err", perm=True))

    # Prüfung, ob der Pfad auf ein Verzeichnis zeigt.
    if not Path(dirname).is_dir():
        raise NotADirectoryError(console("Der Pfad", dirname, "ist kein Ordner.", mode="err", perm=True))

    # Prüfung, ob das Verzeichnis gelesen werden kann.
    if os.access(Path(dirname), os.R_OK) is not True:
        raise PermissionError(console("Das Verzeichnis", dirname, "ist nicht lesbar.", mode="err", perm=True))

    # Prüfung, ob in das Verzeichnis geschrieben werden kann.
    if os.access(Path(dirname), os.W_OK) is not True:
        raise PermissionError(console("Das Verzeichnis", dirname, "ist nicht beschreibbar.", mode="err", perm=True))
