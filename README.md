# Royale Tippgemeinschaft --- Backend

## Setup

### Python 3 Virtualenv
`virtualenv -p python3 rtg`

`pip install -r requirements/base.txt`

## Aktuelle TODOs

### Migration auf Python 3 & Django 1.11 (was: 1.8)

* ANSCHLUSS: Server fährt hoch, findet aber noch gar keine URLs
    * vermutlich verkonfiguriert, da ich überall das rtg. Prefix raus genommen habe
    * urls.py hat sich auch etwas geändert in neuerer Django-Version
    * api.html vom REST framework wird nicht gefunden?

#### Datenbank

* Migration lief auf Anhieb durch
* gibt aber noch keinen Admin-User --> im Nachhinein erstellen?

#### Tests

* Haben noch Import-Probleme (rtg.rtg)

### Migration auf generisches RTG-Projekt

* Bislang alles naiv umbenannt, jegliche Funktionaliät (v.a. rund ums Deployment muss überprüft werden)