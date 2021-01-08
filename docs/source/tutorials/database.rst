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


I. Lite setup
-------------

.. note::
    If it is your first time working on this project, we highly recommend you to follow
    this setup. The complete setup is only required for maintainers working with the
    database hosted on the ADE Scheduler server.

I-a. Install SQLite3
********************

You will need to install SQLite3 to perform operation on your database.
To do so, refer to instructions related to your machine. For ubuntu:

.. code-block:: console

    $ sudo apt-get install sqlite3

I-b. Create a database
**********************

You will need to create an empty database, wherever you want, on your machine.
Just create an empty file name :code:`ade-database.db`.

Please, remember the location of the database, as you will need it for later in the
tutorial. Now, you can directly jump to section *III*.

II. Complete setup
------------------

II-a. Install PostgreSQL
************************

For this, we highly recommend you to follow this guide:
https://www.postgresqltutorial.com/install-postgresql/

II-b. Setup a password
**********************

Even if it is not always required, it is good practice to setup a password for the
:code:`postgres` user:

.. code-block:: console
    :caption: Tutorial from: https://docs.boundlessgeo.com/suite/1.1.1/dataadmin/pgGettingStarted/firstconnect.html

    $ sudo -u postgres psql postgres
    $ \password
    enter your password_psql and confirm
    $ \q

II-c. Create a database
***********************

In order to manipulate databases, you need to create a database instance:

.. code-block:: console

    $ sudo su - postgres
    $ createdb ade-database
    $ exit

II-d. Setup read without password access
****************************************

By default, ADE Scheduler tries to access the database without password. Here, we need
to explicitly allow the program to access the newly created database without password:

.. code-block:: console
    :caption: You main need to replace *12* with your actual version if it differs

    $ sudo {vim|geany|nano|...} /etc/postgresql/12/main/pg_hba.conf
    and change `peer`/`md5` values to `trust`
    $ sudo systemctl restart postgresql


III. Link database in .flaskenv
-------------------------------

Now, you will need to tell the program where your database is located. To do so, add
this line in your :code:`<repo>/.flaskenv` file:

.. code-block:: console

    $ ADE_DB_PATH="sqlite:///<path/to>/ade_database.db"
    for SQLite3 (warning, <path/to> may be "/home/..." so it will add 1 more "/")
    $ ADE_DB_PATH="postgresql://postgres@localhost/ade-database"
    for PostgreSQL
    or, alternatively, you can use an other database you have
    $ ADE_DB_PATH=<database URI>

IV. Populate the database
-------------------------

If your database is empty, you need to populate it with the correct tables and columns.
This can be done using the client:

.. code-block:: console

    $ flask sql init

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

    drop old database
    $ psql -c 'drop database "ade-database";' -U postgres --host=localhost
    create new database
    $ psql -c 'create database "ade-database";' -U postgres --host=localhost
    $ gzip -d {db-backup}.sql.gz
    un-zip database
    $ psql -U postgres --host=localhost --dbname=ade-database < {db-backup}.sql
    un-dump database
    eventually enter you password_psql


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
