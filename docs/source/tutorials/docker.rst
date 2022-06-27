
======================
Docker setup tutorials
======================

.. docker info begin

.. note::

    This section will describe how to install and run ADE Scheduler under Docker on your system.

.. docker info end

.. contents:: Table of content


Docker setup
============

.. note::
    Even though it was not tested, this setup should work on any platform: Linux, Mac OS X, Windows.

.. docker setup begin

I. Install Docker
-----------------

First, you must have Docker installed on your system. We recommend to install it from the official website: https://docs.docker.com/desktop/#download-and-install

II. Pull Docker image
---------------------

Pull the Docker image:

.. code-block:: console

    $ docker pull gilponcelet/ade-scheduler


III. Build and run the ADE Scheduler server
-------------------------------------------

Run the following in :code:`<repo>`:

.. code-block:: console

    $ docker build -f Dockerfile -t ade-scheduler .
    $ docker run --name ade-scheduler -it -p 5000:5000 -v <Path to ADE-Scheduler folder>:/ADE-Scheduler ade-scheduler
    $ docker start -i ade-scheduler       # To run the app
    $ docker exec -it ade-scheduler bash  # To e.g. run `flask shell`

.. warning::

    This tutorial is still under development! Any problem you might encounter is important for us, so please contact use whenever you need help :-)

.. docker setup end
