"""

Projekt Anwendungsentwicklung im Sommersemester 2022
Jonas Berger, Fachhochschule Südwestfalen

Thema: Entwicklung eines Konfigurationsgenerators für WireGuard VPN

! Wireguard Konfigurationsdateien sind case-insensitive
! configparser kann nicht verwendet werden, da [Peer] in Serverkonfigurationen mehrfach vorkommt
! INI-Syntax wird nicht vollständig abgebildet: s.o., Name muss als Kommentar eingefügt werden
? Erweiterbarkeit: Datenstruktur als abgeleitete Klasse von dict (kompliziert, wird von abgeraten) vs. dict (primitiv)
  vs. neue abgeleitete Klasse (schönste Lösung, umständliche Erweiterung)
"""

# Öffentliche Imports
from colorama import init, Fore, Style  # Für vom Betriebssystem unabhängige farbige Ausgaben
import sys

# Interne Imports
from importing import import_configurations
from management import print_configurations
from ServerConfig import ServerConfig
from constants import DEBUG


def main():
    """
    Hauptmenü.
    """
    server = ServerConfig()
    init()  # Colorama passt sich an das Betriebssystem an

    repeat = True
    while repeat:
        print("Wireguard Konfigurationsverwalter")
        print("#################################")
        print(" 1 --> Übersicht erstellen")
        print(" 2 --> Konfigurationen ändern")
        print(" 3 --> Schlüsselpaar des Servers neu generieren")
        print(" 4 --> Aktualisierung der Netzwerkgröße")
        print(" 5 --> QR-Code generieren")
        print("---------------------------------")
        print(" 0 --> Verlassen")

        if DEBUG:
            print(f"{Fore.BLUE}Info: Detaillierte Ausgaben zum Programmablauf sind eingeschaltet.{Style.RESET_ALL}")

        option = input("? ")

        if option == "1":
            if DEBUG:
                print(f"{Fore.BLUE}Info: Importiere Verbindungen...{Style.RESET_ALL}")
            import_configurations(server)
            if DEBUG:
                print(f"{Fore.GREEN}Erfolg: Verbindungen importiert{Style.RESET_ALL}")
            print_configurations(server)
        elif option == "0":
            repeat = False


if __name__ == "__main__":
    sys.exit(main())
