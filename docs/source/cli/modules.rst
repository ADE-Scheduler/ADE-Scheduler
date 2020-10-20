command-line tools
==================

Here are listed the different command-line tools which can be used directly in a command shell.
**Warning**: only the commands we have created are documented here, but many more
exist !


.. image:: ../../../static/img/client.gif
   :align: center

Documentation is generated using sphinx-click but does not offer a pretty rendering.
For a more detailed documentation, please use :code:`flask --help` directly in the
command shell.

.. click:: cli:client
    :prog: client
    :show-nested:

.. click:: cli:redis
   :prog: redis
   :show-nested:

.. click:: cli:schedules
   :prog: schedules
   :show-nested:

.. click:: cli:sql
   :prog: sql
   :show-nested:
