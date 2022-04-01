"""
Enthält die Klassendefinition für die Peer-Sektion einer Serverkonfiguration.
"""


class Peer:
    """
    Enthält alle möglichen Parameter der Peer-Sektion.
    (vgl. https://github.com/pirate/wireguard-docs#config-reference)
    """

    def __init__(self):
        self.publickey = ""  # Öffentlicher Schlüssel des Clients.
        self.endpoint = ""  # Externe IP-Adresse oder Hostname des Clients aus Sicht des Servers.
        self.persistentkeepalive = ""  # Abstand zwischen zwei vom Server gesendeten Erreichbarkeitssignalen
