# Installation und Ausführung

## Einleitung
Hier wird beschrieben, wie das Programm ausgeführt werden kann. Es ist nur der Betrieb unter unixoiden Systemen vorgesehen. Mithilfe eines Docker-Containers ist die Ausführung auf anderen Betriebssystemen aber auch möglich.

## Docker
Zuerst werden die Inhalte des Repository mittels `git clone` auf das Zielsystem kopiert.

Im Anschluss wird das Docker Image gebaut:
`docker build -t wg-config-mgmt ./`

Nun kann das Image in einem Container ausgeführt werden:
`docker run -it --rm wg-config-mgmt`

Vorhandene Verzeichnisse müssen im Container eingebunden werden, um die Konfigurationen bearbeiten zu können:
`docker run -it --rm -v /etc/wireguard:/res wg-config-mgmt`

Nach Konfigurationsänderungen muss der Container mit `docker restart` neu gestartet werden.

## Konventionelle Installation, getestet unter Ubuntu 22.04
Als Basis wird eine Standardinstallation von Ubuntu 22.04 vorausgesetzt. Alle Aktualisierungen sollten installiert und das System sollte im Anschluss ggf. neu gestartet worden sein.
`sudo apt update && sudo apt full-upgrade && sudo apt autoremove`
`sudo reboot`

Danach folgt die Installation der Abhängigkeiten auf dem Hostsystem
`sudo apt install pip git wireguard python3.10-venv`

Die Inhalte des GitHub Repositories werden mittels `git clone` auf das Zielsystem kopiert.

Da die Software aufgrund der Berechtigungen des Verzeichnisses `/etc/wireguard` als Benutzer mit erhöhten Berechtigungen `root` ausgeführt werden muss, wird aus Sicherheitsgründen eine virtuelle Python Umgebung mit `python3 -m venv wireguard-mgmt-env` erstellt und mit `source wireguard-mgmt-env/bin/activate` verwendet. Nun ist eine sichere Verwendung als Superuser möglich.

Im Anschluss werden die Abhängigkeiten der Python-Installation installiert. Dafür muss ggf. zuerst in das gerade erstellte Verzeichnis der Codebasis gewechselt werden. In diesem Verzeichnis befindet sich u.A. die Datei `requirements.txt`
`sudo pip install --no-cache-dir -r requirements.txt`

Es ist notwendig, die Variable `WG_DIR` in der Datei `src/constants.py` auf das aktuelle System anzupassen. Bei einer Standardinstallation, wie hier beschrieben, muss der Wert `"/etc/wireguard/"` lauten.

Nun kann das Programm ausgeführt werden. Dafür muss in das Verzeichnis `src` gewechselt werden, falls nicht bereits geschehen.
`cd src`
`sudo python3 -m main`

Der Aufruf von `python3` erfolgt mit `sudo` aufgrund der Berechtigungen des Konfigurationsverzeichnisses `/etc/wireguard`, wie oben bereits erwähnt.

Sobald eine Konfiguration auf das Dateisystem geschrieben wurde, kann der Dienst erstmalig mit `sudo systemctl enable --now wg-quick@wg0` aktiviert werden. Nach Konfigurationsänderungen ist ein Neustart des Dienstes notwendig: `sudo systemctl restart wg-quick@wg0`
