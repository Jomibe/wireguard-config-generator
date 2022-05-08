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

## Konventionelle Installation, getestet unter Ubuntu 22.04
Als Basis wird eine Standardinstallation von Ubuntu 22.04 vorausgesetzt. Alle Aktualisierungen sollten installiert und das System sollte im Anschluss ggf. neu gestartet worden sein.
`sudo apt update && sudo apt full-upgrade && sudo apt autoremove`
`sudo reboot`

Danach folgt die Installation der Abhängigkeiten auf dem Hostsystem
`sudo apt install pip git wireguard`

Die Inhalte des GitHub Repositories werden mittels `git clone` auf das Zielsystem kopiert.

Im Anschluss werden die Abhängigkeiten der Python-Installation installiert. Dafür muss ggf. zuerst in das gerade erstellte Verzeichnis der Codebasis gewechselt werden. In diesem Verzeichnis befindet sich u.A. die Datei `requirements.txt`
`pip install --no-cache-dir -r requirements.txt`

Es ist notwendig, die Variable `WG_DIR` in der Datei `src/constants.py` auf das aktuelle System anzupassen. Bei einer Standardinstallation, wie hier beschrieben, muss der Wert `"/etc/wireguard/"` lauten.

Nun kann das Programm ausgeführt werden. Dafür muss in das Verzeichnis `src` gewechselt werden, falls nicht bereits geschehen.
`cd src`
`python3 -m main`