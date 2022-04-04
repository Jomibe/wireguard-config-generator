"""
Enthält die Klassendefinition von Clientkonfigurationen
"""


class ClientConfig:
    """
    Enthält alle möglichen Parameter der Clientkonfiguration.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """

    # Anzahl der Attribute wird durch die Parameterreferenz vorgegeben.
    # pylint: disable=too-many-instance-attributes

    # Eine Klasse ist für diesen Anwendungsfall am besten geeignet.
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.name = ""  # Die Bezeichnung des Clients ("friendly name").
        self.filename = ""  # Der Dateiname inkl. Dateiendung.
        self.address = ""  # Die Hostadresse des Clients im VPN.
        self.listenport = ""  # Der Port auf welchem clientseitig gelauscht wird.
        self.privatekey = ""  # Der private Schlüssel des Clients, base64 kodiert.
        self.dns = ""  # Verwendete DNS-Server.
        self.table = ""  # Verwendete Routing-Tabellen.
        self.mtu = ""  # Angepasste maximale Übertragungseinheit.
        self.preup = ""  # Auszuführende Programme vor dem Verbindungsaufbau
        self.postup = ""  # Auszuführende Programme nach dem Verbindungsaufbau
        self.predown = ""  # Auszuführende Programme vor dem Verbindungsabbau
        self.postdown = ""  # Auszuführende Programme nach dem Verbindungsabbau
        self.allowedips = ""  # Zugelassene IP-Adressen des Verbindungspartners.
        self.endpoint = ""  # Die IP-Adresse oder der Hostname des VPN-Servers.
        self.publickey = ""  # Der öffentliche Schlüssel des Servers, base64 kodiert.
        self.persistentkeepalive = ""  # Abstand zwischen zwei Erreichbarkeitssignalen.
        self.client_publickey = ""  # Öffentlicher Schlüssel des Clients.
        self.client_endpoint = ""  # Externe IP-Adresse oder Hostname des Clients aus Sicht des Servers.
        self.client_persistentkeepalive = ""  # Abstand zwischen zwei vom Server gesendeten Erreichbarkeitssignalen
