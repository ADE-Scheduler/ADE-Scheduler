.. _setup tutorials:

===============
Setup tutorials
===============

.. centered::
    Everything you need in order to run this project

.. contents:: Table of content


This page contains all the required steps that you must follow in order to have a
fully working development environment. Each tutorial can be found its in own section
with more details on own to use particular tools.

.. warning::

    It is important to follow this setup guide in the correct order of sections!


1. Redis server
===============

.. include:: redis-server.rst
    :start-after: redis-server info begin
    :end-before: redis-server info end


.. include:: redis-server.rst
    :start-after: redis-server setup begin
    :end-before: redis-server setup end


2. ADE Scheduler
================

.. include:: ade-scheduler.rst
    :start-after: ade-scheduler info begin
    :end-before: ade-scheduler info end


.. include:: ade-scheduler.rst
    :start-after: ade-scheduler setup begin
    :end-before: ade-scheduler setup end


3. Database
===========

.. include:: database.rst
    :start-after: database info begin
    :end-before: database info end


.. include:: database.rst
    :start-after: database setup begin
    :end-before: database setup end


4. ADE API
==========

# Should talk about token granting and fake api

5. Contributing
===============

# Should incude pre-commit, black linter, tests
