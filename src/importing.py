"""
Enthält alle Funktionen für das Importieren von Konfigurationen auf dem Dateisystem in interne Datenstrukturen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import glob  # Für das Auffinden von Konfigurationsdateien mittels Wildcard
import re  # Für das Parsen von Konfigurationsdateien

# Imports von Drittanbietern
from colorama import Fore, Style  # Für vom Betriebssystem unabhängige farbige Ausgaben

# Eigene Imports
from config_management import calculate_publickey
from constants import CONFIG_PARAMETERS
from constants import WG_DIR
from constants import DEBUG
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import SERVER_CONFIG_FILENAME
from constants import PEER_CONFIG_PARAMETERS
from client_config import ClientConfig
from file_management import check_file
from file_management import check_dir
from server_config import ServerConfig
from peer import Peer


def parse_and_import(peer):
    """
    Schreibt die Werte der Parameter einer Datei in die Datenstruktur. peer kann ein Client oder Server sein.
    Der Parameter peer.filename von peer muss einen validen Pfad zu einer Konfigurationsdatei enthalten.
    """

    # Parameterprüfungen
    check_file(peer.filename)

    # Vorbereitung, "deklarieren" der peer_config Variable für das Sammeln und Übertragen von Parametern einer
    # Peer-Sektion
    client_data = ""

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    # Vorbereitung auf Prüfung auf Konfigurationsparameter der Peer-Sektion
    peer_config_parameters = [parameter.lower() for parameter in PEER_CONFIG_PARAMETERS]

    # Vorbereitung auf die Prüfung auf Vollständigkeit der notwendigen Parameter
    minimal_parameters = [parameter.lower() for parameter in MINIMAL_CONFIG_PARAMETERS]

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
    with open(peer.filename, encoding='utf-8') as config:
        # Datei Zeile für Zeile einlesen
        if DEBUG:
            print(f"{Fore.BLUE}Info: Lese Datei {Style.RESET_ALL}{peer.filename}")
        for line in config:
            if DEBUG:
                # Zeile ohne \n ausgeben
                print(f"{Fore.BLUE}Info: Lese Zeile{Style.RESET_ALL}", line.replace('\n', ''))
            # Die Zeile wird auf Bestandteile der Syntax untersucht: leer, Kommentar, Sektion oder Name-Wert Paar
            match = re.search(r'^ *$', line)  # Leere Zeile darf keine oder nur Leerzeichen enthalten
            # Bei leerer Zeile: fahre fort
            if match:
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Zeile enthält keine Konfiguration.{Style.RESET_ALL}")
                continue

            match = re.search(r'^\[.*]$', line)
            # Bei Sektion: Unterscheide zwischen Server und Client. Client: fahre fort. Server: Importiere Daten in die
            # Datenstruktur des Clients.
            if match:
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Zeile leitet eine INI-Sektion ein{Style.RESET_ALL}")

                match = re.search(r'^ *\[Peer] *$', line, re.IGNORECASE)
                if match and is_server:
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Zeile leitet eine Peer-Sektion ein{Style.RESET_ALL}")

                    # Die Daten werden zeilenweise eingelesen. Eine Peer-Sektion besteht aus unbekannt vielen Zeilen.
                    # Um die Daten zu einem peer zu sammeln, muss also zeilenübergreifend gearbeitet werden. Die Daten
                    # des Peers werden in die Variable peer geschrieben. Zu Beginn der nächsten Peer-Sektion oder nach
                    # Ende der Datei werden die gespeicherten Konfigurationsparameter in das server Objekt übernommen.
                    # Die Zuordnung erfolgt dabei über das Schlüsselpaar. Mit dem bereits bekannten privaten Schlüssel
                    # kann der öffentliche Schlüssel berechnet werden. Die Daten werden für den Client hinterlegt,
                    # dessen errechneter öffentlicher Schlüssel mit dem des hinterlegten übereinstimmt.

                    # Zuerst werden Daten aus dem Objekt client_data gesichert, falls notwendig
                    if isinstance(client_data, Peer):
                        # peer ist hier immer ein Objekt der Klasse ServerConfig
                        assign_peer_to_client(client_data, peer)

                    # Danach wird ein neues Objekt angelegt
                    client_data = Peer()

                    # In den folgenden Durchläufen werden clientspezifische Daten in dem Objekt gesammelt, bis diese
                    # mit der oben aufgerufenen Funktion assign_peer_to_client in die Datenstruktur übernommen werden.

                continue

            match = re.search(r'^#', line)
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
                    if DEBUG:
                        print(f"{Fore.BLUE}Info: Es sind mehrere kommentierte Zeilen in der Datei vorhanden. "
                              f"Der erste Kommentar wurde als Bezeichnung interpretiert, dieser und folgende Kommentare"
                              f" werden ignoriert.{Style.RESET_ALL}")
                continue

            # TODO Refactoring: nach Erkennung des regex weiteren Prozess in Funktion auslagern und in insert_client()
            #  wiederverwenden
            match = re.search("^([^ ]*) *= *(.*)", line, re.IGNORECASE)
            # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
            key = re.split("^([^ ]*) *= *(.*)", line, re.IGNORECASE)[1].strip()
            value = re.split("^([^ ]*) *= *(.*)", line, re.IGNORECASE)[2].strip()
            if DEBUG:
                print(f"{Fore.GREEN}Erfolg: Parameter {Style.RESET_ALL}{key}{Fore.GREEN} mit Wert {Style.RESET_ALL}"
                      f"{value}{Fore.GREEN} erkannt{Style.RESET_ALL}")
            # Bei Name-Wert Paar: Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
            if match:
                if DEBUG:
                    print(f"{Fore.BLUE}Info: Prüfe, ob der Parameter in der Menge der unterstützten Parameter "
                          f"enthalten ist")
                # Prüfe, ob der Parameter Teil einer Peer-Sektion einer Serverkonfiguration ist
                if key.lower() in peer_config_parameters and is_server:
                    # Falls ja, Parameter nicht im peer-Objekt hinterlegen, sondern im client_data Objekt vorhalten
                    setattr(client_data, key.lower(), value)
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Ein Parameter aus einer Server-Peer Sektion wurde für die spätere "
                              f"Verarbeitung zurückgestellt.")

                # Sonst: prüfe, ob der Parameter grundsätzlich gültig ist
                elif key.lower() in config_parameters:
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

        # und für den Fall, dass eine Peer-Sektion endet: übertrage Daten von client_data in das server Objekt.
        if isinstance(client_data, Peer):  # Falls eine Peer-Sektion verarbeitet wurde
            assign_peer_to_client(client_data, peer)  # peer ist in diesem Fall immer ein Objekt der Klasse ServerConfig


def assign_peer_to_client(client_data, server):
    """
    client_data enthält Konfigurationsparameter aus der Peer-Sektion einer Serverkonfiguration. Die Daten müssen einem
    bereits importierten Client anhand des öffentlichen Schlüssels zugeordnet werden. Dazu wird das Attribut publickey
    der Objekte in server.clients[] mit dem Attribut client_data.publickey verglichen.
    """

    # Prüfung, ob client_data einen öffentlichen Schlüssel enthält
    # Falls nicht, ist eine Zuordnung unmöglich
    if client_data.publickey == "":
        print(f"{Fore.YELLOW}Warnung: eine Peer-Sektion aus der Serverkonfiguration kann keinem Client zugeordnet "
              f"werden. Die Peer-Sektionen müssen einen Wert für PublicKey enthalten. Bitte die Sektion mit folgenden "
              f"Werten prüfen: ", end="")

        additional_values = False
        for parameter in PEER_CONFIG_PARAMETERS:
            if getattr(client_data, parameter.lower()) != "":
                print(f"{parameter} = {getattr(client_data, parameter.lower())}", end="")
                additional_values = True

        if not additional_values:
            print(f"es handelt sich um eine leere Peer-Sektion.{Style.RESET_ALL}")
        else:
            print(f"{Style.RESET_ALL}")  # Zeilenumbruch

    # Falls ein öffentlicher Schlüssel hinterlegt wurde, diesen mit den vorhandenen Schlüsseln abgleichen
    else:
        # Vorbereitung für den Programmablauf nach erfolgreicher Übertragung der Parameter in das server-Objekt
        success = False

        if DEBUG:
            print(f"{Fore.BLUE}Info: Zuordnung der Client-Sektion zu vorhandenen Clients{Style.RESET_ALL}")
        for client in server.clients:
            if DEBUG:
                print(f"{Fore.BLUE}Info: Vergleiche Schlüssel aus der Peer-Sektion{Style.RESET_ALL} "
                      f"{client_data.publickey} {Fore.BLUE} mit hinterlegtem Schlüssel{Style.RESET_ALL} "
                      f"{client.client_publickey} {Fore.BLUE}...")
            if client.client_publickey == client_data.publickey:
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Übereinstimmung gefunden{Style.RESET_ALL}")
                # Daten übertragen
                if DEBUG:
                    print(f"{Fore.BLUE}Info: Beginne mit der Übertragung der Parameter{Style.RESET_ALL}")
                for parameter in PEER_CONFIG_PARAMETERS:
                    # Die Parameter aus den Peer-Sektionen der Serverkonfiguration werden clientspezifisch gespeichert.
                    # Da in den Konfigurationen der Clients auch eine Peer-Sektion vorkommt, wird den Parametern aus
                    # der Serverkonfiguration ein 'client_' vorangestellt.
                    setattr(client, "client_" + parameter.lower(), getattr(client_data, parameter.lower()))
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Parameter erfolgreich übernommen")
                success = True

        if not success:
            print(f"{Fore.YELLOW}Warnung: eine Peer-Sektion konnte keinem Client zugeordnet werden, da kein "
                  f"übereinstimmender öffentlicher Schlüssel in der Konfiguration enthalten ist. Das Schlüsselpaar "
                  f"ist ungültig. Bitte in der Serverkonfiguration {Style.RESET_ALL}{WG_DIR}{SERVER_CONFIG_FILENAME}"
                  f"{Fore.YELLOW} die Sektion mit dem öffentlichen Schlüssel {Style.RESET_ALL}{client_data.publickey}"
                  f"{Fore.YELLOW} prüfen.{Style.RESET_ALL}")


def import_configurations():
    """
    Importiert alle VPN-Konfigurationen im Wireguard-Verzeichnis.
    """

    server = ServerConfig()

    check_dir(WG_DIR)

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
        print(f"{Fore.BLUE}Info: Neben der Serverkonfiguration wurden folgende Clientkonfigurationen gefunden: "
              f"{list_client_configuration_filenames}{Style.RESET_ALL}")

    # Konfigurationen importieren

    # ..der Clients
    for file in list_client_configuration_filenames:

        # Für jede gefundene Clientkonfiguration wird dem Server-Objekt ein ClientConfig-Objekt hinzugefügt.
        server.clients.append(ClientConfig())

        # Der Dateipfad wird in der Datenstruktur hinterlegt
        server.clients[-1].filename = file

        # Import der Parameter
        parse_and_import(server.clients[-1])

        # Berechnung und Ergänzung des öffentlichen Schlüssels in der Konfiguration im Arbeitsspeicher. Notwendig für
        # die spätere Zuordnung der Peer-Sektionen aus der Serverkonfiguration.
        calculate_publickey(server.clients[-1])

        if DEBUG:
            print(f"{Fore.GREEN}Erfolg: Folgende Clients wurden importiert:{Style.RESET_ALL}")
        for client in server.clients:
            if DEBUG:
                print(f"{Fore.GREEN}Client {Style.RESET_ALL}{str(client.name)}{Fore.GREEN} mit privatem Schlüssel "
                      f"{Style.RESET_ALL}{str(client.privatekey)}")

    # ..des Servers
    parse_and_import(server)

    return server
