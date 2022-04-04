"""
Enthält die Klassendefinition von Serverkonfigurationen.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Interne Imports
from constants import SERVER_CONFIG_FILENAME
from constants import WG_DIR


class ServerConfig:
    """
    Enthält alle möglichen Parameter der Serverkonfiguration.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """

    # Anzahl der Attribute wird durch die Parameterreferenz vorgegeben. Daher:
    # pylint: disable=too-many-instance-attributes

    # Eine Klasse ist für diesen Anwendungsfall am besten geeignet. Daher:
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.name = ""  # Die Bezeichnung des Servers ("friendly name").
        self.filename = WG_DIR + SERVER_CONFIG_FILENAME  # Der Dateiname inkl. Dateiendung.
        self.address = ""  # Die Hostadresse im VPN.
        self.listenport = ""  # Der Port auf welchem gelauscht wird.
        self.privatekey = ""  # Der private Schlüssel, base64 kodiert.
        self.dns = ""  # Zu verwendende DNS-Server.
        self.table = ""  # Zu verwendende Routingtabellen.
        self.mtu = ""  # Angepasste maximale Übertragungseinheit.
        self.preup = ""  # Auszuführende Programme vor dem Verbindungsaufbau
        self.postup = ""  # Auszuführende Programme nach dem Verbindungsaufbau
        self.predown = ""  # Auszuführende Programme vor dem Verbindungsabbau
        self.postdown = ""  # Auszuführende Programme nach dem Verbindungsabbau
        self.clients = []  # Liste der verwandten Client-Konfigurationen.
