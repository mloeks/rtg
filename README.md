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

## Neue Features

### Logging

* einrichten, inkl. Log Rotation
* freier Splunk oder Kibana Account?

### HTTPS

#### DjangoEurope FAQ

* HTTPS-Only kann manuell über die Website-Proxies eingestellt werden
* DjangoEurope stellt per default nur Self-Signed Certificates aus, die faktisch keinen Mehrwert haben
    * Warnung im Browser kommt
    * Selbst ausgestellt, nicht von Certificate Authority

#### Kommerzielles CA-Zertifikat

Kann scheinbar von [Let's Encrypt](https://letsencrypt.org/getting-started/) ausgestellt werden

* 90 Tage gültig (also häufiger erneuern)
* Kann nur im manual mode installiert werden, da DjangoEurope das nicht direkt unterstützt und das `certbot` CLI Tool nicht installiert ist

##### Manual Mode

https://certbot.eff.org/docs/using.html#manual

```text
If your hosting provider doesn’t want to integrate Let’s Encrypt, 
but does support uploading custom certificates, you can install 
Certbot on your own computer and use it in manual mode. 
In manual mode, you upload a specific file to your website to 
prove your control. Certbot will then retrieve a certificate that 
you can upload to your hosting provider. We don’t recommend this 
option because it is time-consuming and you will need to repeat 
it several times per year as your certificate expires. For most 
people it is better to request Let’s Encrypt support from your 
hosting provider, or switch providers if they do not plan to 
implement it.
```