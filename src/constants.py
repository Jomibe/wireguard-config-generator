"""
Enthält vom Programm verwendete statische Veriablen. Die Parameter können auf das eigene System angepasst werden.
"""

# Absoluter Pfad des Konfigurationsverzeichnisses von Wireguard. Standard: /etc/wireguard
WG_DIR = "../res/"

# Dateiname der Serverkonfiguration. Standard: wg0.conf
SERVER_CONFIG_FILENAME = "wg0.conf"

# Quelle: https://docs.sweeting.me/s/wireguard#Overview
# Parameter der Sektion Interface
INTERFACE_CONFIG_PARAMETERS = ("Name", "Address", "ListenPort", "PrivateKey", "DNS", "Table", "MTU", "PreUp", "PostUp",
                               "PreDown", "PostDown")

# Parameter der Sektion Peer
PEER_CONFIG_PARAMETERS = ("AllowedIPs", "Endpoint", "PublicKey", "PersistentKeepalive")

# Alle Konfigurationsparameter
CONFIG_PARAMETERS = INTERFACE_CONFIG_PARAMETERS + PEER_CONFIG_PARAMETERS

# Zusätzliche Ausgaben zum Programmablauf ausgeben
DEBUG = False

# Für den Betrieb notwendige Konfigurationsparameter
MINIMAL_CONFIG_PARAMETERS = ("address", "privatekey")
