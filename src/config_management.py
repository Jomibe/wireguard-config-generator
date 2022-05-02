"""
Enthält alle Funktionen für das Verwalten und Anzeigen von importierten Konfigurationen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import io
import re  # Für das Parsen von Konfigurationsdateien

# Imports von Drittanbietern
from ipaddress import ip_address
from colorama import Style
import qrcode

# Eigene Imports
from client_config import ClientConfig
from constants import CONFIG_PARAMETERS
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import INTERFACE_CONFIG_PARAMETERS
from constants import RE_MATCH_KEY
from constants import RE_MATCH_KEY_VALUE
from debugging import console
from exporting import config_to_str
from networking import get_cidr_mask_from_hosts
from server_config import ServerConfig
import keys


def print_configuration(server):
    """
    Zeigt eine tabellarische Übersicht der konfigurierten VPN-Konfigurationen an.
    """

    # Parameterprüfungen
    if not isinstance(server, ServerConfig):
        console("Serverkonfiguration ist ungültig", mode="err", perm=True)
        return

    # Prüfung, ob erforderliche Parameter vorhanden sind. Alle fehlenden Parameter werden ausgegeben.
    minimal_parameters_are_valid = True
    for parameter in MINIMAL_CONFIG_PARAMETERS:
        if getattr(server, parameter) == "":
            console("Serverkonfiguration ist nicht vollständig. Parameter", parameter, "fehlt", mode="err", perm=True)
            minimal_parameters_are_valid = False
    if not minimal_parameters_are_valid:
        return

    # Prüfung, ob Clients hinterlegt sind
    if len(server.clients) < 1:
        console("Keine Clientkonfigurationen hinterlegt.", mode="warn", perm=True)
        return

    # Anzeige der Details pro Client, fettgedruckt: Bezeichnung, Anfang privater Schlüssel, IP-Adresse
    print(f"{Style.BRIGHT}{'#':4}{'Name':12} | {'Privater Schlüssel':18} | {'IP-Adresse':18}{Style.RESET_ALL}")
    pos = 1
    for client in server.clients:
        print(f"{Style.BRIGHT}{pos:<4}{Style.RESET_ALL}{client.name[:12]:12} | {client.privatekey[:15] + '...':18} | "
              f"{client.address}")  # IPv4 Adressen mit CIDR-Maske umfassen nie mehr als 18 Zeichen
        pos = pos + 1


def calculate_publickey(client):
    """
    Berechnet die öffentlichen Schlüssel der Clients anhand der privaten Schlüssel.
    """
    client.client_publickey = keys.pubkey(client.privatekey)

    console("Öffentlicher Schlüssel", client.client_publickey[:5] + "...", "für privaten Schlüssel",
            client.privatekey[:5] + "...", "berechnet und hinterlegt.", mode="succ")


def insert_client(server):
    """
    Erstellt eine neue Clientkonfiguration. Werte für Parameter werden über die Kosole eingegeben.
    """

    # TODO Bearbeitung von Server Peer-Parametern

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    # Ein neues ClientConfig Objekt wird erstellt, welches später zum ServerConfig Objekt hinzugefügt wird.
    new_client = ClientConfig()

    # Ein Schlüsselpaar wird generiert und hinterlegt.
    new_client.privatekey = keys.genkey()
    new_client.client_publickey = keys.pubkey(new_client.privatekey)

    # Der öffentliche Schlüssel des Servers wird hinterlegt
    new_client.publickey = keys.pubkey(server.privatekey)

    # Eingabe eines Namens
    name = input("Client anlegen (Name?) > ")
    new_client.name = name

    # Eingabe einer IP-Adresse
    while True:
        address = input("Client anlegen (IP-Adresse?) > ")
        try:
            new_client.address = ip_address(address)
        except ValueError:
            console("Ungültige Eingabe. Eingabe einer IPv4-Adresse erwartet.", mode="err", perm=True)
            continue
        break

    # Befindet sich die angegebene IP-Adresse im Subnetz des VPN-Servers?
    if new_client.address not in list(server.address.network.hosts()):
        console("IP-Adresse", new_client.address.ip, "ist nicht Teil des VPN-Netzwerks", server.address.network,
                mode="warn", perm=True, no_space=False)

    # Auf IP-Adresskonflikte prüfen
    if server.address.ip == new_client.address:
        console("Es liegt ein IP-Adresskonflikt vor. Der Server verwendet dieselbe IP-Adresse.", mode="warn", perm=True)

    index = 0
    for client in server.clients:
        console("Prüfe auf Übereinstimmung von", client.address, "mit", new_client.address, mode="info")
        index = index + 1
        if client.address == new_client.address:
            console("Es liegt ein IP-Adresskonflikt vor.", "Client " + str(index), "verwendet dieselbe IP-Adresse.",
                    mode="warn", perm=True)

    # Weitere Parameter abfragen, prüfen und einfügen
    console("Bitte weitere Parameter eintragen. Zurück mit", ".", mode="info", perm=True)
    # TODO BUG: Falsche Parameter werden nicht bemängelt
    while True:
        try:
            input_line = input("Client anlegen (zusätzliche Parameter?) > ")
        except UnicodeDecodeError:
            console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)

        # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
        match = re.search(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)

        # Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
        if match:
            # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
            key = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[1].strip()
            value = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[2].strip()
            console("Parameter", key, "mit Wert", value, "erkannt", mode="succ")

            console("Prüfe, ob der Parameter in der Menge der unterstützten Parameter enthalten ist.", mode="info")

            # Prüfe, ob der Parameter grundsätzlich gültig ist
            if key.lower() in config_parameters:
                # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                setattr(new_client, key.lower(), value)
                console("Parameter hinterlegt", mode="succ")
            else:
                console("Unbekannter Parameter", key, mode="warn", perm=True)
        elif input_line == ".":
            break
        else:
            console("Ungültige Eingabe.", mode="err", perm=True)
            # continue
    # Clientkonfiguration zur Serverkonfiguration hinzufügen
    server.clients.append(new_client)
    console("Client zur Konfiguration hinzugefügt.", mode="succ")


def delete_client(server, choice):
    """
    Entfernt eine bestehende Konfiguration der Parameter choice bestimmt, welche Konfiguration entfernt wird, 0
    entspricht der Serverkonfiguration. Clients haben aufsteigende Nummern ab 1.
    """

    # Parameterprüfungen
    client_id = validate_client_id(server, choice)
    if client_id is None:
        console("Breche ab.", mode="err", perm=True)
        return

    del server.clients[client_id - 1]


def change_client(server, choice):
    """
    Änderung einer bestehenden Konfiguration. Der Parameter choice bestimmt, welche Konfiguration angepasst wird.
    0 entspricht der Serverkonfiguration. Clients haben aufsteigende Nummern ab 1.
    """

    # TODO BUG MINIMAL_CONFIG_PARAMETERS dürfen nicht "" lauten. Prüfung notwendig.
    # TODO BUG name kann nicht geändert werden

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen in Kleinbuchstaben
    config_parameters = [parameter.lower() for parameter in CONFIG_PARAMETERS]

    # Vorbereitung auf Generierung einer Liste mit allen verfügbaren Parameternamen der Interface-Sektion in
    # Kleinbuchstaben
    interface_config_parameters = [parameter.lower() for parameter in INTERFACE_CONFIG_PARAMETERS]

    console("", "Parameter ", "ohne Wert eingeben für Ausgabe des derzeitigen Werts.", "Parameter = Wert",
            "eingeben für Änderung des Werts. Zurück mit", ".", mode="info", perm=True, no_space=True)

    if choice == "0":
        # Serverkonfiguration soll geändert werden. Es ist nur möglich, die Interface-Sektion zu bearbeiten. Peer-
        # Sektionen werden mit der Clientkonfiguration angepasst

        while True:
            try:
                input_line = input(f"{Style.BRIGHT}Konfiguration ändern (Server) > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)

            # TODO Refactoring: ausgelagerte Funktion aus parse_and_import() verwenden
            match_key_value = re.search(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)

            match_key = re.search(RE_MATCH_KEY, input_line, re.IGNORECASE)

            if input_line == ".":
                break

            # Prüfe, ob der Parameter ein unterstützter offizieller Parameter der Interface-Sektion ist
            if match_key_value:
                # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
                key = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[1].strip()
                value = re.split(RE_MATCH_KEY_VALUE, input_line, re.IGNORECASE)[2].strip()
                console("Parameter", key, "mit Wert", value, "erkannt.", mode="succ")

                console("Prüfe, ob der Parameter in der Menge der unterstützten Parameter enthalten ist.", mode="info")

                # Prüfe, ob der Parameter grundsätzlich gültig ist
                if key.lower() in interface_config_parameters:
                    # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                    setattr(server, key.lower(), value)
                    console("Parameter hinterlegt.", mode="succ")
                else:
                    console("Unbekannter Parameter", input_line, mode="warn", perm="True")

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
                    console("Unbekannter Parameter", key, mode="warn", perm=True)
            else:
                console("Ungültige Eingabe.", mode="err", perm=True)

    else:
        # Eine der Clientkonfigurationen soll geändert werden

        # Parameterprüfungen
        client_id = validate_client_id(server, choice)
        if client_id is None:
            console("Breche ab.", mode="err", perm=True)
            return

        while True:
            try:
                input_line = input(f"{Style.BRIGHT}Konfiguration ändern (Client {client_id}) > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)

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
                console("Parameter", key, "mit Wert", value, "erkannt", mode="succ")

                console("Prüfe, ob der Parameter in der Menge der unterstützten Parameter enthalten ist.", mode="info")

                # Prüfe, ob der Parameter grundsätzlich gültig ist
                if key.lower() in config_parameters:
                    # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                    setattr(server.clients[client_id-1], key.lower(), value)
                    console("Parameter hinterlegt", mode="succ")

                else:
                    console("Unbekannter Parameter", input_line, mode="warn", perm=True)

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
                    console("Unbekannter Parameter.", key, mode="warn", perm=True)

            else:
                console("Ungültige Eingabe.", mode="err", perm=True)


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
        console("Ändere das Schlüsselpaar des Servers.", mode="info")

        server.privatekey = keys.genkey()
        publickey = keys.pubkey(server.privatekey)

        for client in server.clients:
            client.publickey = publickey

    else:
        # Parameterprüfungen
        client_id = validate_client_id(server, choice)
        if client_id is None:
            console("Breche ab.", mode="err", perm=True)
            return

        console("Ändere das Schlüsselpaar des Clients", client_id, ".", mode="info")

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
        console("Eingabe einer Zahl erwartet.", mode="err", perm=True)
        return

    if number_of_hosts < len(server.clients):
        console("Die Konfiguration im Arbeitsspeicher umfasst", len(server.clients),
                "Clients. Es kann keine Netzwerkgröße für eine geringere Anzahl eingestellt werden. Breche ab.",
                mode="err", perm=True)
        return

    # CIDR-Maske berechnen
    cidr_mask = get_cidr_mask_from_hosts(number_of_hosts)
    if cidr_mask is None:  # Bei einem Fehler wird None zurückgegeben
        console("Breche ab.", mode="err", perm=True)
        return
    console("CIDR-Maske", cidr_mask, "berechnet.", mode="succ")

    # Netzklasse A, B oder C festlegen
    if cidr_mask >= 24:
        ip4_network_class = "c"
    elif cidr_mask >= 16:
        ip4_network_class = "b"
    elif cidr_mask >= 8:
        ip4_network_class = "a"
    else:
        console("Ungültige CIDR-Maske für ein privates Netzwerk berechnet. Breche ab.", mode="err", perm=True)
        return

    console("Netzklasse", ip4_network_class.upper(), "festgelegt.", mode="succ")

    # Geeignetes IPv4-Netzwerk festlegen
    if ip4_network_class == "a":
        ip4_network = ip_network(f'10.0.0.0/{cidr_mask}')
    elif ip4_network_class == "b":
        ip4_network = ip_network(f'172.16.0.0/{cidr_mask}')
    elif ip4_network_class == "c":
        ip4_network = ip_network(f'192.168.0.0/{cidr_mask}')
    else:
        console("Berechnung des Subnets ungültig. Breche ab.", mode="err", perm=True)
        return

    console("Neues Subnetz", ip4_network, "wird verwendet.", mode="succ")

    list_of_host_addr = list(ip4_network.hosts())

    # Dem Server die letzte IP-Adresse im Subnetz zuweisen
    try:
        console("Weise dem Server die IP-Adresse", list_of_host_addr[-1], "zu.", mode="info")
        server.address = list_of_host_addr[-1]
    except AttributeError:
        console("Es ist keine Serverkonfiguration vorhanden. Neue erstellen oder importieren. Breche ab.",
                mode="err", perm=True)

    # Den Clients vom Anfang aufsteigende Adressen zuweisen
    for i in range(len(server.clients)):
        server.clients[i].address = list_of_host_addr[i]
        console("Weise Client mit privatem Schlüssel", f"{server.clients[i].privatekey:5}" + "...", "die IP-Adresse",
                list_of_host_addr[i], "zu.", mode="info")


def update_client_config_parameter(peer, parameter, value):
    """
    Setzt den Wert eines Parameters in der Datenstruktur im Arbeitsspeicher für einen Peer (Server oder Client)
    """


def print_qr_code(server, choice):
    """
    Gibt die Konfiguration eines Clients auf der Konsole als QR-Code aus. Der Code kann mit der WireGuard App für
    Android und iOS eingelesen und die Konfiguration so komfortabel importiert werden.
    """

    # Parameterprüfungen
    client_id = validate_client_id(server, choice)
    if client_id is None:
        console("Breche ab.", mode="err", perm=True)
        return

    # QR-Code für server.clients[client_id] ausgeben
    client_qr_code = qrcode.QRCode()
    client_qr_code.add_data(config_to_str(server, client_id))
    output = io.StringIO()
    client_qr_code.print_ascii(out=output)
    output.seek(0)
    print(output.read())


def validate_client_id(server, choice):
    """
    Prüft, ob der übergebene Parameter ein Ganzzahl-Objekt ist und ein Client mit dieser ID existiert.
    """

    try:
        client_id = int(choice)
    except ValueError:
        console("Eingabe einer Zahl erwartet.", mode="err", perm=True)
        return None
    try:
        if len(server.clients) < client_id:
            console("Konfiguration", client_id, "existiert nicht", mode="err", perm=True)
            return None
    # Wenn das Attribut clients nicht vorhanden ist, ist server nicht von der Klasse ServerConfig
    except AttributeError:
        console("Keine Konfiguration im Arbeitsspeicher hinterlegt. Neue Konfiguration importieren oder anlegen.",
                mode="err", perm=True)
        return None

    return client_id


def server_config_exists(server):
    """
    Überprüft, ob eine Serverkonfiguration vorliegt.
    """
    if server is None:
        console("Es existiert keine Konfiguration im Arbeitsspeicher. Neue Konfiguration importieren oder "
                "anlegen.", mode="err", perm=True)
        return False
    return True
