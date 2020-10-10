.. ADE-Scheduler documentation master file, created by
   sphinx-quickstart on Tue Jun 23 19:26:22 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to ADE-Scheduler's documentation !
==========================================


.. image:: ../../static/img/ade_scheduler_icon.png
   :width: 200
   :align: center

This documentation is here to help contributors understanding how the
project is built.

*******
Backend
*******

This module implements all the computationally intensive and complex
functions, in a more or less optimized manner, in order to provide complete
services to end users.

*****
Views
*****

This module makes the interface between the backend and the frontend. All
requests are handled by this module.

.. toctree::
   :maxdepth: 3
   :caption: Table of content:

   backend/modules
   views/modules




Index et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
