[![Build Status](https://travis-ci.org/open-contracting/opendatacomparison.svg?branch=master)](https://travis-ci.org/open-contracting/opendatacomparison)
[![Coverage Status](https://coveralls.io/repos/open-contracting/opendatacomparison/badge.png)](https://coveralls.io/r/open-contracting/opendatacomparison)

A Django application for comparing datsets, built on Open Comparison

Requirements
============
You will need:
* git
* pip
* MySQL

Installation on Ubuntu 14.04. 

    $ sudo apt-get install git python-pip python-dev mysql-server libmysqlclient-dev 
    $ sudo pip install virtualenv

Installation on OSX 10.8 with homebrew:

    $ brew install git python mysql
    $ pip install virtualenv


Install
=======
This has been tested on Ubuntu 14.04 & OSX 10.8.

The whole application runs inside a virtualenv, but you do not have to manage
it yourself, the [dye](https://github.com/aptivate/dye) commands handle this for you.

After cloning the repo, go to the deploy directory:

    $ cd opendatacomparison/deploy

The bootstrap.py command sets up a virtualenv for us:

    $ ./bootstrap.py

We use the deploy command to do the following:
* sets up our sql database for the first time including creating a new username and password (this is why deploy wants your mysql root password)
* links to the correct local settings files
* does other deploy things (which are generally more relevant when deploying to server - building webassets etc.


To deploy (note it will ask you for your MySQL root password twice):

    $ ./tasks.py deploy:dev

Run locally
===========
Go into the django directory and use manage.py to run django:

    $ ./manage.py runserver

./manage.py automatically runs inside the virtualenv that was setup
by bootstrap.py

Run tests
=========
To run the tests use:

    $ ./manage.py test


Adding new requirements
=======================
To add new pip packages to validator, add them to deploy/pip_packages.txt.
After doing this, run bootstrap.py again to update your virtualenv.


Deploy
======
Dye provides a wrapper around fabric for deployment. Basic deploy from root directory:

    $ cd deploy
    $ ./fab.py production deploy

If you need to specify a different user to log in to the server:

    $ ./fab.py production deploy -u username
