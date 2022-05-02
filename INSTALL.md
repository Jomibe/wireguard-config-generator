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

## Konventionell/ nativ
folgt in Kürze
