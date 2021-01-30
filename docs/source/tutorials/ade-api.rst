.. ade-api tutorials

=================
ADE API tutorials
=================

.. ade-api info begin

.. note::

    The ADE API is the interface allowing ADE Scheduler to obtain all the
    information it needs, such as events, courses, etc., from the ADE server at
    UCLouvain.

.. ade-api info end

.. contents:: Table of content


ADE API setup
=============

.. note::
    Before running into the other tutorials, you should go through this one in
    order to setup all you need for the calendar to work properly.
    As ADE Scheduler is hosted on a UNIX system machine, this tutorial will use the
    same commands as UNIX / LINUX system machines. No current support is provided for
    Windows users.

.. warning::
    Make sure to never commit your :code:`<repo>/.flaskenv` file on Github! It should
    stay secret and the :code:`<repo>/.gitignore` file should prevent you from doing
    that.

.. ade-api setup begin

I. With credentials
-------------------

If you are one of the maintainers, you should have received credentials in order to
proceed requests to the ADE API. If you do not have such credentials, please read
next section.

In the :code:`<repo>/.flaskenv` file, make sure to write those lines and complete with
your
credentials:

.. code-block:: bash

    ADE_URL = <url to get token>
    ADE_DATA = <grant_type>
    ADE_AUTHORIZATION = <authorization access>


II. Without credentials
-----------------------

Because we cannot share the credentials with everyone, but we want people to be able
to have the best environment to contribute to ADE Scheduler, we created a fake API.
To use this fake API, you will need to modify the :code:`<repo>/.flaskenv`

.. code-block:: bash

    ADE_URL = <leave empty>
    ADE_DATA = <leave empty>
    ADE_AUTHORIZATION = <leave empty>

    ADE_FAKE_API = true

Next, you need to `download a compressed folder <https://drive.google.com/file/d/1E8zboqLDRdufXnXZJUrLnSLih_ATaekO/view?usp=sharing>`_ containing the fake api as a folder containing pickled requests and a README file explaining everything that you can request with this API. The :code:`fake_api` folder should be placed in the :code:`<repo>` folder. Please contact us if something isn't working as expected.

.. note::
    We know it is not the best way to provide you an access to the ADE API but we are still working on this and propositions are more than welcome!

.. ade-api setup end
