# Royale Tippgemeinschaft --- Backend

## Aktuelle TODOs

## Setup

### Benötigte Packages

(kein Anspruch auf Vollständigkeit)

`sudo apt install gcc make cmake python-dev python3-dev`

### Python 3 Virtualenv
`virtualenv -p python3 rtg`

`pip install -r requirements/base.txt`

### Datenbank

`sudo -u postgres createuser -P -d mloeks`

`sudo -u postgres createdb -O mloeks rtg`

## How To's

### Run the app

#### From the command line

Activate the `rtg` virtualenv, then:

`python manage.py runserver 8000`

#### From within IntelliJ IDE

Create a new Run configuration of type `Django Server`, enter `localhost` and port `8000`.
Use the `rtg` virtualenv as specified interpreter.

Add the `SECRET_KEY_RTG` and `DJANGO_SETTINGS_MODULE=rtg.settings.local` env variables.

### Running tests

#### From the command line

Activate the `rtg` virtualenv, then run:

* All tests: `python manage.py test main`
* Unit / Model tests: `python manage.py test main/test/models`
* Integration / API tests: `python manage.py test main/test/api`

#### From within IntelliJ IDE

Make sure the entire `main` directory is marked as `Sources` in the Project Settings.

Edit the Django Tests Run Configuration Template such that the `SECRET_KEY_RTG` and `DJANGO_SETTINGS_MODULE`
env variables are properly set.

Then just right-click on the `test` folder or the individual `api` or `models` folder and choose "Run Test: ...".


### Upgrading

#### Dependencies

* Adjust pip requirements files, re-run `pip install -r local.txt` with virtualenv activated, and test.
* Remember to execute `pip install -r production.txt` on the server after deploying the updated code.

#### Django

* After upgrading to a newer Django version via the requirements file, some adjustments on the server might be necessary
    * See [the documentation on updating Django](https://panel.djangoeurope.com/faq/update)
* During major upgrades, it might make sense to have [the wizard in the web admin panel](https://panel.djangoeurope.com/installer/django) install a new project using the corresponding Django version and then compare crucial configuration files and scripts (particularly for the gunicorn app server and nginx).
* While updating, it might be necessary to re-create the DB superuser at some point. This can be achieved - [as documented here](https://docs.djangoproject.com/en/2.2/intro/tutorial02/#creating-an-admin-user) - with the command `python manage.py createsuperuser`

## Dokumentation: Migration auf generisches RTG-Projekt

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

# Wunschliste - Fachliche Features

* Zusammenfassung User oben auf Startseite (Avatar, Platz, Punkte etc.)
* Siehe TODOs in diesem und dem Frontend Repo

# Wunschliste - Technische Features

## Performance

* ggf. Performance bei Updates (ist seit "generischen" Bets langsam geworden...)

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
