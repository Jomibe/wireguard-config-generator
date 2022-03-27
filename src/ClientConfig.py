"""
Enthält die Klassendefinition von Clientkonfigurationen
"""


class ClientConfig:
    """
    Enthält alle möglichen Parameter der Clientkonfiguration.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """
    
    def __init__(self):
        self.address = ""  # Die Hostadresse im VPN.
        self.endpoint_address = ""  # Die IP-Adresse oder der Hostname des VPN-Servers.
        self.description = ""  # Die Bezeichnung des Clients.
        self.filename = ""  # Der Dateiname inkl. Dateiendung.
        self.listen_port = ""  # Der öffentlich erreichbare Port für die Kommunikation.
        self.private_key = ""  # Der private Schlüssel, base64 kodiert.
        self.public_key = ""  # Der öffentliche Schlüssel, base64 kodiert.
        self.server = ""  # Die Serverkonfiguration.
