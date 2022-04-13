"""
Enthält alle Funktionen für das Verwalten und Anzeigen von importierten Konfigurationen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import re  # Für das Parsen von Konfigurationsdateien

# Imports von Drittanbietern
from colorama import Fore, Style

# Eigene Imports
from client_config import ClientConfig
from constants import CONFIG_PARAMETERS
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import INTERFACE_CONFIG_PARAMETERS
from constants import PEER_CONFIG_PARAMETERS
from constants import DEBUG
from server_config import ServerConfig
import keys


def print_configuration(server):
    """
    Zeigt eine tabellarische Übersicht der konfigurierten VPN-Konfigurationen an.
    """

    # Parameterprüfungen
    if not isinstance(server, ServerConfig):
        print(f"{Fore.RED}Fehler: Serverkonfiguration ist ungültig{Style.RESET_ALL}")
        return

    # Prüfung, ob erforderliche Parameter vorhanden sind. Alle fehlenden Parameter werden ausgegeben.
    minimal_parameters_are_valid = True
    for parameter in MINIMAL_CONFIG_PARAMETERS:
        if getattr(server, parameter) == "":
            print(f"{Fore.RED}Fehler: Serverkonfiguration ist nicht vollständig. Parameter {Style.RESET_ALL}{parameter}"
                  f"{Fore.RED} fehlt{Style.RESET_ALL}")
            minimal_parameters_are_valid = False
    if not minimal_parameters_are_valid:
        return

    # Prüfung, ob Clients hinterlegt sind
    if len(server.clients) < 1:
        print(f"{Fore.RED}Fehler: keine Clientkonfigurationen hinterlegt.{Style.RESET_ALL}")
        return

    # Anzeige der Details pro Client, fettgedruckt: Bezeichnung, IP-Adresse, Anfang öffentlicher Schlüssel
    print(f"{Style.BRIGHT}{'#':4}{'Name':12} | {'Privater Schlüssel':18}{Style.RESET_ALL}")
    pos = 1
    for client in server.clients:
        print(f"{Style.BRIGHT}{pos:<4}{Style.RESET_ALL}{client.name[:12]:12} | {client.privatekey[:15] + '...':18}")
        pos = pos + 1


def calculate_publickey(client):
    """
    Berechnet die öffentlichen Schlüssel der Clients anhand der privaten Schlüssel.
    """
    client.client_publickey = keys.pubkey(client.privatekey)
    if DEBUG:
        print(f"{Fore.GREEN}Erfolg: Öffentlicher Schlüssel {Style.RESET_ALL}{client.client_publickey[:5]}..."
              f"{Fore.GREEN} für privaten Schlüssel{Style.RESET_ALL} {client.privatekey[:5]}...{Fore.GREEN} "
              f"berechnet und hinterlegt.{Style.RESET_ALL}")


def insert_client(server):
    """
    Erstellt eine neue Clientkonfiguration. Werte für Parameter werden über die Kosole eingegeben.
    """
    # TODO Bug: keine Parameterprüfung von ServerKonfiguration. Falls server leer ist, muss dies erst konfiguriert
    #  werden.

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    # Ein neues ClientConfig Objekt wird erstellt, welches später zum ServerConfig Objekt hinzugefügt wird.
    client = ClientConfig()

    # Ein Schlüsselpaar wird generiert und hinterlegt.
    client.privatekey = keys.genkey()
    client.client_publickey = keys.pubkey(client.privatekey)

    # Der öffentliche Schlüssel des Servers wird hinterlegt
    client.publickey = keys.pubkey(server.privatekey)

    # Eingabe eines Namens
    name = input("Name? --> ")
    client.name = name

    # TODO Valide IP-Adresse muss ermittelt werden
    # Eingabe einer IP-Adresse
    address = input("IP-Adresse? --> ")
    client.address = address

    # Weitere Parameter abfragen, prüfen und einfügen
    print(f"{Fore.BLUE}Info: Bitte weitere Parameter eintragen. Zurück mit{Style.RESET_ALL} .")
    while True:
        try:
            input_line = input()
        except UnicodeDecodeError:
            print(f"{Fore.RED}Fehler: Ungültige Eingabe. Bitte keine Akzente eingeben.")

        # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
        match = re.search("^([^ ]*) *= *(.*)", input_line, re.IGNORECASE)

        # Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
        if match:
            # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
            key = re.split("^([^ ]*) *= *(.*)", input_line, re.IGNORECASE)[1].strip()
            value = re.split("^([^ ]*) *= *(.*)", input_line, re.IGNORECASE)[2].strip()
            if DEBUG:
                print(f"{Fore.GREEN}Erfolg: Parameter {Style.RESET_ALL}{key}{Fore.GREEN} mit Wert {Style.RESET_ALL}"
                      f"{value}{Fore.GREEN} erkannt{Style.RESET_ALL}")

            if DEBUG:
                print(f"{Fore.BLUE}Info: Prüfe, ob der Parameter in der Menge der unterstützten Parameter "
                      f"enthalten ist{Style.RESET_ALL}")

            # Prüfe, ob der Parameter grundsätzlich gültig ist
            if key.lower() in config_parameters:
                # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                setattr(client, key.lower(), value)
                if DEBUG:
                    print(f"{Fore.GREEN}Erfolg: Parameter hinterlegt{Style.RESET_ALL}")
        elif input_line == ".":
            break
        else:
            print(f"{Fore.RED}Fehler: Ungültige Eingabe.{Style.RESET_ALL}")
            # continue
    # Clientkonfiguration zur Serverkonfiguration hinzufügen
    server.clients.append(client)
    if DEBUG:
        print(f"{Fore.GREEN}Erfolg: Client zur Konfiguration hinzugefügt{Style.RESET_ALL}")


def delete_client(server, choice):
    """
    Entfernt eine bestehende Konfiguration der Parameter choice bestimmt, welche Konfiguration entfernt wird, 0
    entspricht der Serverkonfiguration. Clients haben aufsteigende Nummern ab 1.
    """

    try:
        client_id = int(choice)
    except ValueError:
        print(f"{Fore.RED}Fehler: Eingabe einer Zahl erwartet.{Style.RESET_ALL}")
        return
    try:
        del server.clients[client_id - 1]
    except IndexError:
        print(f"{Fore.RED}Fehler: Ungültige ID eingegeben.{Style.RESET_ALL}")
    except AttributeError:
        print(f"{Fore.RED}Fehler: Keine Konfiguration im Arbeitsspeicher.{Style.RESET_ALL}")


def change_client(server, choice):
    """
    Änderung einer bestehenden Konfiguration. Der Parameter choice bestimmt, welche Konfiguration angepasst wird.
    0 entspricht der Serverkonfiguration. Clients haben aufsteigende Nummern ab 1.
    """

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    print(f"Parameter {Fore.BLUE}ohne Wert eingeben für Ausgabe des derzeitigen Werts. {Style.RESET_ALL}Parameter = "
          f"Wert{Fore.BLUE} eingeben für Änderung des Werts. Zurück mit {Style.RESET_ALL}.")

    if choice == "0":
        # Serverkonfiguration soll geändert werden

        while True:
            try:
                input_line = input(f"{Style.BRIGHT}Konfiguration ändern (Server) > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe. Bitte keine Akzente eingeben.")

            # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
            match = re.search("^([^ ]*) *= *(.*)", input_line, re.IGNORECASE)

            if input_line == ".":
                break
            ### COPIED FROM create_client

            # Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
            elif match:
                # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
                key = re.split("^([^ ]*) *= *(.*)", input_line, re.IGNORECASE)[1].strip()
                value = re.split("^([^ ]*) *= *(.*)", input_line, re.IGNORECASE)[2].strip()
                if DEBUG:
                    print(
                        f"{Fore.GREEN}Erfolg: Parameter {Style.RESET_ALL}{key}{Fore.GREEN} mit Wert {Style.RESET_ALL}"
                        f"{value}{Fore.GREEN} erkannt{Style.RESET_ALL}")

                if DEBUG:
                    print(f"{Fore.BLUE}Info: Prüfe, ob der Parameter in der Menge der unterstützten Parameter "
                          f"enthalten ist{Style.RESET_ALL}")

                # Prüfe, ob der Parameter grundsätzlich gültig ist
                if key.lower() in config_parameters:
                    # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                    setattr(server, key.lower(), value)
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Parameter hinterlegt{Style.RESET_ALL}")
            ### END OF COPIED FROM create client
            else:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe{Style.RESET_ALL}")

    else:
        # Eine der Clientkonfigurationen soll geändert werden

        try:
            client_id = int(choice)
        except ValueError:
            print(f"{Fore.RED}Fehler: Eingabe einer Zahl erwartet.{Style.RESET_ALL}")
            return
        try:
            if len(server.clients) < client_id:
                print(f"{Fore.RED}Fehler: Konfiguration {Style.RESET_ALL}{client_id}{Fore.RED} existiert nicht"
                      f"{Style.RESET_ALL}")
                return
        # Wenn das Attribut clients nicht vorhanden ist, ist server nicht von der Klasse ServerConfig
        except AttributeError:
            print(f"{Fore.RED}Fehler: Keine Konfiguration im Arbeitsspeicher hinterlegt. Neue Konfiguration importieren"
                  f" oder erstellen.{Style.RESET_ALL}")
            return

        while True:
            input_line = input(f"{Style.BRIGHT}Konfiguration ändern (Client {client_id}) > {Style.RESET_ALL}")

            if input_line == ".":
                break
            else:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe{Style.RESET_ALL}")


def print_details(server, choice):
    """
    Gibt alle Parameter einer Konfiguration auf der Konsole aus.
    """

    # TODO Bug: Parameternamen werden nur kleingeschrieben ausgegeben

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    # Vorbereitung auf Prüfung auf Konfigurationsparameter der Peer-Sektion
    peer_config_parameters = [parameter.lower() for parameter in PEER_CONFIG_PARAMETERS]

    # Vorbereitung auf Generierung einer Liste mit allen Parameternamen der Interface-Sektion
    interface_config_parameters = [parameter.lower() for parameter in INTERFACE_CONFIG_PARAMETERS]

    if choice == "0":
        # Der Name ist nicht Bestandteil der Konfigurationsparameter und wird daher gesondert ausgegeben
        print(f"{Style.BRIGHT}Name{Style.RESET_ALL} = {getattr(server, 'name')}")
        # Ausgabe der Konfiguration des Servers
        for parameter in interface_config_parameters:
            print(f"{Style.BRIGHT}{parameter}{Style.RESET_ALL} = {getattr(server, parameter)}")
        # Ausgabe der Peer-Sektionen
        for client in server.clients:
            print("[Peer]")
            print(f"# Name = {client.name}")
            for parameter in peer_config_parameters:
                print(f"{Style.BRIGHT}{parameter}{Style.RESET_ALL} = {getattr(client, f'client_{parameter}')}")

    else:
        # Ausgabe der Konfiguration von server.clients[choice-1]
        try:
            client_id = int(choice)
        except ValueError:
            print(f"{Fore.RED}Fehler: Eingabe einer Zahl erwartet.{Style.RESET_ALL}")
            return
        try:
            if len(server.clients) < client_id:
                print(f"{Fore.RED}Fehler: Konfiguration {Style.RESET_ALL}{client_id}{Fore.RED} existiert nicht"
                      f"{Style.RESET_ALL}")
                return
        # Wenn das Attribut clients nicht vorhanden ist, ist server nicht von der Klasse ServerConfig
        except AttributeError:
            print(f"{Fore.RED}Fehler: Keine Konfiguration im Arbeitsspeicher hinterlegt.{Style.RESET_ALL}")
            return

        # Der Name ist nicht Bestandteil der Konfigurationsparameter und wird daher gesondert ausgegeben
        print(f"{Style.BRIGHT}Name{Style.RESET_ALL} = {getattr(server.clients[client_id-1], 'name')}")

        for parameter in config_parameters:
            print(f"{Style.BRIGHT}{parameter}{Style.RESET_ALL} = {getattr(server.clients[client_id-1], parameter)}")

    # def change_client_keypair(server, choice):
    """
    Generiert ein neues Schlüsselpaar. Hinterlegt den privaten Schlüssel in der Serverkonfiguration und den öffentlichen
    Schlüssel in alle Peer-Sektionen der Clientkonfigurationen.
    """