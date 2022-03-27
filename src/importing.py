"""
Enthält alle Funktionen für das Importieren von Konfigurationen auf dem Dateisystem in interne Datenstrukturen.
"""

# Öffentliche Imports
import glob  # Für das Auffinden von Konfigurationsdateien mittels Wildcard
import os  # Für Dateisystemzugriffe
from pathlib import Path  # Für Dateipfadangaben
import re  # Für das Parsen von Konfigurationsdateien


# Interne Imports
from constants import CONFIG_PARAMETERS
from constants import WG_DIR
from constants import DEBUG


def import_configurations(server):
    """
    Importiert alle VPN-Konfigurationen im Wireguard-Verzeichnis.
    """

    # Prüfung, ob der Pfad existiert.
    if not Path(WG_DIR).exists():
        raise SystemExit(f"Fehler: Der Pfad {WG_DIR} existiert nicht.")

    # Prüfung, ob der Pfad auf ein Verzeichnis zeigt.
    if not Path(WG_DIR).is_dir():
        raise SystemExit(f"Fehler: Der Pfad {WG_DIR} ist kein Ordner.")

    # Prüfung, ob das Verzeichnis gelesen werden kann.
    if os.access(Path(WG_DIR), os.R_OK) is not True:
        SystemExit(f"Fehler: Das Verzeichnis {WG_DIR} ist nicht lesbar.")

    # Prüfung, ob in das Verzeichnis geschrieben werden kann.
    if os.access(Path(WG_DIR), os.W_OK) is not True:
        SystemExit(f"Fehler: Das Verzeichnis {WG_DIR} ist nicht beschreibbar.")

    # Falls nicht: alle Dateien im Verzeichnis sollen entfernt werden, es wird eine neue Konfiguration angelegt.

    # Einlesen der Clientkonfigurationen *.conf

    # Liste mit Dateinamen erstellen
    list_client_configuration_filenames = glob.glob(f"{WG_DIR}*.conf")

    # Dateiname der Serverkonfiguration ausschließen und damit prüfen, ob diese existiert
    try:
        list_client_configuration_filenames = glob.glob(f"{WG_DIR}*.conf")  # TODO doppelt notwendig?
        list_client_configuration_filenames.remove(server.filename)
    except ValueError:
        print("Warnung: Keine Serverkonfiguration wg0.conf gefunden.")

    # Zu importierende Clientkonfigurationen anzeigen
    if DEBUG:
        print(f"Info: Folgende Clientkonfigurationen wurden gefunden: {list_client_configuration_filenames}")

    # Konfigurationen importieren

    # ..des Servers

    # ..der Clients
    for file in list_client_configuration_filenames:

        server.clients.append({})  # Für jede gefundene Clientkonfiguration wird dem Server-Objekt ein dict hinzugefügt

        with open(file) as config:
            for line in config:
                # Die Bezeichnung ist kein offizieller Parameter (aber ein INI-Standard) und wird daher gesondert
                # behandelt.
                match = re.search('^#', line,
                                  re.IGNORECASE)  # Die Bezeichnung steht in der ersten Zeile als Kommentar (optional)
                if match:
                    if "description" not in server.clients[-1]:  # Nur die erste kommentierte Zeile wird gespeichert
                        server.clients[-1]["description"] = re.split("^# ", line)[
                            1]  # Die ersten beiden Zeichen ('# ') werden abgeschnitten
                # Nun folgen alle offiziellen Parameter
                for parameter in CONFIG_PARAMETERS:
                    match = re.search(f'^{parameter} = ', line, re.IGNORECASE)
                    if match:
                        if parameter not in server.clients[-1]:
                            server.clients[-1][parameter] = re.split(f"^{parameter} = ", line, re.IGNORECASE)

        for client in server.clients:
            if DEBUG:
                print("Client " + str(client["description"]) + " hat den privaten Schlüssel ")  # + client["private_key"])

        # Parameter importieren

    # Wenn keine Bezeichnung vorhanden ist, Dateiname verwenden

    # Bei Einlesefehlern (unbekannte Parameter, Syntaxfehler): Ursache melden, mit nächster Datei fortfahren.
