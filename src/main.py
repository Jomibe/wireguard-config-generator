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
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken
import sys

# Imports von Drittanbietern
from colorama import init, Fore, Style  # Für vom Betriebssystem unabhängige farbige Ausgaben

# Eigene Imports
from importing import import_configurations
from config_management import print_configuration
from config_management import change_client
from config_management import create_server_config
from config_management import delete_client
from config_management import insert_client
from config_management import print_details
from constants import DEBUG
from server_config import ServerConfig


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
        if DEBUG:
            print(f"{Fore.BLUE}Info: Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.{Style.RESET_ALL}")

        option = input(f"{Style.BRIGHT}Hauptmenü > {Style.RESET_ALL}")

        if option == "1":
            if DEBUG:
                print(f"{Fore.BLUE}Info: Importiere Verbindungen...{Style.RESET_ALL}")
            if server is not None:
                choice = input(f"{Fore.YELLOW}Warnung: Konfiguration im Arbeitsspeicher überschreiben?{Style.RESET_ALL}"
                               f" [j/n]")
                if choice != "j":
                    print(f"{Fore.BLUE}Info: Vorgang abgebrochen{Style.RESET_ALL}")
                    continue
            server = import_configurations()
            if DEBUG:
                print(f"{Fore.GREEN}Erfolg: Verbindungen importiert{Style.RESET_ALL}")
        elif option == "2":
            if server is None:
                print(f"{Fore.RED}Fehler: Es existiert keine Konfiguration im Arbeitsspeicher. Neue Konfiguration "
                      f"importieren oder anlegen.{Style.RESET_ALL}")
                continue
            print_configuration(server)
            print(f"{Fore.BLUE}Info: Für Details {Style.RESET_ALL}ID{Fore.BLUE} eingeben, {Style.RESET_ALL}0{Fore.BLUE}"
                  f" für den Server. Zurück zum Hauptmenü mit {Style.RESET_ALL}.")
            while True:
                choice = input(f"{Style.BRIGHT}Details anzeigen > {Style.RESET_ALL}")
                if choice == ".":
                    break
                print_details(server, choice)
        elif option == "3":
            if server is None:
                print(f"{Fore.RED}Fehler: keine Serverkonfiguration vorhanden. Soll eine neue Konfiguration im "
                      f"Arbeitsspeicher angelegt werden? (j/n){Style.RESET_ALL}")
                choice = input()

                if choice == "j":
                    server = create_server_config()
                    print(f"{Fore.BLUE}Info: Serverkonfiguration angelegt. Es folgt die Erstellung einer "
                          f"Clientkonfiguration{Style.RESET_ALL}")
                else:
                    print(f"{Fore.BLUE}Info: Vorgang abgebrochen.{Style.RESET_ALL}")
                    continue
            insert_client(server)
        elif option == "4":
            choice = input("ID? ")
            if choice == "0":
                choice = input(f"{Fore.YELLOW}Warnung: Gesamtkonfiguration aus dem Arbeitsspeicher entfernen?"
                               f"{Style.RESET_ALL} (j/n)")
                if choice != "j":
                    print(f"{Fore.BLUE}Info: Vorgang abgebrochen{Style.RESET_ALL}")
                    continue
                server = None
                continue
            delete_client(server, choice)
        elif option == "5":
            print(f"{Fore.BLUE}Info: Bitte {Style.RESET_ALL}ID{Fore.BLUE} des Clients eingeben, {Style.RESET_ALL}0"
                  f"{Fore.BLUE} für den Server. Zurück zum Hauptmenü mit {Style.RESET_ALL}.")
            try:
                choice = input(f"{Style.BRIGHT}Konfiguration ändern (Auswahl) > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                print(f"{Fore.RED}Fehler: Ungültige Eingabe. Bitte keine Akzente eingeben.")
                continue
            change_client(server, choice)
        elif option == "?":
            print_menu()
        elif option == "0":
            repeat = False
        else:
            print(f"{Fore.RED}Fehler: Ungültige Eingabe. Für Hilfe {Style.RESET_ALL}?{Fore.RED} eingeben"
                  f"{Style.RESET_ALL}")


if __name__ == "__main__":
    sys.exit(main())
