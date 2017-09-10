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

### TODOs

* checken, was davon wirklich wichtig ist und gemacht werden sollte

### Migration auf generisches RTG-Projekt

* User aus rtg2016-Datenbank in generische DB übertragen (und deaktivieren bis zum ersten Login)

# Neue Features 2018

## HTTPS

Damit der Browser die Seite als "Sicher" anzeigt und nicht nach der Ausnahme fragt, muss dass Zertifikat
ein kommerzielles sein - Self-Signed reicht nicht.

### Let's Encrypt

DjangoEurope hat eine neue Option, das einfach per Mausklick zu tun im "SSL"-Bereich.
Die "Let's Encrypt" Option muss angehakt sein. Auch Subdomains können eingetragen werden
(SSL-Zertifikate müssen für jede Subdomain ausgestellt werden, oder als Wildcard-Zertifikat).

### Erneuerung

Die Let's Encrypt Zertifikate sind nur 90 Tage gültig und müssen entsprechend häufig
erneuert werden. Scheinbar macht dies DjangoEurope automatisch? Am 09.12.17 checken...

## Logging

Ich möchte Logfiles schreiben, inkl. Log Rotation (z.B. 10 Tage aufbewahren)

### Recherche Auswertung

Gibt es eine freie Auswertemöglichkeit über das reine Lesen der Logfiles selbst hinaus?
Z.B. Splunk, Kibana ... ? 

### Access Log

* NGINX access log nehmen?
* Log Rotation:
    * https://serverfault.com/questions/209177/nginx-logrotate-config

### Technical Log