.. _setup tutorial:

==============
Setup tutorial
==============

.. centered::
    *Everything you need in order to run this project*

.. contents:: Table of content


This page contains all the required steps that you must follow in order to have a
fully working development environment. Each tutorial can be found its in own section
with more details on how to use particular tools.

.. warning::

    It is important to follow this setup guide in the correct order of sections!


(*New*) Docker setup
====================

A new setup alternative is the Docker setup. This setup is a lot more simple as it will install most of the requirements for you.


.. include:: docker.rst
    :start-after: docker info begin
    :end-before: docker info end


.. include:: docker.rst
    :start-after: docker setup begin
    :end-before: docker setup end

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

.. include:: ade-api.rst
    :start-after: ade-api info begin
    :end-before: ade-api info end


.. include:: ade-api.rst
    :start-after: ade-api setup begin
    :end-before: ade-api setup en


5. Email
========

.. include:: email.rst
    :start-after: email info begin
    :end-before: email info end


.. include:: email.rst
    :start-after: email setup begin
    :end-before: email setup en


6. Launch
=========

.. include:: launch.rst
    :start-after: launch info begin
    :end-before: launch info end


7. Contributing
===============

.. include:: contribute.rst
    :start-after: contribute info begin
    :end-before: contribute info end


.. include:: contribute.rst
    :start-after: contribute setup begin
    :end-before: contribute setup en
