.. dabatase tutorials

==================
Database tutorials
==================


.. database info begin

.. note::

    For permanent or long-term storage, a SQL database is used. While many
    implementations exist, we choose to use PostgreSQL for its robustness against
    high activity. SQLite has proven to be a bottleneck in performances for ADE
    Scheduler (in production) but can still be used for development.

.. database info end

.. contents:: Table of content


PostgreSQL setup
================

.. note::
    Before running into the other tutorials, you should go through this one in
    order to setup all you need for database manipulations.
    As ADE Scheduler is hosted on a UNIX system machine, this tutorial will use the
    same commands as UNIX / LINUX system machines. No current support is provided for
    Windows users.


.. database setup begin

I. Install PostgreSQL
---------------------

For this, we highly recommend you to follow this guide:
https://www.postgresqltutorial.com/install-postgresql/

II. Setup a password
--------------------

Even if it is not always required, it is good practice to setup a password for the
:code:`postgres` user:

.. code-block:: console
    :caption: Tutorial from: https://docs.boundlessgeo.com/suite/1.1.1/dataadmin/pgGettingStarted/firstconnect.html

    $ sudo -u postgres psql postgres
    $ \password
    enter your password_psql and confirm
    $ \q

III. Create a database
----------------------

In order to manipulate databases, you need to create a database instance:

.. code-block:: console

    $ sudo su - postgres
    $ createdb ade-database
    $ exit

IV. Setup read without password access
--------------------------------------

By default, ADE Scheduler tries to access the database without password. Here, we need
to explicitly allow the program to access the newly created database without password:

.. code-block:: console
    :caption: You main need to replace *12* with your actual version if it differs

    $ sudo {vim|geany|nano|...} /etc/postgresql/12/main/pg_hba.conf
    and change `peer`/`md5` values to `trust`
    $ sudo systemctl restart postgresql

V. Link database in .flaskenv
-----------------------------

Now, you will need to tell the program where your database is located. To do so, add
this line in your :code:`<repo>/.flaskenv` file:

.. code-block:: console

    $ ADE_DB_PATH="postgresql://postgres@localhost/ade-database"

.. database setup end

1. Recovering data from backup version
======================================

In order to provide robustness to ADE Scheduler's users, a backup of the database is
done once in a while. This tutorial will show you how to use a precedent version of
the database, in order to do some statistic about usage or to recover an old version
of the database in case of problem.


1.1 Reading the database on your local machine
----------------------------------------------

Here, we suppose that you have a copy of backup version of the database.
Such copy can be obtained using :code:`scp` command to transfer a backup version from
the server to your local machine.

.. code-block:: console

    $ gzip -d {db-backup}.sql.gz
    un-zip database
    $ psql -U postgres --host=localhost --dbname=ade-database < {db-backup}.sql
    $ un-dump database
    $ eventually enter you password_psql


2. SQL client
=============

Once the project is setup, you can use the various commands in the shell in order to
interact with the database:

.. code-block:: console

    $ flask db --help
    $ flask sql --help

3. Modify the database structure
================================

.. todo

4. Update or migrate the database
=================================

.. todo

