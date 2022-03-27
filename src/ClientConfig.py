"""
Enthält die Klassendefinition von Clientkonfigurationen
"""


class ClientConfig:
    """
    Enthält alle möglichen Parameter der Clientkonfiguration.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """
    
    def __init__(self):
        self.name = ""  # Die Bezeichnung des Clients ("friendly name").
        self.filename = ""  # Der Dateiname inkl. Dateiendung.
        self.server = ""  # Die verwandte Serverkonfiguration.
        self.address = ""  # Die Hostadresse im VPN.
        self.listenport = ""  # Der Port auf welchem gelauscht wird.
        self.privatekey = ""  # Der private Schlüssel, base64 kodiert.
        self.dns = ""  # Verwendete DNS-Server.
        self.table = ""  # Verwendete Routing-Tabellen.
        self.mtu = ""  # Angepasste maximale Übertragungseinheit.
        self.preup = ""  # Auszuführende Programme vor dem Verbindungsaufbau
        self.postup = ""  # Auszuführende Programme nach dem Verbindungsaufbau
        self.predown = ""  # Auszuführende Programme vor dem Verbindungsabbau
        self.postdown = ""  # Auszuführende Programme nach dem Verbindungsabbau
        self.allowedips = ""  # Zugelassene IP-Adressen des Verbindungspartners.
        self.endpoint = ""  # Die IP-Adresse oder der Hostname des VPN-Servers.
        self.public_key = ""  # Der öffentliche Schlüssel, base64 kodiert.
        self.persistentkeepalive = ""  # Abstand zwischen zwei Erreichbarkeitssignalen.
        self.client_publickey = ""  # Öffentlicher Schlüssel des Clients.
        self.client_endpoint = ""  # Externe IP-Adresse oder Hostname des Clients aus Sicht des Servers.
        self.client_persistentkeepalive = ""  # Abstand zwischen zwei vom Server gesendeten Erreichbarkeitssignalen
