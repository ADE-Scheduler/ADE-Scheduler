.. contribute tutorials

======================
Contribution tutorials
======================


.. contribute info begin

.. note::

    In order to keep the code as readable as possible, some guidelines are followed.
    Even though our coding style can never be perfect, it is good practice to follow
    a common syntax for all the project, as it will help newcomers getting easily into
    the project, as well debugging.

.. contribute info end

.. contents:: Table of content


Contribution setup
==================

.. note::
    Before running into the other tutorials, you should go through this one in
    order to setup all you need before contributing.
    As ADE Scheduler is hosted on a UNIX system machine, this tutorial will use the
    same commands as UNIX / LINUX system machines. No current support is provided for
    Windows users.


.. contribute setup begin

I. Install pre-commit
---------------------

Please follow the tutorial on the official site: https://pre-commit.com/

Once it's done:

.. code-block:: console

    $ cd <repo>
    $ pre-commit install

II. Create a branch
-------------------

If you plan to contribute, it is always better to work on a separate branch with a
meaningful name. To do so, in :code:`<repo>`:

.. code-block:: console

    $ git branch -b your-branch-name

.. contribute setup end


1. Running and writing tests
============================

At ADE Scheduler, we think that Continuous Integration is important and it is why we
are using unit tests. While any pull request must be validated by an automated CI
check, we highly recommend you to run the tests in your local machine if you made
change in the code. In :code:`<repo>`, simply run:

.. code-block:: console

    $ pytest

Whenever you modify or create a Python function, make sure there are sufficient unit
tests in the :code:`<repo>/tests/` folder to ensure its correctness.

2. Syntax linting with Black
============================

In order to keep our code clean and uniform, we use `Black <https://github.com/psf/black>`_.
For the moment, you do not really to care about how to use it as it is automated with
:ref:`pre-commit`. If, by any mean, pre-commit is not working, please always run Black
tool in :code:`<repo>` before committing changes:

.. code-block:: console

    $ black .

.. _pre-commit:

3. Committing changes
=====================

Before committing changes, you need to run in :code:`<repo>`:

.. code-block:: console

    $ pre-commit run --all-files

4. Translations
===============

Down below, we listed the most important things to know when using translation in
this project. You can learn many others from the
`Flask-Megatutorial about babel <https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n>`_.

4.1 Adding translations
-----------------------

If you add text which will be displayed on the website, you need to provide
translations. The language used in the code is always English.

Once the code is written, you need to extract the strings to translate:

.. code-block:: console

    $ cd <repo>
    $ pybabel extract -F translations/babel.cfg -k _l -o translations/messages.pot .
    $ pybabel update -i translations/messages.pot -d translations

Then, manually enter the translations in the various :code:`messages.po` files
located in :code:`<repo>/translations/<language>/LC_MESSAGES/`. When it's done, you
can compile the new translations from :code:`<repo>`:

.. code-block:: console

    $ pybabel compile -d translations

4.1.a In Python files
*********************

When you want a string to be translated, you need to do two things:

.. code-block:: python

    from flask_babel import gettext

    x = gettext("string_to_translate")

4.1.b In HTML and Javascript files
**********************************

Here, you only need to embed the string with mustaches:

.. code-block:: html

    {{ _('string_to_translate') }}

4.2 Adding a new language
-------------------------

You can easily add a new language (here *fr*) by executing this command from
:code:`<repo>`:

.. code-block:: console

    $ pybabel init -i translations/messages.pot -d translations -l fr

5. Documentation
================

5.1 Coding style
----------------

If you plan to contribute to ADE Scheduler, thank you! We really appreciate any help,
from anyone. You code will never be rejected because of its coding style but, if you
can follow the PEP8 guidelines, it will save us time!

Most PEP guidelines can be followed if you use the Black tool mentioned before.

5.2 Building the docs
---------------------

This whole documentation is actually built using the Sphinx tool. If you happen to
make modifications in the documentation, please try building the documentation before
making a pull request.

.. code-block:: console

    $ cd <repo>/docs
    $ pip install -r requirements.txt # Only run this once
    $ sphinx-apidoc -o source/backend ../backend -f
    $ sphinx-apidoc -o source/views ../views -f
    $ make html

Then, simply open :code:`build/html/index.html` in any browser to access the
documentation.

5.3 Additional readings
-----------------------

Here are listed some interesting readings about Sphinx's documentation tool:

* https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
* https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
* https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html


6. Profiling the Flask Application
==================================

Performance is a crucial aspect in ADE Scheduler as it will impact users' experience. This section discusses how to profile the Flask Application to better understand some performance issues you might encounter.

6.1 Setup
---------

Profiling is straighforward: you just need to add one line to your :code:`.flaskenv` file.

.. code-block:: bash
    :caption: :code:`<repo>/.flaskenv`

    PROFILE = True

And voilà! Once the application is (re-)started, it will now output the time taken by each request. It will also write the profile stats into files under the :code:`profile` folder.

If you wish the tweak the profiling settings, you can modify the :code:`app.py` file. More information can be found `here <https://werkzeug.palletsprojects.com/en/2.0.x/middleware/profiler/>`_.

6.2 Reading stats files
-----------------------

Interpreting :code:`.prof` files can be hard and we recommend you to use a graphical tool to do so. There are plenty available for free and we use `tuna <https://github.com/nschloe/tuna>`_. With this tool, it is straighforward to analyse the profiling stats.

.. code-block:: console

    $ cd <repo>
    $ tuna profile/<path_to_file.prof>
