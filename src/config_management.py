"""
Enthält alle Funktionen für das Verwalten und Anzeigen von importierten Konfigurationen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports von Drittanbietern
from colorama import Fore, Style

# Eigene Imports
from constants import MINIMAL_CONFIG_PARAMETERS
from constants import DEBUG
from server_config import ServerConfig
from keys import pubkey


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

    # Anzeige der Details pro Client, fettgedruckt: Bezeichnung, IP-Adresse, Anfang öffentlicher Schlüssel
    print(f"{Style.BRIGHT}{'Name':12} | {'Privater Schlüssel':18}{Style.RESET_ALL}")
    for client in server.clients:
        print(f"{client.name[:12]:12} | {client.privatekey[:15] + '...':18}")


def calculate_publickey(client):
    """
    Berechnet die öffentlichen Schlüssel der Clients anhand der privaten Schlüssel.
    """
    client.client_publickey = pubkey(client.privatekey)
    if DEBUG:
        print(f"{Fore.GREEN}Erfolg: Öffentlicher Schlüssel {Style.RESET_ALL}{client.client_publickey[:5]}..."
              f"{Fore.GREEN} für privaten Schlüssel{Style.RESET_ALL} {client.privatekey[:5]}...{Fore.GREEN} "
              f"berechnet und hinterlegt.{Style.RESET_ALL}")

    # def change_server_keypair(server):
    """
    Generiert ein neues Schlüsselpaar. Hinterlegt den privaten Schlüssel in der Serverkonfiguration und den öffentlichen
    Schlüssel in alle Peer-Sektionen der Clientkonfigurationen.
    """


# def check_configuration_integrity(server):
    """
    Prüft die importierten Konfigurationen auf Plausibilität und Vollständigkeit.
    """

    # Prüfung, ob der öffentliche Schlüssel des Servers in allen Clientkonfigurationen korrekt hinterlegt ist.

    # Prüfung, ob IP-Adresskonflikte vorliegen.
