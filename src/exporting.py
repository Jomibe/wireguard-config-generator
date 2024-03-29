"""
Enthält alle Funktionen für das Exportieren von Konfigurationen aus dem Arbeitsspeicher auf das Dateisystem.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import os
from pathlib import Path

# Imports von Drittanbietern
from shutil import rmtree

# Eigene Imports
from constants import DISABLE_BACKUP
from constants import INTERFACE_CONFIG_PARAMETERS
from constants import PEER_CONFIG_PARAMETERS
from constants import SAVEDIR
from constants import SAVEDIR_NEW
from constants import SERVER_CONFIG_FILENAME
from constants import WG_DIR
from debugging import console


def export_configurations(server):
    """
    Exportiert die Konfigurationen aus dem Arbeitsspeicher in das Wireguard-Verzeichnis.
    """

    # Prüfung, ob Konfigurationen vorhanden sind
    files = os.listdir(WG_DIR)

    # Entfernung des Ordners einer vorherigen Datensicherung aus der Liste, falls vorhanden
    if SAVEDIR.strip("/") in files:
        console("Vorherige Datensicherung erkannt", mode="info")
        files.remove(SAVEDIR.strip("/"))

    console("Enthaltene Dateien in ", WG_DIR, ": ", str(files), mode="info", no_space=True)

    if files != [''] and not DISABLE_BACKUP:
        # Falls ja: alte Konfigurationen sichern
        # Wenn nicht bereits vorhanden, das Sicherungsverzeichnis anlegen
        console("Erstelle Ordner", WG_DIR + SAVEDIR_NEW, mode="info")
        Path(WG_DIR + SAVEDIR_NEW).mkdir(parents=True, exist_ok=True)

        # Dateien in das Verzeichnis verschieben
        for file in files:
            console("Verschiebe Datei", WG_DIR + file, "in", WG_DIR + SAVEDIR_NEW, mode="info")
            os.rename(WG_DIR + file, WG_DIR + SAVEDIR_NEW + file)

        # Sicherungsverzeichnis umbenennen, alte Datensicherung überschreiben
        console("Ordner", WG_DIR + SAVEDIR_NEW, "wird umbenannt in", WG_DIR + SAVEDIR, mode="info")
        # Wenn SAVEDIR Dateien enthält, kann os.replace diesen nicht entfernen
        rmtree(WG_DIR + SAVEDIR, ignore_errors=True)
        os.replace(Path(WG_DIR + SAVEDIR_NEW), Path(WG_DIR + SAVEDIR))  # os.replace funktioniert unter Unix und Windows

    # Verzeichnis leeren, falls Dateien noch existieren
    for file in files:
        if Path(file).exists():
            console("Entferne Datei", file, mode="info")
            os.remove(WG_DIR + file)

    # Serverkonfiguration schreiben
    with open(WG_DIR + SERVER_CONFIG_FILENAME, "w", encoding='utf-8') as server_config_file:
        console("Schreibe Serverkonfiguration", WG_DIR + SERVER_CONFIG_FILENAME, mode="info")
        server_config_file.write(config_to_str(server, 0))
        server_config_file.close()

    # Clientkonfigurationen schreiben
    index = 0
    for client in server.clients:
        index = index + 1
        if client.filename != "":
            client_config_filename = client.filename
            console("Schreibe Konfiguration für Client", index, "in", WG_DIR + client_config_filename, mode="info")
        elif client.name != "":
            client_config_filename = WG_DIR + f"{client.name}".replace(" ", "_") + ".conf"
            console("Schreibe Konfiguration für Client", index, "in", WG_DIR + client_config_filename, mode="info")
        else:
            client_config_filename = f"{WG_DIR}Client_{index}.conf"
            console("Schreibe Konfiguration für Client", index, "in", WG_DIR + client_config_filename, mode="info")

        with open(client_config_filename, "w", encoding='utf-8') as client_config_file:
            client_config_file.write(config_to_str(server, index))
            client_config_file.close()


def config_to_str(server, choice):
    """
    Gibt ein String-Objekt zurück, welches die Konfiguration eines beliebigen Clients enthält. choice enthält die
    Angabe, welcher Client ausgegeben werden soll. 0 steht für den Server.
    """

    # Vorbereitung auf Prüfung auf Konfigurationsparameter der Peer-Sektion. Verwendung von CamelCase
    peer_config_parameters = list(PEER_CONFIG_PARAMETERS)

    config_str = ""

    try:
        client_id = int(choice)
    except ValueError:
        console("Eingabe einer Zahl erwartet.", perm=True, mode="err")
        return ""

    if client_id == 0:
        # Serverkonfiguration schreiben
        config_str = config_str + interface_to_str(server)

        # Clients hinterlegen: Bezeichnung, öffentlicher Schlüssel, IP-Adresse im VPN
        for client in server.clients:
            console("Schreibe Peer-Sektion mit folgenden Parametern:", end="", mode="info")
            config_str = config_str + "\n[Peer]\n"
            if client.name != "":
                config_str = config_str + "# Name = " + client.name + "\n"
                console("", "Name", ", ", end="", quiet=True, no_space=True, mode="info")
            for parameter in peer_config_parameters:
                console("", parameter, ", ", end="", quiet=True, no_space=True, mode="info")
                if getattr(client, "client_" + parameter.lower()) != "":
                    config_str = config_str + parameter + " = " + str(getattr(client, "client_" + parameter.lower())) \
                                 + "\n"
            console(quiet=True, mode="info")  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

        return config_str

    # else
    try:
        if len(server.clients) < client_id:
            console("Konfiguration", client_id, "existiert nicht", perm=True, mode="err")
            return ""
    # Wenn das Attribut clients nicht vorhanden ist, ist server nicht von der Klasse ServerConfig
    except AttributeError:
        console("Keine Konfiguration im Arbeitsspeicher hinterlegt.", perm=True, mode="err")
        return ""

    config_str = config_str + interface_to_str(server.clients[client_id-1])

    config_str = config_str + "\n[Peer]\n"
    console("Die Peer-Sektion enthält folgende Parameter:", end="", mode="info")
    if server.name != "":
        config_str = config_str + "# Name = " + server.name + "\n"
        console("", "Name", ", ", end="", quiet=True, no_space=True, mode="info")
    for parameter in peer_config_parameters:
        if getattr(server.clients[client_id-1], parameter.lower()) != "":
            console("", parameter, ", ", end="", quiet=True, no_space=True, mode="info")
            config_str = config_str + parameter + " = " + str(getattr(server.clients[client_id-1],
                                                                      parameter.lower())) + "\n"
    console(quiet=True, mode="info")  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

    return config_str


def interface_to_str(peer):
    """
    Gibt die Interface-Sektion eines Peers zurück. Ein Peer kann ein Server oder Client sein, beide haben den selben
    Parameterumfang in der Interface-Sektion.
    """

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen der Interface-Sektion. Verwendung
    # von CamelCase
    interface_config_parameters = list(INTERFACE_CONFIG_PARAMETERS)

    config_interface_str = ""

    config_interface_str = config_interface_str + "[Interface]\n"

    console("Die Interface-Sektion enthält folgende Parameter:", end="", mode="info")

    if peer.name != "":
        config_interface_str = config_interface_str + "# Name = " + peer.name + "\n"
        console("", "Name", ", ", end="", quiet=True, no_space=True, mode="info")

    for parameter in interface_config_parameters:
        console("", parameter, ", ", end="", quiet=True, no_space=True, mode="info")
        if getattr(peer, parameter.lower()) != "":
            config_interface_str = config_interface_str + parameter + " = " + str(getattr(peer, parameter.lower())) + \
                                   "\n"
    console(quiet=True, mode="info")  # Zeilenumbruch für detaillierte Ausgaben zum Programmablauf

    return config_interface_str
