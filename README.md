# Royale Tippgemeinschaft --- Backend

## Setup

### Python 3 Virtualenv
`virtualenv -p python3 rtg`

`pip install -r requirements/base.txt`

## Erkenntnisse aus der Migration von Django 1.8 auf 1.11

* v.a. package foo und Verzeichnisstruktur haben Probleme gemacht
* DB ging einfacher als gedacht
* DB Superuser im Nachhinein erstellen: `python manage.py createsuperuser`
                                        https://docs.djangoproject.com/en/1.11/intro/tutorial02/#creating-an-admin-user
* einige breaking changes in Django, REST Framework & Co., ggf. Changelogs genauer anschauen (wobei der Konsolen-Output auch meistens hilfreich ist)
* Python sys.path und Auflösung von Packages verstehen!! 

## Aktuelle TODOs

### Tests

* noch 32 rote API Tests fixen

### Migration auf generisches RTG-Projekt

* Bislang alles naiv umbenannt, jegliche Funktionaliät (v.a. rund ums Deployment muss überprüft werden)