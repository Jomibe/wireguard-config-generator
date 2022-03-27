"""
Enthält die Klassendefinition von Serverkonfigurationen.
"""

# Interne Imports
from constants import SERVER_CONFIG_FILENAME
from constants import WG_DIR


class ServerConfig:
    """
    Enthält alle möglichen Parameter der Serverkonfiguration.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """

    def __init__(self):
        self.address = ""  # Die Hostadresse im VPN.
        self.clients = []  # Liste der Client-Konfigurationen, gespeichert in einem dict.
        self.filename = WG_DIR + SERVER_CONFIG_FILENAME  # Der Dateiname inkl. Dateiendung.
        self.listen_port = ""  # Der öffentlich erreichbare Port für die Kommunikation.
        self.private_key = ""  # Der private Schlüssel, base64 kodiert.
        self.public_key = ""  # Der öffentliche Schlüssel, base64 kodiert.
