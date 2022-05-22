"""
Enthält alle Funktionen für das Importieren von Konfigurationen auf dem Dateisystem in interne Datenstrukturen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import glob  # Für das Auffinden von Konfigurationsdateien mittels Wildcard
import re  # Für das Parsen von Konfigurationsdateien
from ipaddress import IPv4Interface, ip_address  # Für Berechnungen der Netzwerktechnik

# Imports von Drittanbietern

# Eigene Imports
from config_management import calculate_publickey
from constants import CONFIG_PARAMETERS
from constants import WG_DIR
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import SERVER_CONFIG_FILENAME
from constants import PEER_CONFIG_PARAMETERS
from debugging import console
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
    try:
        check_file(peer.filename)
    except OSError:  # Superklasse von FileNotFoundError, PermissionError und NotADirectoryError
        console("Breche ab.", mode="err", perm=True)
        return None

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
        console("Serverkonfiguration erkannt", mode="succ")
        if peer.filename != WG_DIR + SERVER_CONFIG_FILENAME:
            console("Serverkonfiguration", peer.filename, "entspricht nicht dem Standard",
                    WG_DIR + SERVER_CONFIG_FILENAME, mode="info")
    elif isinstance(peer, ClientConfig):
        console("Clientkonfiguration erkannt", mode="succ")
    else:
        console("Ungültige Datenstruktur vom Typ", type(peer), "übergeben.", mode="err")

    # Öffnen der Datei
    with open(peer.filename, encoding='utf-8') as config:
        # Datei Zeile für Zeile einlesen
        console("Lese Datei", peer.filename, mode="info")
        for line in config:
            # Zeile ohne \n ausgeben
            console("Lese Zeile", line.replace('\n', ''), mode="info")
            # Die Zeile wird auf Bestandteile der Syntax untersucht: leer, Kommentar, Sektion oder Name-Wert Paar
            match = re.search(r'^ *$', line)  # Leere Zeile darf keine oder nur Leerzeichen enthalten
            # Bei leerer Zeile: fahre fort
            if match:
                console("Zeile enthält keine Konfiguration.", mode="succ")
                continue

            match = re.search(r'^\[.*]$', line)
            # Bei Sektion: Unterscheide zwischen Server und Client. Client: fahre fort. Server: Importiere Daten in die
            # Datenstruktur des Clients.
            if match:
                console("Zeile leitet eine INI-Sektion ein.", mode="succ")

                # Hier können vier Fälle vorliegen: Client und [Interface], Client und [Peer], Server und [Interface]
                # sowie Server und [Peer]. In den ersten drei genannten Fällen kann die Zeile mit der Sektionsdefinition
                # ignoriert werden, es gibt in den beiden Sektionen keine doppelten Parameter. Die Parameter können
                # daher problemlos einer Sektion zugeordnet werden. Sonderfall Server und [Peer]: diese kommt so häufig
                # vor, wie es Clients gibt. Daher muss diese vollständig erfasst und abgespeichert werden.

                match = re.search(r'^ *\[Peer] *$', line, re.IGNORECASE)
                if match and is_server:
                    console("Zeile leitet eine Peer-Sektion ein.", mode="succ")

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
                console("Kommentar erkannt", mode="succ")
                if peer.name == "":
                    # Rauten (#), Leerzeichen sowie ein ggf. voranstehendes 'Name =' werden entfernt
                    peer.name = line.replace('\n', '').replace("Name", "").replace("=", "").replace("#", "").strip()
                    console("Bezeichnung", peer.name, "hinterlegt.", mode="succ")
                else:
                    console("Es sind mehrere kommentierte Zeilen in der Datei vorhanden. Der erste Kommentar wurde als "
                            "Bezeichnung interpretiert, dieser und folgende Kommentare werden ignoriert.", mode="info")
                continue

            match = re.search("^([^ ]*) *= *(.*)", line, re.IGNORECASE)
            # Name und Wert werden ohne Leerzeichen zur Weiterverarbeitung gespeichert
            key = re.split("^([^ ]*) *= *(.*)", line, re.IGNORECASE)[1].strip()
            value = re.split("^([^ ]*) *= *(.*)", line, re.IGNORECASE)[2].strip()
            console("Parameter", key, "mit Wert", value, "erkannt.", mode="succ")
            # Bei Name-Wert Paar: Prüfe, ob der Parameter ein unterstützter offizieller Parameter ist
            if match:
                console("Prüfe, ob der Parameter in der Menge der unterstützten Parameter enthalten ist.", mode="info")
                # Prüfe, ob der Parameter Teil einer Peer-Sektion einer Serverkonfiguration ist
                if key.lower() in peer_config_parameters and is_server:
                    # Falls ja, Parameter nicht im peer-Objekt hinterlegen, sondern im client_data Objekt vorhalten
                    setattr(client_data, key.lower(), value)
                    console("Ein Parameter aus einer Server-Peer Sektion wurde für die spätere Verarbeitung "
                            "zurückgestellt.", mode="succ")

                # Sonst: prüfe, ob der Parameter grundsätzlich gültig ist
                elif key.lower() in config_parameters:
                    # Falls ja, übernehme den Wert des Parameters in der Datenstruktur
                    setattr(peer, key.lower(), value)
                    console("Parameter hinterlegt.", mode="succ")
                    # "Streiche" den Parameter von der Liste der notwendigen Parameter, falls vorhanden
                    if key.lower() in minimal_parameters:
                        console("Parameter", key.lower(), "war in der Liste der notwendigen Parameter enthalten",
                                mode="succ")
                        minimal_parameters.remove(key.lower())

                # Falls nein: gebe eine entsprechende Warnung aus
                else:
                    console("Kein gültiger Parameter in Zeile", line.replace('\n', ''), "erkannt", mode="err",
                            perm=True)
                continue

            # Ist keine Übereinstimmung zu finden, ist die Zeile ungültig
            console("Die Zeile ist ungültig:", line.replace('\n', ''), mode="err", perm=True)

        # Sobald das Ende der Datei erreicht ist, prüfe ob notwendige Konfigurationsparameter importiert wurden
        if len(minimal_parameters) > 0:
            console("Datei", re.split(WG_DIR, peer.filename)[1], "enthält nicht die erforderlichen Parameter",
                    MINIMAL_CONFIG_PARAMETERS, mode="warn", perm=True)

        # und für den Fall, dass eine Peer-Sektion endet: übertrage Daten von client_data in das server Objekt.
        if isinstance(client_data, Peer):  # Falls eine Peer-Sektion verarbeitet wurde
            assign_peer_to_client(client_data, peer)  # peer ist in diesem Fall immer ein Objekt der Klasse ServerConfig

        # PEP 8: Either all return statements in a function should return an expression, or none of them should.
        return None


def assign_peer_to_client(client_data, server):
    """
    client_data enthält Konfigurationsparameter aus der Peer-Sektion einer Serverkonfiguration. Die Daten müssen einem
    bereits importierten Client anhand des öffentlichen Schlüssels zugeordnet werden. Dazu wird das Attribut publickey
    der Objekte in server.clients[] mit dem Attribut client_data.publickey verglichen.
    """

    # Prüfung, ob client_data einen öffentlichen Schlüssel enthält
    # Falls nicht, ist eine Zuordnung unmöglich
    if client_data.publickey == "":
        console("Eine Peer-Sektion aus der Serverkonfiguration kann keinem Client zugeordnet werden. Die Peer-Sektionen"
                " müssen einen Wert für PublicKey enthalten. Bitte die Sektion mit folgenden Werten prüfen: ", end="",
                mode="warn", perm=True)

        additional_values = False
        for parameter in PEER_CONFIG_PARAMETERS:
            if getattr(client_data, parameter.lower()) != "":
                print(f"{parameter} = {getattr(client_data, parameter.lower())}", end="")  # console()
                additional_values = True

        if not additional_values:
            console("es handelt sich um eine leere Peer-Sektion.", mode="warn", quiet=True, perm=True)
        else:
            print("")  # Zeilenumbruch

    # Falls ein öffentlicher Schlüssel hinterlegt wurde, diesen mit den vorhandenen Schlüsseln abgleichen
    else:
        # Vorbereitung für den Programmablauf nach erfolgreicher Übertragung der Parameter in das server-Objekt
        success = False

        console("Zuordnung der Client-Sektion zu vorhandenen Clients.", mode="info")
        for client in server.clients:
            console("Vergleiche Schlüssel aus der Peer-Sektion", client_data.publickey, "mit hinterlegtem Schlüssel",
                    client.client_publickey, "...", mode="info")
            if client.client_publickey == client_data.publickey:
                console("Übereinstimmung gefunden", mode="succ")
                # Daten übertragen
                console("Beginne mit der Übertragung der Parameter", mode="info")
                for parameter in PEER_CONFIG_PARAMETERS:
                    # Die Parameter aus den Peer-Sektionen der Serverkonfiguration werden clientspezifisch gespeichert.
                    # Da in den Konfigurationen der Clients auch eine Peer-Sektion vorkommt, wird den Parametern aus
                    # der Serverkonfiguration ein 'client_' vorangestellt.
                    setattr(client, "client_" + parameter.lower(), getattr(client_data, parameter.lower()))
                console("Parameter erfolgreich übernommen", mode="succ")
                success = True

        if not success:
            console("Eine Peer-Sektion konnte keinem Client zugeordnet werden, da kein übereinstimmender öffentlicher "
                    "Schlüssel in der Konfiguration enthalten ist. Das Schlüsselpaar ist ungültig oder die "
                    "Konfigurationsdatei ist nicht mehr vorhanden. Bitte in der Serverkonfiguration", WG_DIR +
                    SERVER_CONFIG_FILENAME, "die Sektion mit dem öffentlichen Schlüssel", client_data.publickey,
                    "prüfen. Die Clientkonfiguration wird andernfalls beim nächsten Export verworfen.", mode="warn",
                    perm=True)


def import_configurations():
    """
    Importiert alle VPN-Konfigurationen im Wireguard-Verzeichnis.
    """

    server = ServerConfig()

    try:
        check_dir(WG_DIR)
    except OSError:  # Superklasse von FileNotFoundError, PermissionError und NotADirectoryError
        console("Breche ab.", mode="err", perm=True)
        return None

    # Einlesen der Konfigurationsdateien *.conf

    # Liste mit Dateinamen erstellen
    list_client_configuration_filenames = glob.glob(f"{WG_DIR}*.conf")

    # Dateiname der Serverkonfiguration ausschließen und damit prüfen, ob diese existiert
    try:
        list_client_configuration_filenames.remove(server.filename)
    except ValueError:
        console("Keine Serverkonfiguration", "wg0.conf", "gefunden.", mode="warn", perm=True)

    # Zu importierende Clientkonfigurationen anzeigen
    console("Neben der Serverkonfiguration wurden folgende Clientkonfigurationen gefunden:",
            list_client_configuration_filenames, mode="info")

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

        # Anpassung des Parameters address in den Clientkonfigurationen. Das Zeichenketten-Objekt wird in ein
        # IP4Interface-Objekt umgewandelt.
        server.clients[-1].address = ip_address(IPv4Interface(server.clients[-1].address).ip)
        console("IP-Adresse", server.clients[-1].address, "erfasst.", mode="succ")

        console("Folgende Clients wurden importiert:", mode="succ")
        for client in server.clients:
            console("Client", str(client.name), "mit privatem Schlüssel", str(client.privatekey), mode="succ",
                    quiet=True)

    # ..des Servers
    try:
        parse_and_import(server)
    except OSError:
        console("Breche ab.", mode="err", perm=True)
        return None

    # Anpassung des Parameters address in der Serverkonfiguration. Das Zeichenketten-Objekt wird in ein
    # IP4Interface-Objekt umgewandelt. Dieses enthält eine IPv4-Adresse inkl. Maske.
    server.address = IPv4Interface(server.address)
    if server.address.network.is_private is not True:
        console("Das VPN-Netzwerk ist kein von der IANA für private Zwecke reserviertes Netzwerk.", mode="warn",
                perm=True)

    # Prüfung, ob die IP-Adressen der Clients im Subnetz des Servers liegen
    index = 0
    for client in server.clients:
        index = index + 1
        if client.address not in list(server.address.network.hosts()):
            console("IP-Adresse", client.address.ip, "von", "Client" + str(index), "ist nicht Teil des VPN-Netzwerks",
                    server.address.network, mode="warn", perm=True, no_space=False)

    return server
