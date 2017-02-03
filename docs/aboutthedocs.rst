About this Documentation
========================

This section contains instructions to build and view the documentation locally,
using the ``docker-compose`` ``docs.yml`` file of the ``bigchaindb-driver``
repository: https://github.com/bigchaindb/bigchaindb-driver.

If you do not have a clone of the repo, you need to get one.


Building the documentation
--------------------------
To build the docs, simply run

.. code-block:: bash

    $ docker-compose --file docs.yml up -d bdocs

Or if you prefer, start a ``bash`` session,

.. code-block:: bash

    $ docker-compose --file docs.yml run --rm bdocs bash

and build the docs:

.. code-block:: bash

    root@a651959a1f2d:/usr/src/app# make -C docs html


Viewing the documentation
-------------------------
You can start a little web server to view the docs at http://localhost:55555/

.. code-block:: bash

    $ docker-compose --file docs.yml up -d vdocs

.. note:: If you are using ``docker-machine`` you need to replace ``localhost``
    with the ``ip`` of the machine (e.g.: ``docker-machine ip tm`` if your
    machine is named ``tm``).


Making changes
--------------
The necessary source code is mounted, which allows you to make modifications,
and view the changes by simply re-building the docs, and refreshing the
browser.
