.. ADE-Scheduler documentation master file, created by
   sphinx-quickstart on Tue Jun 23 19:26:22 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ../../static/img/ade_scheduler_icon.png
   :width: 200
   :align: center

==========================================
Welcome to ADE-Scheduler's documentation !
==========================================

This documentation is here to help contributors understanding how the
project is built.

Quickstart
==========

Installation
------------

To setup your ADE Scheduler project locally, we recommend you to follow our
:ref:`setup tutorial`.

Documentation
-------------

* **Tutorials**

.. note::

    This section contains many tutorials on how ADE Scheduler is built and how to
    run the project on your local machine.

.. toctree::
    :maxdepth: 2
    :caption: Tutorials:

    tutorials/setup
    tutorials/index

.. toctree::
   :maxdepth: 3
   :caption: Python modules:

   backend/modules
   views/modules

* **Backend**

.. note::

    This module implements all the computationally intensive and complex
    functions, in a more or less optimized manner, in order to provide complete
    services to end users.


* **Views**

.. note::

    This module makes the interface between the backend and the frontend. All
    requests are handled by this module.


.. toctree::
   :maxdepth: 2
   :caption: Client modules:

   cli/modules

.. note::

    This module contains all the command-line tools built to interact with
    ADE-Scheduler's data such database statistics.

Contributor Guide
=================

We really encourage people who want to contribute in any way to do so !
There are many ways to help us:

- Pointing a problem
- Asking for a new feature
- Fixing a problem
- Adding language translations
- Fixing typos in the code

and so on...

Please take a look at our Contribution tutorials.


Index et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
