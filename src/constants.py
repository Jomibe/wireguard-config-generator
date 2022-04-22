"""
Enthält vom Programm verwendete statische Veriablen. Die Parameter können auf das eigene System angepasst werden.
"""

# Pfad des Konfigurationsverzeichnisses von Wireguard. Muss mit einem / enden. Standard: /etc/wireguard
WG_DIR = "../res/"

# Dateiname der Serverkonfiguration. Standard: wg0.conf
SERVER_CONFIG_FILENAME = "wg0.conf"

# Quelle: https://docs.sweeting.me/s/wireguard#Overview
# Parameter der Sektion Interface
INTERFACE_CONFIG_PARAMETERS = ("Address", "ListenPort", "PrivateKey", "DNS", "Table", "MTU", "PreUp", "PostUp",
                               "PreDown", "PostDown")

# Parameter der Sektion Peer
PEER_CONFIG_PARAMETERS = ("AllowedIPs", "Endpoint", "PublicKey", "PersistentKeepalive")

# Alle Konfigurationsparameter
CONFIG_PARAMETERS = INTERFACE_CONFIG_PARAMETERS + PEER_CONFIG_PARAMETERS

# Zusätzliche Ausgaben zum Programmablauf ausgeben
DEBUG = False

# Für den Betrieb notwendige Konfigurationsparameter. Hinterlegt in kleinbuchstaben.
MINIMAL_CONFIG_PARAMETERS = ("address", "privatekey")

# Regulärer Ausdruck für die Erkennung eines einzelnen Parameters. Es dürfen Leerzeichen vor und hinter dem Parameter
# stehen. Die erste Gruppe enthält den Parameter ohne äußere Leerzeichen.
RE_MATCH_KEY = r"^ *([a-zA-Z]*) *"

# Regulärer Ausdruck für die Erkennung eines Name-Wert Paares. Es dürfen Leerzeichen zwischen Name, dem
# Zuweisungsoperator = und dem Wert stehen. Die erste Gruppe beinhaltet den Parameternamen ohne Leerzeichen. Die
# zweite Gruppe beinhaltet den Wert ohne führende Leerzeichen.
RE_MATCH_KEY_VALUE = r"^([^ ]*) *= *(.*)"

# Relativer Ordnerpfad zu WG_DIR für die Datensicherung. Muss mit einem / enden.
SAVEDIR = ".wg_conf_bak/"

# Relativer Ordnerpfad zu WG_DIR für die Datensicherung. Wird nach erfolgreicher Erstellung in SAVEDIR umbenannt,
# um Datenverlust bei einem Fehler im Export vorzubeugen. Muss mit einem / enden.
SAVEDIR_NEW = ".wg_conf_bak_new/"

# Datensicherung beim Export deaktivieren
DISABLE_BACKUP = False
