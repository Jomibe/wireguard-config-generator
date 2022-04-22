# Entwicklung eines Konfigurationsgenerators für WireGuard VPN

## Skizze
Es wird die Entwicklung einer Python-Applikation geplant und durchgeführt. Die Applikation nimmt dem Benutzer den Aufwand ab, das Erzeugen der Schlüsselpaare sowie der Netzwerkeinstellungen für WireGuard-VPN Konfigurationen selbst vornehmen zu müssen. Außerdem können bestehende Konfigurationen eingelesen und ergänzt werden.

## Hintergrund
VPN Netzwerke werden heutzutage an vielen Stellen in der Informationstechnik verwendet: Mitarbeiter greifen über Tunnelverbindungen gesichert auf Firmennetzwerke zu; Privatleute verwenden die Technik gerne, um die Herkunft gegenüber den Anbietern im Internet aus Datenschutzgründen zu verschleiern und viele aus dem Internet erreichbare Systeme lassen dessen Konfiguration nur noch über ein VPN-Netzwerk zu, welches sicherstellt, dass die grundlegenden Schutzziele der IT-Sicherheit wie Authentizität und Vertraulichkeit dabei sichergestellt werden können. In den letzen Jahren haben sich einige Lösungen etabliert: OpenVPN und IPsec zum Beispiel. WireGuard ist eine relativ junge Softwarelösung, welche 2020 in den Linux Kernel integriert wurde und gegenüber den erwähnten Produkten Geschwindigkeitsvorteile liefert, sowohl beim Betrieb als auch bei der Konfiguration. Die Verbindungen sind UDP-basiert und der für den Betrieb notwendige Code beschränkt sich auf etwa 1% der Implementierung von OpenVPN, darüber hinaus wird im Gegensatz zu den erwähnten Produkten eine statische Auswahl von Sicherheitsalgorithmen verwendet, was das Aushandeln der Verbindungseigenschaften (eine bisweilen sehr zeitintensive Aufgabe beim initialen Herstellen einer IPsec-VPN Verbindung) vollständig eliminiert.

## Beschreibung
Die Applikation soll den Anwender bei der Verwaltung der auf dem System vorhandenen Konfigurationsdateien unterstützen. Grundsätzlich stehen für alle bekannten Betriebssysteme auf PCs, Firewalls und Mobilgeräten Implementierungen von WireGuard zur Verfügung. Die Administration (mittels Erstellung und Bearbeitung von Textdateien) und der Betrieb findet allerdings häufig auf Linux- und BSD-basierten Betriebssystemen statt. Da bei diesen unixoiden Systemen die Verwaltung jeweils ähnlich verläuft, soll sich die Kompatibilität der Anwendung auf unixoide Betriebssysteme (außer macOS) beschränken.

Die Software ist in der Lage, sowohl "auf einer grünen Wiese" zu starten als auch bestehende Gesamtkonfigurationen (für Server und Clients) einzulesen und zu ergänzen. Die VPN-Konfiguration findet im Verzeichnis `/etc/wireguard` statt. Auf dem Server befinden sich dort die Datei `wg0.conf`, welche Parameter der Schnittstelle enthält (u.A. privater Schlüssel und Port, auf welchem Verbindungsanfragen entgegengenommen werden) sowie die Konfigurationsdateien der Clients (diese sind für den Betrieb des Servers nicht notwendig, sorgen aber für eine bessere Übersicht über die erstellten Konfigurationen für die Clients). Die Konfigurationsdateien beinhalten die Verbindungsparameter im Klartext in einer einfachen INI-Syntax `[Sektion] Parameter = Wert`. Pro Verbindung muss ein neues Schlüsselpaar, bestehend aus privatem und öffentlichem Schlüssel generiert werden und base64-kodiert in der Konfigurationsdatei hinterlegt werden. Da kein DHCP-Server verwendet wird, erfolgt die IP-Adressvergabe statisch ebenfalls in den Konfigurationsdateien. Hierbei muss ggf. die zur Netzwerkgröße passende Maske berechnet werden. Es sollte dabei offensichtlich zu keinen IP-Adresskonflikten kommen, daher sollte eine IP-Adresse nur jeweils einem Gerät zugeordnet werden.

Um die Übermittlung der Daten auf Mobilgeräte zu vereinfachen, soll eine Funktion für die Generierung eines QR-Codes implementiert werden. Dieser kann mit der WireGuard-App für Android und iOS eingelesen werden und ermöglicht den sofortigen Verbindungsaufbau nach Bestätigung der Informationen auf dem Endgerät.

Die Software wird über die Konsole bedient. Die bestehenden Dateien werden eingelesen und es wird beim Start der Applikation eine Übersicht erstellt. Dabei werden alle in der Referenz (vgl. https://github.com/pirate/wireguard-docs#Config-Reference) erwähnten Parameternamen ausgewertet. Der Anwender kann die Konfiguration verwerfen und neu beginnen oder weitere Clientverbindungen hinzufügen. Im Falle einer kompromittierten Konfiguration soll es die Möglichkeit geben, das Schlüsselpaar des Servers neu zu generieren und in allen Client-Konfigurationen zu hinterlegen. Weiterhin soll eine Aktualisierung der Netzwerkgröße möglich sein, dazu müssen die Angaben zur IP-Adresse und Netzwerkmaske in den Dateien angepasst werden. Nach erfolgreicher Bearbeitung der Konfigurationen sollen diese in einer einheitlichen Formatierung im oben genannten Verzeichnis hinterlegt werden. Eine durchschnittliche Clientkonfiguration enthält etwa 10 Zeilen. Die Serverkonfiguration besteht aus etwa fünf Zeilen, pro Client werden dabei mindestens drei Zeilen hinzugefügt.

### Beispiel Serverkonfigurationsdatei:
```
# Serverkonfiguration

[Interface]
Address = 10.10.10.1/24
ListenPort = 12345
PrivateKey = cHZQta30/Z4Zijb/nCeYxkkR/u8ep1vwGuy5xYT2708=

[Peer]
# Name = Mein iPhone
AllowedIPs = 10.10.10.2/32
PublicKey = Ew8gAiOdwOIoltpCwDYrLFzMJb/Jl3oB7GO1k4JqgzY=
```

### Beispiel Clientkonfigurationsdatei:
```
[Interface]
# Name = Mein iPhone
Address = 10.10.10.2/32
PrivateKey = kC/Wd4Ws65DX4FXCsZBkHdNAbKVpe86JJbIA2LK0slY=

[Peer]
AllowedIPs = 10.10.10.1
Endpoint = mein-vpn-server:12345
PublicKey = 0dAwIB3Ji96GYdlesA+iCNxhB7NElkFf7DZ4GWyaEFI=
```
