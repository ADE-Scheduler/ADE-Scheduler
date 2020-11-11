.. redis-server tutorials

======================
Redis server tutorials
======================

.. redis-server info begin

.. note::

    A Redis server is used as a cache memory storage and will, among others, act as a
    buffer between the ADE API and ADE Scheduler in order to enhance performance and
    to reduce delay between repetitive requests.

.. redis-server info end

.. contents:: Table of content


Redis setup
===========

.. note::
    Before running into the other tutorials, you should go through this one in
    order to setup all you need for the redis server manipulations.
    As ADE Scheduler is hosted on a UNIX system machine, this tutorial will use the
    same commands as UNIX / LINUX system machines. No current support is provided for
    Windows users.

.. redis-server setup begin

I. Install Redis
----------------

The installation process is pretty simple and we recommend you to follow the official
guide: https://redis.io/topics/quickstart

II. Check that it works
-----------------------

Before running into more troubles, make sure that Redis is correctly installed and that
you can manually start a server from command line. Something like this should work:

.. code-block:: console
    :caption: Start this in one terminal

    $ redis-server
    do not kill this terminal

.. code-block:: console
    :caption: Then, do this in another terminal

    $ redis-cli ping
    you should receive `pong`
    $ redis-cli shutdown
    this kills the redis server

.. redis-server setup end


1. Redis clients
================

There are 2 clients for the Redis server:

1.1 Built-in client
-------------------

The built-in client is provided with Redis installation. Its purpose is to provide tools
to modify or to read the content of the server. The documentation of this client can
be found online: https://redis.io/documentation

.. code-block:: console
    :caption: Invoking the Redis client (a Redis server must be running!)

    $ redis-cli

1.2 Flask client
----------------

The Flask client is defined by the `cli` module and its documentation can be found in
the appropriate section.

.. code-block:: console

    $ flask redis --help
