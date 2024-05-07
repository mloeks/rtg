# Royale Tippgemeinschaft --- Backend

This repository contains the backend code for the "Royale Tippgemeinschaft" API.

It is based on Python and the [Django Web Framework](https://www.djangoproject.com/).

## Current TODOs

### Manual tests

Using old frontend.

#### User Flow

| Test                                | Issues |
|-------------------------------------|--------|
| Register as new user                | OK     |
| Reset password link                 | OK     |
| Set new password through reset link | OK     |
| Change password in settings         | OK     |
| Change user details                 | OK     |
| Change avatar                       | OK     |
| Delete account                      | OK     |
| Refreshing tokens                   | .      |

#### Games Flow

| Test                              | Issues |
|-----------------------------------|--------|
| Show all games, recent games etc. | .      |

#### Bets Flow

| Test                                                       | Issues |
|------------------------------------------------------------|--------|
| Place bet on bets page for open games (incl. invalid bets) | .      |
| Place bet on home page                                     | .      |
| Do not accept bets after deadline has passed               | .      |
| Points should be calculated correctly                      | .      |
| See all bets in game card                                  | .      |

#### Comments Flow

| Test                                                    | Issues                            |
|---------------------------------------------------------|-----------------------------------|
| Add new post on home page incl. draft intermediate save | OK                                |
| Post a comment with replies on home page                | OK                                |
| Use the contact form without being logged in            | 500 response. WSGIRequest is_ajax |

#### Admin Flow

| Test                                                            | Issues |
|-----------------------------------------------------------------|--------|
| Regular users must not be able to access admin pages / sections | .      |
| New post e-mail options                                         | .      |
| Add new game on games page                                      | .      |
| Administrate users (who has paid etc)                           | .      |
| Enter game results                                              | .      |
| (Un-)set maintenance page                                       | .      |
| Access Django's admin page                                      | OK     |

### Further TODOs for launch

* Check console errors on as many pages / flows as possible
* Update static UI assets (dates etc.)
* Data reset: backup PROD DB, remove old posts & tournament data
* Prepare and add new tournament data
* Activate cron jobs / increase frequency for live mode

* Check libraries with major upgrades for breaking changes
* Check some P1/P2 TODOs

## Feature wishlist (quite old)

Some features that would be nice to have if I find the time someday...

### New features visible to the user

* Summary for the user at the top of the home page (Avatar, current rank and points)
* Facebook/Instagram/Twitter Integration
    * Newsfeed could display updates from all social channels?
* See also numerous TODOs in the code of this and the [frontend repository](https://github.com/mloeks/rtg-ui)

### Performance

* bet/game/statistic updates have become rather slow since the project went generic. There is certainly some potential for optimisation.

### Logging

I'd like to introduce a proper logging which for instance allows for easier debugging.

#### Research

Is there any free-to-use log analytics tool like Splunk or Kibana?

#### Access Log

Probably just use access/error logs from Nginx.

Implement log rotation with custom shell script. There is a `logrotate` command on the DjangoEurope server available. However,
it cannot be tailored for my user, nor is there any helpful information in their FAQ about using it.

### Application Log

Started to implement this, but there are some problems present. E.g. each entry is still logged twice, even though `propagate: false` has been set.
Tried to debug this, the debugger also steps twice into the breakpoint. Currently not sure why this happens.

## Setup

### Required packages

(might be incomplete)

`sudo apt install gcc make cmake python3-dev python3-virtualenv postgresql`

### Python 3 Virtualenv

Install Python virtualenv:

`pip install virtualenv`

Create virtualenv `rtg` in `.v` subdirectory:

`mkdir .v; cd .v; virtualenv -p python3 rtg`

Activate virtualenv with

`source .v/rtg/bin/activate`

Then install required packages within `rtg` virtualenv:

`pip install -r requirements/base.txt`

### Database

`sudo -u postgres createuser -P -d mloeks`

`sudo -u postgres createdb -O mloeks rtg`

Run migrations by activating the `rtg` virtualenv and running:

`python manage.py migrate`

Create superuser `mloeks` if it doesn't yet exist:

`python manage.py createsuperuser`

## How To's

### Run the app

#### From the command line

Activate the `rtg` virtualenv, then:

`python manage.py runserver 8000`

#### From within IntelliJ IDE

Create a new Run configuration of type `Django Server`, enter `localhost` and port `8000`.
Use the `rtg` virtualenv as specified interpreter.

Add the `SECRET_KEY_RTG` and `DJANGO_SETTINGS_MODULE=rtg.settings.local` env variables.

### Explore the API

Start the app, then navigate to:

* `localhost:8000/admin` in order to view the DjangoAdmin panel and login with the superuser
* `localhost:8000/rtg` to explore the API using DjangoRestFramework's standard API browser

### Running tests

#### From the command line

Activate the `rtg` virtualenv, then run:

* All tests: `python manage.py test main`
* Unit / Model tests: `python manage.py test main.test.models`
    * Individual unit / model tests e.g.: `python manage.py test main.test.models.test_bet`
* Integration / API tests: `python manage.py test main.test.api`

#### From within IntelliJ IDE

Make sure the entire `main` directory is marked as `Sources` in the Project Settings.

Edit the Django Tests Run Configuration Template such that the `SECRET_KEY_RTG` and `DJANGO_SETTINGS_MODULE`
env variables are properly set.

Then just right-click on the `test` folder or the individual `api` or `models` folder and choose "Run Test: ...".

### Upgrading

#### Dependencies

* Adjust pip requirements files, re-run `pip install -r local.txt` with virtualenv activated, and test.

#### Django

This project is hosted on a [DjangoEurope](https://djangoeurope.com) server.

* After upgrading to a newer Django version via the requirements file, some adjustments on the server might be necessary
    * See [the documentation on updating Django](https://panel.djangoeurope.com/faq/update)
    * See [Django release notes](https://docs.djangoproject.com/en/dev/releases/)
* During major upgrades, it might make sense to have [the wizard in the web admin panel](https://panel.djangoeurope.com/installer/django) install a new project using the corresponding Django version and then compare crucial configuration files and scripts (particularly for the gunicorn app server and nginx).
* While updating, it might be necessary to re-create the database superuser at some point. This can be achieved - [as documented here](https://docs.djangoproject.com/en/2.2/intro/tutorial02/#creating-an-admin-user) - with the command `python manage.py createsuperuser`

## Starting a new tournament

This software cannot cope yet with multiple tournaments. It's always limited to a one and only tournament.
Therefore, there are always some necessary preparations for new tournaments, which are listed here:

* Manual steps to be carried out:
    * Backup PROD database
    * Prepare new tournament data (teams, games etc.) in a new command named "<tournament_abbrev>_create_tournament_data"
    * Commit and push that new command
    * First locally, then on DEMO, then on PROD:
        * Run Django command "clear_tournament_data"
        * Run Django command "<tournament_abbrev>_create_tournament_data"
        * Test
    * Reset "has_paid" flag for all users

## Past migration to a generic RTG project

This software used to consist of an individual repository for each tournament. This was changed in 2018 when it was migrated to 
a (mostly) generic RTG project. Still, as mentioned above, the software itself is not yet as flexible as to provide a generic betting
game solution which can cope with multiple configured tournaments.

Since the migration did take some effort, I documented the steps which were taken. Maybe this is useful for later reconstruction.

### Migration steps taken

All registered users from the old rtg2016 database were manually moved to a new, generic database and deactivated so that they are known to the
2018 software but need to log in once to re-activate:

Dump data with INSERTS and column descriptions:

`pg_dump -a --column-inserts -f rtg2016_auth_user.sql -d muden_rtg2016 -t auth_user`

Then, remove pkeys manually from created SQL file.

Restore data in new, generic database:

`psql -d muden_rtg -f rtg2016_auth_user.sql`

Correctly fill dependent foreign key table `account_emailaddress`:

`INSERT INTO account_emailaddress (email, verified, "primary", user_id) SELECT email, false, true, id FROM auth_user;`

For all these users the corresponding `Profile` and `Statistic` instances had to be created.
I introduced a dedicated management command `create_profiles` for this.
