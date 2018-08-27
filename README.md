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

### Konzept generischer Bets

* ggf. Performance bei Updates (ist langsam geworden...)

### Migration auf generisches RTG-Projekt

* User aus rtg2016-Datenbank in generische DB übertragen (und deaktivieren bis zum ersten Login)

Nur Daten mit INSERTS und Spaltenangaben dumpen:

`pg_dump -a --column-inserts -f rtg2016_auth_user.sql -d muden_rtg2016 -t auth_user`

Primary Keys händisch aus erzeugter SQL-Datei entfernen...

Daten in generische DB einspielen:

`psql -d muden_rtg -f rtg2016_auth_user.sql`

Abhängige Fremdschlüssel-Tabelle korrekt befüllen:

* account_emailaddress
`insert into account_emailaddress (email, verified, "primary", user_id) select email, false, true, id from auth_user;`

Für all diese User müssen noch entsprechende Profile und Statistic Instanzen erstellt werden.
Dafür habe ich ein eigenes management command 'create_profiles' erstellt.

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

# Wunschliste - Fachliche Features

* Zusammenfassung User oben auf Startseite (Avatar, Platz, Punkte etc.)
* Siehe TODOs in diesem und dem Frontend Repo

# Wunschliste - Technische Features

## Logging

Ich möchte Logfiles schreiben, inkl. Log Rotation (z.B. 10 Tage aufbewahren)

### Recherche Auswertung

Gibt es eine freie Auswertemöglichkeit über das reine Lesen der Logfiles selbst hinaus?
Z.B. Splunk, Kibana ... ? 

### Access Log

NGINX access/error logs nehmen

Log Rotation mit eigenem Shell-Script umsetzen.
Gibt `logrotate` auf dem System, aber nicht user-spezifisch editierbar, auch nichts in den FAQ.

### Application Log

**TODO**: jeder Eintrag wird noch 2x geloggt, trotz `propagate: False`.
Debugger: Landet auch 2x im Request Breakpoint ...?

## Browser Tests

Um automatisiert zu testen, ob die RTG "zwischen den Turnieren" lauffähig bleibt, wäre es super, den Happy Path per 
UI Test abdecken zu können.