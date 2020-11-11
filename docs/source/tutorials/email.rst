.. email tutorials

===============
Email tutorials
===============

.. email info begin

.. note::

    In order to quickly receive feedback if anything goes wrong, ADE Scheduler will
    send you an email everytime an error occurs. This can be, of course, disabled to
    avoid email spamming. This email address can also be used to send account
    confirmation emails.

.. email info end

.. contents:: Table of content


Email setup
===========

.. note::
    Before running into the other tutorials, you should go through this one in
    order to setup all you need for the email feedback system to work properly.
    As ADE Scheduler is hosted on a UNIX system machine, this tutorial will use the
    same commands as UNIX / LINUX system machines. No current support is provided for
    Windows users.

.. warning::
    Make sure to never commit your :code:`<repo>/.flaskenv` file on Github! It should
    stay secret and the :code:`<repo>/.gitignore` file should prevent you from doing
    that.


.. email setup begin

I. With credentials
-------------------

If you are one of the maintainers, you should have received credentials in order to
proceed requests to the ADE API. If you do not have such credentials, please read
next section.

In the :code:`<repo>/.flaskenv` file, make sure to write those lines and complete with
your
credentials:

.. code-block:: bash

    ADE_SECRET_KEY=<secret key in bytes>
    ADE_URL=<url to get token>
    ADE_USER=<user>
    ADE_PASSWORD=<password>
    ADE_DATA=<grant_type>
    ADE_AUTHORIZATION=<authorization access>


II. Without credentials
-----------------------

Because we cannot share the credentials with everyone, but we want people to be able
to have the best environment to contribute to ADE Scheduler, we created a fake API.
To use this fake API, you will need to modify the :code:`<repo>/.flaskenv`

.. code-block:: bash

    ADE_SECRET_KEY=<leave empty>
    ADE_URL=<leave empty>
    ADE_USER=<leave empty>
    ADE_PASSWORD=<leave empty>
    ADE_DATA=<leave empty>
    ADE_AUTHORIZATION=<leave empty>

    ADE_FAKE_API=true

.. email setup end

