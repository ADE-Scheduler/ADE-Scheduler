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
    order to setup all you need for the feedback system to work properly.
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

Here, you will allow ADE Scheduler to send emails using your email address. You may
need to allow third-party applications to let ADE Schedule use your email address.
Please refer to your email provider documentation if so.
If you do not want to use the emails, please read next section.

In the :code:`<repo>/.flaskenv` file, make sure to write those lines and complete with
your
credentials:

.. code-block:: bash

    MAIL_USERNAME = <email address>
    MAIL_PASSWORD = <password>



II. Without credentials
-----------------------

In the :code:`<repo>/.flaskenv` file, make sure to write those lines:

.. code-block:: bash

    MAIL_USERNAME = <leave empty>
    MAIL_PASSWORD = <leave empty>
    MAIL_DISABLE = true


.. email setup end


1. Disable error emails
=======================

In the :code:`<repo>/.flaskenv` file, add this line:

.. code-block:: bash

    MAIL_SEND_ERRORS = false
