"""
Enthält alle Funktionen für das Verwalten und Anzeigen von importierten Konfigurationen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import re  # Für das Parsen von Konfigurationsdateien

# Imports von Drittanbietern
from ipaddress import ip_network
from colorama import Fore, Style

# Eigene Imports
from client_config import ClientConfig
from constants import CONFIG_PARAMETERS
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import INTERFACE_CONFIG_PARAMETERS
from constants import DEBUG
from constants import RE_MATCH_KEY
from constants import RE_MATCH_KEY_VALUE
from networking import get_cidr_mask_from_hosts
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
    name = input("Client anlegen (Name?) > ")
    client.name = name

    # TODO Valide IP-Adresse muss ermittelt werden
    # Eingabe einer IP-Adresse
    address = input("Client anlegen (IP-Adresse?) > ")
    client.address = address

    # Weitere Parameter abfragen, prüfen und einfügen
    print(f"{Fore.BLUE}Info: Bitte weitere Parameter eintragen. Zurück mit{Style.RESET_ALL} .")
    # TODO BUG: Falsche Parameter werden nicht bemängelt
    while True:
        try:
            input_line = input("Client anlegen (zusätzliche Parameter?) > ")
        except UnicodeDecodeError:
            print(f"{Fore.RED}Fehler: Ungültige Eingabe. Bitte keine Akzente eingeben.")

        # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
        match = re.search(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)

        # Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
        if match:
            # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
            key = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[1].strip()
            value = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[2].strip()
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
            else:
                print(f"{Fore.YELLOW}Warnung: Unbekannter Parameter {Style.RESET_ALL}{key}")
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

    # TODO BUG MINIMAL_CONFIG_PARAMETERS dürfen nicht "" lauten. Prüfung notwendig.

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen der Interface-Sektion in
    # Kleinbuchstaben
    interface_config_parameters = [parameter.lower() for parameter in INTERFACE_CONFIG_PARAMETERS]

    print(f"Parameter {Fore.BLUE}ohne Wert eingeben für Ausgabe des derzeitigen Werts. {Style.RESET_ALL}Parameter = "
          f"Wert{Fore.BLUE} eingeben für Änderung des Werts. Zurück mit {Style.RESET_ALL}.")

    if choice == "0":
        # Serverkonfiguration soll geändert werden. Es ist nur möglich, die Interface-Sektion zu bearbeiten. Peer-
        # Sektionen werden mit der Clientkonfiguration angepasst

        while True:
            try:
                input_line = input(f"{Style.BRIGHT}Konfiguration ändern (Server) > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe. Bitte keine Akzente eingeben.")

            # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
            match_key_value = re.search(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)

            match_key = re.search(RE_MATCH_KEY, input_line, re.IGNORECASE)

            if input_line == ".":
                break

            # Prüfe, ob der Parameter ein unterstützter offizieller Parameter der Interface-Sektion ist
            elif match_key_value:
                # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
                key = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[1].strip()
                value = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[2].strip()
                if DEBUG:
                    print(
                        f"{Fore.GREEN}Erfolg: Parameter {Style.RESET_ALL}{key}{Fore.GREEN} mit Wert {Style.RESET_ALL}"
                        f"{value}{Fore.GREEN} erkannt{Style.RESET_ALL}")

                if DEBUG:
                    print(f"{Fore.BLUE}Info: Prüfe, ob der Parameter in der Menge der unterstützten Parameter "
                          f"enthalten ist{Style.RESET_ALL}")

                # Prüfe, ob der Parameter grundsätzlich gültig ist
                if key.lower() in interface_config_parameters:
                    # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                    setattr(server, key.lower(), value)
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Parameter hinterlegt{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Warnung: Unbekannter Parameter {Style.RESET_ALL}{input_line}")

            elif match_key:
                # Der Parametername wird ohne Leerzeichen am Anfang und Ende hinterlegt
                key = re.split(RE_MATCH_KEY, input_line, re.IGNORECASE)[1].strip()
                # Prüfe, ob der Parameter grundsätzlich gültig ist. Da es sich hierbei um eine ServerConfig handelt,
                # in welcher mehrere Peer-Sektionen vorkommen, können nur Parameter der Interface-Sektion ausgegeben
                # werden
                if key.lower() in interface_config_parameters:
                    # Falls ja, gebe den Wert aus
                    print(getattr(server, key.lower()))
                else:
                    # Es handelt sich nicht um einen unbekannten Parameter. Der Benutzer muss informiert werden.
                    print(f"{Fore.YELLOW}Warnung: Unbekannter Parameter {Style.RESET_ALL}{key}")
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
            try:
                input_line = input(f"{Style.BRIGHT}Konfiguration ändern (Client {client_id}) > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe. Bitte keine Akzente eingeben.")

            # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
            match_key_value = re.search(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)

            match_key = re.search(RE_MATCH_KEY, input_line, re.IGNORECASE)
            
            if input_line == ".":
                # Bei Eingabe von . zurück
                break

            # Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
            if match_key_value:
                # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
                key = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[1].strip()
                value = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[2].strip()
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
                    setattr(server.clients[client_id-1], key.lower(), value)
                    if DEBUG:
                        print(f"{Fore.GREEN}Erfolg: Parameter hinterlegt{Style.RESET_ALL}")

                else:
                    print(f"{Fore.YELLOW}Warnung: Unbekannter Parameter {Style.RESET_ALL}{input_line}")

            elif match_key:
                # Der Parametername wird ohne Leerzeichen am Anfang und Ende hinterlegt
                key = re.split(RE_MATCH_KEY, input_line, re.IGNORECASE)[1].strip()

                # Prüfe, ob der Parameter grundsätzlich gültig ist. Da es sich hierbei um einen Client handelt, können
                # alle Parameter in CONFIG_PARAMETERS ausgegeben werden.
                # TODO BUG: Leerzeichen am Ende führen zu einer Nichterkennung des Parameters
                if key.lower() in config_parameters:
                    # Falls ja, gebe den Wert aus
                    print(getattr(server.clients[client_id-1], key.lower()))
                else:
                    # Es handelt sich nicht um einen unbekannten Parameter. Der Benutzer muss informiert werden.
                    print(f"{Fore.YELLOW}Warnung: Unbekannter Parameter {Style.RESET_ALL}{key}")

            else:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe{Style.RESET_ALL}")



def create_server_config():
    """
    Erstelle eine neue Konfiguration.
    """

    # TODO Feature: weitere Parameter direkt bei der Erstellung eingeben

    server = ServerConfig()

    # Ein privater Schlüssel wird generiert und hinterlegt. Der öffentliche Schlüssel kann jederzeit anhand des
    # privaten Schlüssels berechnet werden.
    server.privatekey = keys.genkey()

    # Eingabe eines Namens
    name = input("Server anlegen (Name?) > ")
    server.name = name

    # Eingabe einer IP-Adresse
    address = input("Server anlegen (IP-Adresse?) > ")
    server.address = address

    return server


def change_client_keypair(server, choice):
    """
    Generiert ein neues Schlüsselpaar für einen beliebigen Client. Hinterlegt den privaten Schlüssel eines Clients in
    der Clientkonfiguration und den öffentlichen Schlüssel in der Serverkonfiguration. Hinterlegt den privaten Schlüssel
    eines Servers in der Serverkonfiguration und den öffentlichen Schlüssel in allen Clientkonfigurationen.
    """

    if choice == "0":
        if DEBUG:
            print(f"{Fore.BLUE}Info: Ändere das Schlüsselpaar des Servers.")

        server.privatekey = keys.genkey()
        publickey = keys.pubkey(server.privatekey)

        for client in server.clients:
            client.publickey = publickey

    else:
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

        if DEBUG:
            print(f"{Fore.BLUE}Info: Ändere das Schlüsselpaar des Clients {client_id}.")

        server.clients[client_id-1].privatekey = keys.genkey()
        server.clients[client_id-1].client_publickey = keys.pubkey(server.clients[client_id-1].privatekey)


def change_network_size(server, choice):
    """
    Diese Funktion ändert die Netzwerkgröße des VPN-Netzwerks. Der Parameter server übergibt der Funktion ein Objekt vom
    Typ ServerConfig. Der Parameter number_of_hosts gibt an, wie viele Hosts (Clients + Server) das Netzwerk ausgelegt
    werden soll. Anhand dieser Angabe wird die notwendige Netzwerkmaske berechnet und eine geeignete Netzwerkklasse
    festgelegt.
    """

    # Parameterprüfungen
    try:
        number_of_hosts = int(choice)
    except ValueError:
        print(f"{Fore.RED}Fehler: Eingabe einer Zahl erwartet.{Style.RESET_ALL}")
        return

    if number_of_hosts < len(server.clients):
        print(f"{Fore.RED}Fehler: Die Konfiguration im Arbeitsspeicher umfasst {Style.RESET_ALL}{len(server.clients)}"
              f"{Fore.RED} Clients. Es kann keine Netzwerkgröße für eine geringere Anzahl eingestellt werden. Breche ab"
              f"{Style.RESET_ALL}")
        return

    # CIDR-Maske berechnen
    cidr_mask = get_cidr_mask_from_hosts(number_of_hosts)
    if cidr_mask is None:  # Bei einem Fehler wird None zurückgegeben
        print(f"{Fore.RED}Fehler: Breche ab.{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}Erfolg: CIDR-Maske {cidr_mask} berechnet{Style.RESET_ALL}")

    ip4_network_class = ""
    # Netzklasse A, B oder C festlegen
    if cidr_mask >= 24:
        ip4_network_class = "c"
    elif cidr_mask >= 16:
        ip4_network_class = "b"
    elif cidr_mask >= 8:
        ip4_network_class = "a"
    else:
        print(f"Fehler: Ungültige CIDR-Maske für ein privates Netzwerk berechnet. Breche ab.")
        return

    print(f"{Fore.GREEN}Erfolg: Netzklasse {ip4_network_class.upper()} festgelegt{Style.RESET_ALL}")

    ip4_network = ""
    # Geeignetes IPv4-Netzwerk festlegen
    if ip4_network_class == "a":
        ip4_network = ip_network(f'10.0.0.0/{cidr_mask}')
    elif ip4_network_class == "b":
        ip4_network = ip_network(f'172.16.0.0/{cidr_mask}')
    elif ip4_network_class == "c":
        ip4_network = ip_network(f'192.168.0.0/{cidr_mask}')
    else:
        print(f"{Fore.RED}Fehler: Berechnung des Subnets ungültig. Breche ab.")
        return

    if DEBUG:
        print(f"{Fore.GREEN}Erfolg: Neues Subnetz {Style.RESET_ALL}{ip4_network}{Fore.GREEN} wird verwendet"
              f"{Style.RESET_ALL}")

    list_of_host_addr = list(ip4_network.hosts())

    # Dem Server die letzte IP-Adresse im Subnetz zuweisen
    try:
        print(f"{Fore.BLUE}Info: Weise Server die IP-Adresse {Style.RESET_ALL}{list_of_host_addr[-1]}{Fore.BLUE} zu.")
        server.address = list_of_host_addr[-1]
    except AttributeError:
        print(f"{Fore.RED}Fehler: Es ist keine Serverkonfiguration vorhanden. Neue erstellen oder importieren. Breche "
              f"ab.{Style.RESET_ALL}")

    # Den Clients vom Anfang aufsteigende Adressen zuweisen
    for i in range(len(server.clients)):
        server.clients[i].address = list_of_host_addr[i]
        if DEBUG:
            print(f"{Fore.BLUE}Info: Weise Client mit privatem Schlüssel {Style.RESET_ALL}"
                  f"{server.clients[i].privatekey:5}...{Fore.BLUE} die "
                  f"IP-Adresse {Style.RESET_ALL}{list_of_host_addr[i]}{Fore.BLUE} zu.{Style.RESET_ALL}")
