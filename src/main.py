"""

Projekt Anwendungsentwicklung im Sommersemester 2022
Jonas Berger, Fachhochschule Südwestfalen

Thema: Entwicklung eines Konfigurationsgenerators für WireGuard VPN

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
from constants import WG_DIR
from debugging import console
from exporting import export_configurations
from exporting import config_to_str
from file_management import check_dir


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

        try:
            check_dir(WG_DIR)
        except (FileNotFoundError, NotADirectoryError):
            console("Konfiguration aus dem Arbeitsspeicher kann in diesem Zustand nicht auf das Dateisystem geschrieben"
                    " werden. Bitte den Parameter", "WG_DIR", "in der Datei", "constants.py", "anpassen.", mode="err",
                    perm=True)
        except PermissionError:
            console("Konfiguration aus dem Arbeitsspeicher kann in diesem Zustand nicht auf das Dateisystem geschrieben"
                    " werden. Bitte den Parameter", "WG_DIR", "in der Datei", "constants.py",
                    "anpassen oder das Programm mit erhöhten Benutzerberechtigungen ausführen.", mode="err", perm=True)

        option = ""
        while True:
            try:
                option = input(f"{Style.BRIGHT}Hauptmenü > {Style.RESET_ALL}")
            except UnicodeDecodeError:
                console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                continue
            break

        if option == "1":
            console("Importiere Verbindungen...", mode="info")
            if server is not None:
                console("Konfiguration im Arbeitsspeicher überschreiben?", "[j/n]", mode="warn", perm=True)
                choice = ""
                while True:
                    try:
                        choice = input(f"{Style.BRIGHT}Verbindungen importieren (Bestätigung) > {Style.RESET_ALL}")
                    except UnicodeDecodeError:
                        console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                        continue
                    break
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
                choice = ""
                while True:
                    try:
                        choice = input(f"{Style.BRIGHT}Details anzeigen > {Style.RESET_ALL}")
                    except UnicodeDecodeError:
                        console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                        continue
                    break
                if choice == ".":
                    continue
                print(config_to_str(server, choice))
        elif option == "3":
            if server is None:
                console("Keine Serverkonfiguration vorhanden. Soll eine neue Konfiguration im Arbeitsspeicher angelegt "
                        "werden?", "(j/n)", mode="warn", perm="True")
                choice = ""
                while True:
                    try:
                        choice = input(f"{Style.BRIGHT}Konfiguration anlegen (Bestätigung) > {Style.RESET_ALL}")
                    except UnicodeDecodeError:
                        console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                        continue
                    break

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
                choice = ""
                while True:
                    try:
                        choice = input(f"{Style.BRIGHT}Konfiguration entfernen (Auswahl) > {Style.RESET_ALL}")
                    except UnicodeDecodeError:
                        console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                        continue
                    break
                if choice == "0":
                    console("Gesamtkonfiguration aus dem Arbeitsspeicher entfernen?", "(j/n)", mode="warn", perm=True)
                    choice = ""
                    while True:
                        try:
                            choice = input(f"{Style.BRIGHT}Konfiguration entfernen (Bestätigung) > {Style.RESET_ALL}")
                        except UnicodeDecodeError:
                            console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                            continue
                        break
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
            if server is None:
                repeat = False
            else:
                console("Es liegen ungespeicherte Änderungen vor. Wirklich verlassen?", "(j/n)", mode="warn", perm=True)
                while True:
                    choice = ""
                    try:
                        choice = input(f"{Style.BRIGHT}Verlassen (Bestätigung) > {Style.RESET_ALL}")
                    except UnicodeDecodeError:
                        console("Ungültige Eingabe. Bitte keine Akzente eingeben.", mode="err", perm=True)
                        continue
                    break
                if choice == "j":
                    repeat = False
                elif choice == "n":
                    console("Vorgang abgebrochen", mode="info", perm=True)
                else:
                    console("Ungültige Eingabe. Für Hilfe", "?", "eingeben.", mode="err", perm=True)


if __name__ == "__main__":
    sys.exit(main())
