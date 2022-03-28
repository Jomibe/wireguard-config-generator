"""
Enthält alle Funktionen für das Importieren von Konfigurationen auf dem Dateisystem in interne Datenstrukturen.
"""

# Öffentliche Imports
from colorama import Fore, Style  # Für vom Betriebssystem unabhängige farbige Ausgaben
import glob  # Für das Auffinden von Konfigurationsdateien mittels Wildcard
import os  # Für Dateisystemzugriffe
from pathlib import Path  # Für Dateipfadangaben
import re  # Für das Parsen von Konfigurationsdateien

# Interne Imports
from constants import CONFIG_PARAMETERS
from constants import WG_DIR
from constants import DEBUG
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import SERVER_CONFIG_FILENAME
from ClientConfig import ClientConfig
from ServerConfig import ServerConfig


def parse_and_import(peer):
    """
    Schreibt die Werte der Parameter einer Datei in die Datenstruktur. peer kann ein Client oder Server sein.
    Der Parameter filename von peer muss einen validen Pfad zu einer Konfigurationsdatei enthalten.
    """

    # Parameterprüfungen
    # TODO Prüfung des Pfades auslagern?
    # Prüfung, ob der Pfad existiert.
    if not Path(peer.filename).exists():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {peer.filename} existiert nicht.{Style.RESET_ALL}")

    # Prüfung, ob der Pfad auf eine Datei zeigt.
    if not Path(peer.filename).is_file():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {peer.filename} ist keine Datei.{Style.RESET_ALL}")

    # Prüfung, ob die Datei gelesen werden kann.
    if os.access(Path(peer.filename), os.R_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Die Datei {peer.filename} ist nicht lesbar.{Style.RESET_ALL}")

    # Prüfung, ob in die Datei geschrieben werden kann.
    if os.access(Path(peer.filename), os.W_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Die Datei {peer.filename} ist nicht beschreibbar.{Style.RESET_ALL}")

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = []
    for parameter in CONFIG_PARAMETERS:
        config_parameters.append(parameter.lower())

    # Vorbereitung auf die Prüfung auf Vollständigkeit der notwendigen Parameter
    minimal_parameters = list(MINIMAL_CONFIG_PARAMETERS)

    # Fallunterscheidung: soll eine Server- oder Clientkonfiguration importiert werden?
    is_server = False
    if isinstance(peer, ServerConfig):
        is_server = True
        if DEBUG:
            print(f"{Fore.GREEN}Erfolg: Serverkonfiguration erkannt{Style.RESET_ALL}")
            if peer.filename != WG_DIR + SERVER_CONFIG_FILENAME:
                print(f"{Fore.BLUE}Hinweis: Serverkonfiguration {Style.RESET_ALL}{peer.filename}{Fore.BLUE} entspricht "
                      f"nicht dem Standard {Style.RESET_ALL}{WG_DIR + SERVER_CONFIG_FILENAME}")
    elif isinstance(peer, ClientConfig):
        if DEBUG:
            print(f"{Fore.GREEN}Erfolg: Clientkonfiguration erkannt{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Fehler: Ungültige Datenstruktur vom Typ {Style.RESET_ALL}{type(peer)}{Fore.RED} übergeben"
              f"{Style.RESET_ALL}")

    # Öffnen der Datei
    with open(peer.filename) as config:
        # Datei Zeile für Zeile einlesen
        if DEBUG:
            print(f"{Fore.BLUE}Info: Lese Datei {Style.RESET_ALL}{peer.filename}")
        for line in config:
            if DEBUG:
                # Zeile ohne \n ausgeben
                print(f"{Fore.BLUE}Info: Lese Zeile{Style.RESET_ALL}", line.replace('\n', ''))
            # Die Zeile wird auf Bestandteile der Syntax untersucht: leer, Kommentar, Sektion oder Name-Wert Paar
            match = re.search('^ *$', line)  # Leere Zeile darf keine oder nur Leerzeichen enthalten
            # Bei leerer Zeile: fahre fort
            if match:
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Zeile enthält keine Konfiguration.{Style.RESET_ALL}")
                continue

            match = re.search('^\[.*]$', line)
            # Bei Sektion: fahre fort
            if match:
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Zeile enthält eine INI-Sektion{Style.RESET_ALL}")
                continue

            match = re.search('^#', line)
            # Bei Kommentar: der erste Kommentar gibt die Bezeichnung des Clients an
            # Die Bezeichnung ist kein offizieller Parameter (aber ein INI-Standard) und wird daher gesondert
            # behandelt.
            if match:
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Kommentar erkannt{Style.RESET_ALL}")
                if peer.name == "":
                    # Rauten (#), Leerzeichen sowie ein ggf. voranstehendes 'Name =' werden entfernt
                    peer.name = line.replace('\n', '').replace("Name", "").replace("=", "").replace(
                        "#", "").strip()
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Bezeichnung {Style.RESET_ALL}{peer.name}"
                              f"{Fore.GREEN} hinterlegt{Style.RESET_ALL}")
                else:
                    print(f"{Fore.BLUE}Info: Es sind mehrere kommentierte Zeilen in der Datei vorhanden."
                          f"Der erste Kommentar wurde als Bezeichnung interpretiert, dieser und folgende Kommentare"
                          f" werden ignoriert.{Style.RESET_ALL}")
                continue

            match = re.search("^(.*) *= *(.*)", line, re.IGNORECASE)
            # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
            key = re.split("^(.*) *= *(.*)", line, re.IGNORECASE)[1].strip()
            value = re.split("^(.*) *= *(.*)", line, re.IGNORECASE)[2].strip()
            if DEBUG:
                print(f"{Fore.GREEN}Erfolg: Parameter {Style.RESET_ALL}{key}{Fore.GREEN} mit Wert {Style.RESET_ALL}"
                      f"{value}{Fore.GREEN} erkannt{Style.RESET_ALL}")
            # Bei Name-Wert Paar: Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
            if match:
                if DEBUG:
                    print(f"{Fore.BLUE}Info: Prüfe, ob der Parameter in der Menge der unterstützten Parameter "
                          f"enthalten ist")
                if key.lower() in config_parameters:
                    # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                    setattr(peer, key.lower(), value)
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Parameter hinterlegt{Style.RESET_ALL}")
                    # "Streiche" den Parameter von der Liste der notwendigen Parameter, falls vorhanden
                    if key.lower() in minimal_parameters:
                        if DEBUG:
                            print(f"{Fore.GREEN}Erfolg: Parameter war in der Liste der notwendigen Parameter "
                                  f"enthalten {Style.RESET_ALL}")
                        minimal_parameters.remove(key.lower())

                # Falls nein: gebe eine entsprechende Warnung aus
                else:
                    print(f"{Fore.RED}Fehler: Kein gültiger Parameter in Zeile {Style.RESET_ALL}" + line.replace(
                        '\n', '') + f"{Fore.RED} erkannt{Style.RESET_ALL}")

                continue

            # Ist keine Übereinstimmung zu finden, ist die Zeile ungültig
            print(f"{Fore.RED}Fehler: Die Zeile ist ungültig:{Style.RESET_ALL}", line.replace('\n', ''))

        # Sobald das Ende der Datei erreicht ist, prüfe ob notwendige Konfigurationsparameter importiert wurden
        if len(minimal_parameters) > 0:
            print(f"{Fore.RED}Fehler: Datei {re.split(WG_DIR, peer.filename)[1]} enthält nicht die erforderlichen "
                  f"Parameter {MINIMAL_CONFIG_PARAMETERS}{Style.RESET_ALL}")


def import_configurations(server):
    """
    Importiert alle VPN-Konfigurationen im Wireguard-Verzeichnis.
    """

    # Prüfung, ob der Pfad existiert.
    if not Path(WG_DIR).exists():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {WG_DIR} existiert nicht.{Style.RESET_ALL}")

    # Prüfung, ob der Pfad auf ein Verzeichnis zeigt.
    if not Path(WG_DIR).is_dir():
        raise SystemExit(f"{Fore.RED}Fehler: Der Pfad {WG_DIR} ist kein Ordner.{Style.RESET_ALL}")

    # Prüfung, ob das Verzeichnis gelesen werden kann.
    if os.access(Path(WG_DIR), os.R_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Das Verzeichnis {WG_DIR} ist nicht lesbar.{Style.RESET_ALL}")

    # Prüfung, ob in das Verzeichnis geschrieben werden kann.
    if os.access(Path(WG_DIR), os.W_OK) is not True:
        SystemExit(f"{Fore.RED}Fehler: Das Verzeichnis {WG_DIR} ist nicht beschreibbar.{Style.RESET_ALL}")

    # TODO Falls nicht: alle Dateien im Verzeichnis sollen entfernt werden, es wird eine neue Konfiguration angelegt.

    # Einlesen der Konfigurationsdateien *.conf

    # Liste mit Dateinamen erstellen
    list_client_configuration_filenames = glob.glob(f"{WG_DIR}*.conf")

    # Dateiname der Serverkonfiguration ausschließen und damit prüfen, ob diese existiert
    try:
        list_client_configuration_filenames.remove(server.filename)
    except ValueError:
        print(f"{Fore.YELLOW}Warnung: Keine Serverkonfiguration wg0.conf gefunden.{Style.RESET_ALL}")

    # Zu importierende Clientkonfigurationen anzeigen
    if DEBUG:
        # TODO nur Dateinamen ausgeben
        print(f"{Fore.BLUE}Info: Neben der Serverkonfiguration wurden folgende Clientkonfigurationen gefunden: "
              f"{list_client_configuration_filenames}{Style.RESET_ALL}")

    # Konfigurationen importieren

    # ..des Servers
    parse_and_import(server)

    # ..der Clients
    for file in list_client_configuration_filenames:

        # Für jede gefundene Clientkonfiguration wird dem Server-Objekt ein ClientConfig-Objekt hinzugefügt.
        server.clients.append(ClientConfig())

        # Der Dateipfad wird in der Datenstruktur hinterlegt
        server.clients[-1].filename = file

        # Import der Parameter
        parse_and_import(server.clients[-1])

        if DEBUG:
            print(f"{Fore.GREEN}Erfolg: Folgende Clients wurden importiert:{Style.RESET_ALL}")
        for client in server.clients:
            if DEBUG:
                print(f"{Fore.GREEN}Client {Style.RESET_ALL}{str(client.name)}{Fore.GREEN} mit privatem Schlüssel "
                      f"{Style.RESET_ALL}{str(client.privatekey)}")
