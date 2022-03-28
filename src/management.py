# Öffentliche Imports
from colorama import Fore, Style

# Interne Imports
from constants import MINIMAL_CONFIG_PARAMETERS
from ServerConfig import ServerConfig

"""
Enthält alle Funktionen für das Verwalten und Anzeigen von importierten Konfigurationen.
"""


def print_configurations(server):
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
        print("Fehler: keine Clientkonfigurationen hinterlegt.")
        return

    # Anzeige der Details pro Client: Bezeichnung, IP-Adresse, Anfang öffentlicher Schlüssel
    print(f"{Style.BRIGHT}", end="")
    print("{0:12} | {1:18}".format("Name", f"Privater Schlüssel{Style.RESET_ALL}"))
    for client in server.clients:
        print("{0:12} | {1:18}".format(client.name[:12], client.privatekey[:15] + "..."))


def check_configuration_integrity(server):
    """
    Prüft die importierten Konfigurationen auf Plausibilität und Vollständigkeit.
    """

    # Prüfung, ob alle Clients in der Serverkonfiguration vorhanden sind.

    # Prüfung, ob alle Clients aus der Serverkonfiguration vorhanden sind.

    # Prüfung, ob die privaten und öffentlichen Schlüssel der Clients zueinander passen.

    # Prüfung, ob IP-Adresskonflikte vorliegen.