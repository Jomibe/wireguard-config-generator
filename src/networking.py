"""
Diese Datei enthält Funktionen, welche zur Berechnung von IPv4-Netzwerken ("subnetting") notwendig sind.
"""

# Es gibt ein Problem mit der Erkennung von lokalen Modulen durch pylint. Daher:
# pylint: disable=import-error

# Imports aus Standardbibliotheken

# Imports von Drittanbietern

# Eigene Imports
from debugging import console


def get_cidr_mask_from_hosts(number_of_hosts):
    """
    Diese Funktion berechnet, welche IPv4-Netzwerkmaske notwendig ist, um eine gegebene Anzahl von Hosts zu verwalten.
    Im Anschluss wird die benötigt CIDR-Maske zurückgegeben.
    """

    # Das größte private Netzwerk ist 10.0.0.0/8. Dort sind 24 von 32 Bit für den Host vorgesehen.
    for cidr_suffix in range(24):
        # Wenn die maximale Netzwerkgröße die Menge der angegebenen Hosts übersteigt, wird diese zurückgegeben.
        if 2**cidr_suffix-2 > number_of_hosts:
            return 32-cidr_suffix

    # else/ elif number_of_hosts > 2**24-2:
    console("Es ist nicht möglich, mehr als 2^24-2 Clients in einem privaten IPv4-Subnetz unterzubringen. Bitte eine "
            "kleinere Menge angeben.", mode="err")
    return None
