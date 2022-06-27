.. ade-schedule tutorials

=======================
ADE Scheduler tutorials
=======================

.. ade-scheduler info begin

.. note::

    This section will describe every tools that is brought with the ADE Scheduler
    repository. While many tools can be installed separately, the Github of this
    project contains many tools and things to setup that can be done in a few clicks.

.. ade-scheduler info end

.. contents:: Table of content


ADE Scheduler setup
===================

.. note::
    Before running into the other tutorials, you should go through this one in
    order to setup all you need for the project.
    As ADE Scheduler is hosted on a UNIX system machine, this tutorial will use the
    same commands as UNIX / LINUX system machines. No current support is provided for
    Windows users.

.. ade-scheduler setup begin

New to Github ?
---------------

If you are new to Github, please consider reading this tutorial first:
https://guides.github.com/activities/hello-world/

I. Clone the repository
-----------------------

If you are not one of the official maintainers of this project, you should first fork
this repository: https://github.com/ADE-Scheduler/ADE-Scheduler/fork

Then, clone the forked repository somewhere on your machine. We will always refer to
the location of the project directory as :code:`<repo>`.

II. Install NodeJS and NPM
--------------------------

First, you need NodeJS and NPM (Node Package Manager). It can be downloaded on the
official site:  https://nodejs.org/en/

Once it is installed, go to the :code:`<repo>` directory and run:

.. code-block:: console

    $ npm install

This will install all the Javascript packages we use in the project.

Any javascript or HTML asset needs to be bundled by webpack before being used.
To do so, run in :code:`<repo>`:

.. code-block:: console

    $ npx webpack

Moreover, you can activate the file watcher for hot-reloading and map source files
for easy debugging by running:

.. code-block:: console

    $  npx webpack --watch --devtool inline-source-map

If an error appears about the maximum amount of allowed watchers,
you can fix this by running:

.. code-block:: console
    :caption: from https://stackoverflow.com/questions/53930305/nodemon-error-system-limit-for-number-of-file-watchers-reached

    $ echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf \
    && sudo sysctl -p

III. Install Python
-------------------

The project can work with a variety of Python versions, but we recommend Python 3.9.X as this is the version that is currently used in production.
It can be downloaded from the official site: https://www.python.org/

**Before installing Python packages**:
Some external packages require external dependencies, and missing them will cause errors during the installation process.
Here are a few:
- OpenSSL: https://www.poftut.com/install-use-openssl-library-python-applications/
- OpenLDAP: https://stackoverflow.com/questions/4768446/i-cant-install-python-ldap

IV. Create a virtual environment
--------------------------------

Event though this step is not mandatory, it is good practice and highly recommended
to create a Python virtual environment. This can be done in a few lines:

.. code-block:: console

    $ cd <repo>
    $ sudo apt install python3-virtualenv
    or equivalent command if you are not on ubuntu
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r prod-requirement.txt # For production  (if you do not plan on modifying code)
    $ pip install -r dev-requirements.txt # For development (else)

.. warning::

    Whenever you want to run the project, you need to be in this virtual environment.
    You will then need to activate the environment each time you come back to work.
    Some IDEs such as PyCharm provide tools to automatically activate virtual
    environments.

V. Initialize the environment file
----------------------------------

In this project, we use many configuration files. One of these files will carry
sensible information such as password and it is your duty to create this file and to
keep it secret.

Create a file named :code:`.flaskenv` in the :code:`<repo>` directory and fill the
following lines in:

.. code-block:: bash
    :caption: :code:`<repo>/.flaskenv` content for development

    FLASK_APP = path/to/<repo>/app.py
    FLASK_ENV = development
    FLASK_RUN_HOST = localhost
    FLASK_RUN_PORT = 5000
    TEMPLATES_AUTO_RELOAD = True

    FLASK_SECRET_KEY = <super_secret_key>
    FLASK_SALT = <super_complex_salt>

.. code-block:: bash
    :caption: :code:`<repo>/.flaskenv` content for production

    FLASK_APP = path/to/<repo>/app.py
    FLASK_ENV = production

    FLASK_SECRET_KEY = <super_secret_key>
    FLASK_SALT = <super_complex_salt>

Lines will be added to this file in other tutorials.

.. ade-scheduler setup end


1. Flask client
===============

This project comes with a variety of command line tools. You can list all the
available commands with:

.. code-block:: console

    $ flask --help

2. Flask shell
==============

Among all the command line tools, there is the Flask shell. This interactive shell
enters a Python interactive shell with all the context of the ADE Scheduler application.
It is a great tool for debugging purposes!

.. code-block:: console

    $ flask shell


3. Adding new Python package
============================

Whenever you add a package to your Python environment that is required for the project, you will need to add it to the list of requirements so that other developers will know it. This can be done pretty easily with `pipreqs` utility:

.. code-block::

    $ pip3 install some_package
    # Include this packages in one or multiple Python files
    $ pipreqs --save-path prod-requirements.txt # For anything in app.py / backend / views
    # or
    $ pipreqs --save-path docs/requirements.txt # For anything related for automated docs
    # or
    $ pipreqs --save-path dev-requirements.txt  # For anything else: tests, linting, etc.



.. warning::

    For the moment, `pipreqs` is not the best solution and might not detect every package that is required. To this end, please always manually check changes in the requirement files.
    Only keep changes related to your new package.

4. Adding new Javascript package
================================

As of npm 5.0.0, packages are automatically added to :code:`<repo>/packages.json`
when you install them. So, simply do this:

.. code-block:: console

    $ npm install some_package
