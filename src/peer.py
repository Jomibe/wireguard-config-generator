"""
Enthält die Klassendefinition für die Peer-Sektion einer Serverkonfiguration.
"""


class Peer:
    """
    Enthält alle möglichen Parameter der Peer-Sektion.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """

    # Anzahl der Attribute wird durch die Parameterreferenz vorgegeben.
    # pylint: disable=too-many-instance-attributes

    # Eine Klasse ist für diesen Anwendungsfall am besten geeignet.
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.publickey = ""  # Öffentlicher Schlüssel des Clients.
        self.endpoint = ""  # Externe IP-Adresse oder Hostname des Clients aus Sicht des Servers.
        self.persistentkeepalive = ""  # Abstand zwischen zwei vom Server gesendeten Erreichbarkeitssignalen
