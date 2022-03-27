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
import sys

# Interne Imports
from importing import import_configurations
from ServerConfig import ServerConfig


def main():
    """
    Hauptmenü.
    """
    server = ServerConfig()

    repeat = True
    while repeat:
        print("Wireguard Konfigurationsverwalter")
        print("#################################")
        print(" 1 --> Übersicht erstellen")
        print(" 2 --> Konfigurationen ändern")
        print(" 3 --> Schlüsselpaar des Servers neu generieren")
        print(" 4 --> Aktualisierung der Netzwerkgröße")
        print(" 5 --> QR-src generieren")
        print("---------------------------------")
        print(" 0 --> Verlassen")

        option = input("? ")

        if option == "1":
            print("Importiere Verbindungen...", "")
            import_configurations(server)
        elif option == "0":
            repeat = False


if __name__ == "__main__":
    sys.exit(main())
