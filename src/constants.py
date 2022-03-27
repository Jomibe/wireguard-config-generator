"""
Enthält vom Programm verwendete statische Veriablen. Die Parameter können auf das eigene System angepasst werden.
"""

# Absoluter Pfad des Konfigurationsverzeichnisses von Wireguard. Standard: /etc/wireguard
WG_DIR = "../res/"

# Dateiname der Serverkonfiguration. Standard: wg0.conf
SERVER_CONFIG_FILENAME = "wg0.conf"

# Quelle: https://docs.sweeting.me/s/wireguard#Overview
CONFIG_PARAMETERS = ("Name", "Address", "ListenPort", "PrivateKey", "DNS", "Table", "MTU", "PreUp", "PostUp", "PreDown",
                     "PostDown", "AllowedIPs", "Endpoint", "PublicKey", "PersistentKeepalive")
