"""
Name: WireGuard Cryptography Class
Creator: K4YT3X
Date Created: October 11, 2019
Last Modified: January 26, 2021

The WireGuard class implements some of wireguard-tools' cryptographic
    functions such as generating WireGuard private and public keys.
"""

# Imports aus Standardbibliotheken
import base64

# Imports von Drittanbietern
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


class WireGuard:
    """WireGuard Cryptography Class

    generates WireGuard public key, private key, and PSK
    """

    @staticmethod
    def genkey() -> str:
        """generate WireGuard private key

        Returns:
            str: X25519 private key encoded in base64 format
        """
        return base64.b64encode(
            X25519PrivateKey.generate().private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
        ).decode()

    @staticmethod
    def pubkey(privkey: str) -> str:
        """convert WireGuard private key into public key

        Args:
            privkey (str): WireGuard X25519 private key
                encoded in base64 format

        Returns:
            str: corresponding public key of the provided
                private key encoded as a base64 string
        """
        return base64.b64encode(
            X25519PrivateKey.from_private_bytes(base64.b64decode(privkey.encode()))
            .public_key()
            .public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        ).decode()
