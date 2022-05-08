"""

Projekt Anwendungsentwicklung im Sommersemester 2022
Jonas Berger, Fachhochschule Südwestfalen

Thema: Entwicklung eines Konfigurationsgenerators für WireGuard VPN

! Wireguard Konfigurationsdateien sind case-insensitive
! configparser kann nicht verwendet werden, da [Peer] in Serverkonfigurationen mehrfach vorkommt
! INI-Syntax wird nicht vollständig abgebildet: s.o., Name muss als Kommentar eingefügt werden
? Erweiterbarkeit: Datenstruktur als abgeleitete Klasse von dict (kompliziert, wird von abgeraten) vs. dict (primitiv)
  vs. neue abgeleitete Klasse (schönste Lösung, umständliche Erweiterung)
! Schlüsselgenerierung: https://github.com/k4yt3x/wg-meshconf/blob/master/wg_meshconf/wireguard.py
! Syntaxprüfung mit pylint, Formatierung nach PEP 8
! base64 Schlüssel enthalten 0-2 Gleichheitszeichen am Ende
! Ausblick: Erweiterung, sodass mehrere Server verwaltet werden können, möglich
! Aufgrund von Dateisystemen und unterschiedlichen Entwicklungsanforderungen unterscheiden sich Dateisysteminteraktionen
  zwischen Unix und Windows u.U. grundsätzlich: https://stackoverflow.com/questions/8107352/force-overwrite-in-os-rename
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Das Hauptmenü lässt sich nicht durch Refactoring verkleinern. Daher:
# pylint: disable=too-many-branches, too-many-statements

# Imports aus Standardbibliotheken
import sys

# Imports von Drittanbietern
from colorama import Fore, init, Style  # Für vom Betriebssystem unabhängige farbige Ausgaben

# Eigene Imports
from importing import import_configurations
from config_management import print_configuration
from config_management import change_client
from config_management import change_client_keypair
from config_management import change_network_size
from config_management import create_server_config
from config_management import delete_client
from config_management import insert_client
from config_management import print_qr_code
from config_management import server_config_exists
from debugging import console
from exporting import export_configurations
from exporting import config_to_str


def print_menu():
    """
    Gibt eine Informationsmeldung aus, welche Optionen im Hauptmenü zur Verfügung stehen.
    """
    print(f"{Style.BRIGHT}1{Style.RESET_ALL} --> Konfiguration vom Dateisystem in den Arbeitsspeicher importieren")
    print(f"{Style.BRIGHT}2{Style.RESET_ALL} --> Übersicht und Details anzeigen")
    print(f"{Style.BRIGHT}3{Style.RESET_ALL} --> Client hinzufügen/ Neue Konfiguration anlegen")
    print(f"{Style.BRIGHT}4{Style.RESET_ALL} --> Client entfernen/ Konfiguration verwerfen")
    print(f"{Style.BRIGHT}5{Style.RESET_ALL} --> Konfiguration ändern")
    print(f"{Style.BRIGHT}6{Style.RESET_ALL} --> Schlüsselpaar eines Clients neu generieren")
    print(f"{Style.BRIGHT}7{Style.RESET_ALL} --> Anpassung der Netzwerkgröße")
    print(f"{Style.BRIGHT}8{Style.RESET_ALL} --> QR-Code für mobilen Client generieren")
    print(f"{Style.BRIGHT}9{Style.RESET_ALL} --> Konfiguration vom Arbeitsspeicher auf das Dateisystem exportieren")
    print("---------------------------------")
    print(f"{Style.BRIGHT}?{Style.RESET_ALL} --> Diesen Text anzeigen")
    print(f"{Style.BRIGHT}0{Style.RESET_ALL} --> Verlassen")


def main():
    """
    Hauptmenü.
    """
    server = None
    init()  # Colorama passt sich an das Betriebssystem an

    print(f"{Style.BRIGHT}{Fore.RED}WireGuard{Fore.RESET} Konfigurationsverwalter{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}#################################{Style.RESET_ALL}")
    print_menu()

    repeat = True
    while repeat:
        console("Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.", mode="info")

        option = input(f"{Style.BRIGHT}Hauptmenü > {Style.RESET_ALL}")

        if option == "1":
            console("Importiere Verbindungen...", mode="info")
            if server is not None:
                console("Konfiguration im Arbeitsspeicher überschreiben?", "[j/n]", mode="warn", perm=True)
                choice = input("Verbindungen importieren (Bestätigung) > ")
                if choice != "j":
                    console("Vorgang abgebrochen", mode="info", perm=True)
                    continue
            try:
                server = import_configurations()
            except OSError:
                console("Vorgang abgebrochen.", mode="info", perm=True)
            console("Verbindungen importiert.", mode="succ")
        elif option == "2":
            if server_config_exists(server):
                print_configuration(server)
                console("Für Details", "ID", "eingeben, ", "0", "für den Server. Zurück zum Hauptmenü mit", ".",
                        mode="info", perm=True)
                choice = input(f"{Style.BRIGHT}Details anzeigen > {Style.RESET_ALL}")
                if choice == ".":
                    continue
                print(config_to_str(server, choice))
        elif option == "3":
            if server is None:
                console("Keine Serverkonfiguration vorhanden. Soll eine neue Konfiguration im Arbeitsspeicher angelegt "
                        "werden?", "(j/n)", mode="warn", perm="True")
                choice = input("Konfiguration anlegen (Bestätigung) > ")

                if choice == "j":
                    server = create_server_config()
                    console("Serverkonfiguration angelegt. Es folgt die Erstellung einer Clientkonfiguration",
                            mode="info", perm=True)
                else:
                    console("Vorgang abgebrochen.", mode="info", perm=True)
                    continue
            insert_client(server)
        elif option == "4":
            if server_config_exists(server):
                console("Bitte", "ID", "des Clients eingeben,", 0, "für den Server. Zurück zum Hauptmenü mit", ".",
                        mode="info", perm=True)
                choice = input("Konfiguration entfernen (Auswahl) > ")
                if choice == "0":
                    console("Gesamtkonfiguration aus dem Arbeitsspeicher entfernen?", "(j/n)", mode="warn", perm=True)
                    choice = input("Konfiguration entfernen (Bestätigung) > ")
                    if choice != "j":
                        console("Vorgang abgebrochen", mode="info", perm=True)
                        continue
                    server = None
                    continue
                delete_client(server, choice)
        elif option == "5":
            if server_config_exists(server):
                console("Bitte", "ID", "des Clients eingeben,", 0, "für den Server. Zurück zum Hauptmenü mit", ".",
                        mode="info", perm=True)
                try:
                    choice = input(f"{Style.BRIGHT}Konfiguration ändern (Auswahl) > {Style.RESET_ALL}")
                except UnicodeDecodeError:
                    console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                    continue
                change_client(server, choice)
        elif option == "6":
            if server_config_exists(server):
                console("Bitte", "ID", "des Clients eingeben,", 0, "für den Server. Zurück zum Hauptmenü mit", ".",
                        mode="info", perm=True)
                try:
                    choice = input(f"{Style.BRIGHT}Schlüsselpaar erneuern (Auswahl) > {Style.RESET_ALL}")
                except UnicodeDecodeError:
                    console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                    continue
                change_client_keypair(server, choice)
        elif option == "7":
            if server_config_exists(server):
                console("Wie viele Hosts sollen im Netzwerk insgesamt verwaltet werden (Clients + Server)?",
                        mode="info", perm=True)
                try:
                    choice = input(f"{Style.BRIGHT}Netzwerkgröße anpassen (Auswahl) > {Style.RESET_ALL}")
                except UnicodeDecodeError:
                    console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                    continue
                change_network_size(server, choice)
        elif option == "8":
            if server_config_exists(server):
                console("Welche Clientkonfiguration soll ausgegeben werden?", mode="info", perm=True)
                try:
                    choice = input(f"{Style.BRIGHT}QR-Code ausgeben (Auswahl) > {Style.RESET_ALL}")
                except UnicodeDecodeError:
                    console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                    continue
                print_qr_code(server, choice)
        elif option == "9":
            if server_config_exists(server):
                export_configurations(server)
        elif option == "?":
            print_menu()
        elif option == "0":
            repeat = False
        else:
            console("Ungültige Eingabe. Für Hilfe", "?", "eingeben.", mode="err", perm=True)


if __name__ == "__main__":
    sys.exit(main())
