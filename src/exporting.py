"""
Enthält alle Funktionen für das Exportieren von Konfigurationen aus dem Arbeitsspeicher auf das Dateisystem.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import os
from pathlib import Path

# Imports von Drittanbietern

# Eigene Imports
from constants import DISABLE_BACKUP
from constants import INTERFACE_CONFIG_PARAMETERS
from constants import PEER_CONFIG_PARAMETERS
from constants import SAVEDIR
from constants import SAVEDIR_NEW
from constants import SERVER_CONFIG_FILENAME
from constants import WG_DIR
from debugging import err, info


def export_configurations(server):
    """
    Exportiert die Konfigurationen aus dem Arbeitsspeicher in das Wireguard-Verzeichnis.
    """

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen der Interface-Sektion. Verwendung
    # von CamelCase
    interface_config_parameters = [parameter for parameter in INTERFACE_CONFIG_PARAMETERS]

    # Vorbereitung auf Prüfung auf Konfigurationsparameter der Peer-Sektion. Verwendung von CamelCase
    peer_config_parameters = [parameter for parameter in PEER_CONFIG_PARAMETERS]

    # Prüfung, ob Konfigurationen vorhanden sind
    files = os.listdir(WG_DIR)

    # Entfernung des Ordners einer vorherigen Datensicherung aus der Liste, falls vorhanden
    if SAVEDIR.strip("/") in files:
        info("Vorherige Datensicherung erkannt")
        files.remove(SAVEDIR.strip("/"))

    info("Enthaltene Dateien in ", WG_DIR, ": ", str(files), no_space=True)

    if files != [''] and not DISABLE_BACKUP:
        # Falls ja: alte Konfigurationen sichern
        # Wenn nicht bereits vorhanden, das Sicherungsverzeichnis anlegen
        info("Erstelle Ordner", WG_DIR + SAVEDIR_NEW)
        Path(WG_DIR + SAVEDIR_NEW).mkdir(parents=True, exist_ok=True)

        # Dateien in das Verzeichnis verschieben
        for file in files:
            info("Verschiebe Datei", WG_DIR + file, "in", WG_DIR + SAVEDIR_NEW)
            os.rename(WG_DIR + file, WG_DIR + SAVEDIR_NEW + file)

        # Sicherungsverzeichnis umbenennen, alte Datensicherung überschreiben
        info("Ordner", WG_DIR + SAVEDIR_NEW, "wird umbenannt in", WG_DIR + SAVEDIR)
        os.rename(WG_DIR + SAVEDIR_NEW, WG_DIR + SAVEDIR)

    # Verzeichnis leeren, falls Dateien noch existieren
    for file in files:
        if Path(file).exists():
            info("Entferne Datei", file)
            os.remove(WG_DIR + file)

    # Serverkonfiguration schreiben
    # TODO refactoring mit Ausgabefunktion, doppelten Code vermeiden: Eine Funktion gibt die Konfiguration als String
    #  zurück, welcher auf die Konsole oder in die Datei geschrieben wird
    f = open(WG_DIR + SERVER_CONFIG_FILENAME, "w")
    info("Schreibe Serverkonfiguration", WG_DIR + SERVER_CONFIG_FILENAME)
    f.write("# Serverkonfiguration\n\n")
    f.write("[Interface]\n")

    info("Die Interface-Sektion enthält folgende Parameter:", end="")

    for parameter in interface_config_parameters:
        info("", parameter, ", ", end="", quiet=True, no_space=True)
        if getattr(server, parameter.lower()) != "":
            f.write(parameter + " = " + getattr(server, parameter.lower()) + "\n")
    info(quiet=True)  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

    # Clients hinterlegen: Bezeichnung, öffentlicher Schlüssel, IP-Adresse im VPN
    for client in server.clients:
        info("Schreibe Peer-Sektion mit folgenden Parametern:", end="")
        f.write("\n[Peer]\n")
        if client.name != "":
            f.write("# Name = " + client.name + "\n")
            info("", "Name", ", ", end="", quiet=True, no_space=True)
        for parameter in peer_config_parameters:
            info("", parameter, ", ", end="", quiet=True, no_space=True)
            if getattr(client, "client_" + parameter.lower()) != "":
                f.write(parameter + " = " + getattr(client, "client_" + parameter.lower()) + "\n")
        info(quiet=True)  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

    f.close()

    # Clientkonfigurationen schreiben
    # TODO Was passiert mit Clients ohne Attribut filename und name?
    for i in range(len(server.clients)):
        client = server.clients[i]
        if client.filename != "":
            f = open(WG_DIR + client.filename, "w")
            info("Schreibe Konfiguration für Client", i + 1, "in", WG_DIR + client.filename)
        elif client.name != "":
            f = open(WG_DIR + client.name, "w")
            info("Schreibe Konfiguration für Client", i + 1, "in", WG_DIR + client.name)
        else:
            err("Fehler: Client", i+1, "enthält keine Bezeichnung. Diese ist notwendig für den Export.")
            # TODO Dateien aus der Datensicherung müssen wiederhergestellt werden
            return

        f.write("[Interface]\n")
        info("Die Interface-Sektion enthält folgende Parameter:", end="")
        if client.name != "":
            f.write("# Name = " + client.name + "\n")
            info("", "Name", ", ", end="", quiet=True, no_space=True)
        for parameter in interface_config_parameters:
            if getattr(client, parameter.lower()) != "":
                f.write(parameter + " = " + getattr(client, parameter.lower()) + "\n")
                info("", parameter, ", ", end="", quiet=True, no_space=True)
        info(quiet=True)  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

        f.write("\n[Peer]\n")
        info("Die Peer-Sektion enthält folgende Parameter:", end="")
        for parameter in peer_config_parameters:
            if getattr(client, parameter.lower()) != "":
                info("", parameter, ", ", end="", quiet=True, no_space=True)
                f.write(parameter + " = " + getattr(client, parameter.lower()) + "\n")
        info(quiet=True)  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

        f.close()
