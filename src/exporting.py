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
from debugging import err


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

    if files != [''] and not DISABLE_BACKUP:
        # Falls ja: alte Konfigurationen sichern
        # Wenn nicht bereits vorhanden, das Sicherungsverzeichnis anlegen
        Path(SAVEDIR_NEW).mkdir(parents=True, exist_ok=True)

        # Dateien in das Verzeichnis kopieren
        for file in files:
            os.rename(WG_DIR + file, SAVEDIR_NEW + file)

        # Sicherungsverzeichnis umbenennen, alte Datensicherung überschreiben
        os.rename(SAVEDIR_NEW, SAVEDIR)

    # Verzeichnis leeren, falls Dateien noch existieren
    for file in files:
        try:
            os.remove(WG_DIR + file)
        except FileNotFoundError:
            continue

    # Serverkonfiguration schreiben
    # TODO refactoring mit Ausgabefunktion, doppelten Code vermeiden: Eine Funktion gibt die Konfiguration als String
    #  zurück, welcher auf die Konsole oder in die Datei geschrieben wird
    f = open(WG_DIR + SERVER_CONFIG_FILENAME, "w")
    f.write("# Serverkonfiguration\n\n")
    f.write("[Interface]\n")

    for parameter in interface_config_parameters:
        if getattr(server, parameter.lower()) != "":
            f.write(parameter + " = " + getattr(server, parameter.lower()) + "\n")

    # Clients hinterlegen: Bezeichnung, öffentlicher Schlüssel, IP-Adresse im VPN
    for client in server.clients:
        f.write("\n[Peer]\n")
        if client.name != "":
            f.write("# Name = " + client.name + "\n")
        for parameter in peer_config_parameters:
            if getattr(client, "client_" + parameter.lower()) != "":
                f.write(parameter + " = " + getattr(client, "client_" + parameter.lower()) + "\n")

    f.close()

    # Clientkonfigurationen schreiben
    # TODO Was passiert mit Clients ohne Attribut filename und name?
    for i in range(len(server.clients)):
        client = server.clients[i]
        if client.filename != "":
            f = open(WG_DIR + client.filename, "w")
        elif client.name != "":
            f = open(WG_DIR + client.name, "w")
        else:
            err("Fehler: Client", i, "enthält keine Bezeichnung. Diese ist notwendig für den Export.")
            # TODO Dateien aus der Datensicherung müssen wiederhergestellt werden
            return

        f.write("[Interface]\n")
        if client.name != "":
            f.write("# Name = " + client.name + "\n")
        for parameter in interface_config_parameters:
            if getattr(client, parameter.lower()) != "":
                f.write(parameter + " = " + getattr(client, parameter.lower()) + "\n")

        f.write("\n[Peer]\n")
        for parameter in peer_config_parameters:
            if getattr(client, parameter.lower()) != "":
                f.write(parameter + " = " + getattr(client, parameter.lower()) + "\n")

        f.write("\n")
