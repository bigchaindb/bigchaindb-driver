About this Documentation
========================

This section contains instructions to build and view the documentation locally,
using the ``docker-compose.yml`` file of the ``bigchaindb-driver``
repository: https://github.com/bigchaindb/bigchaindb-driver.

If you do not have a clone of the repo, you need to get one.


Building the documentation
--------------------------
To build the docs, simply run

.. code-block:: bash

    $ docker-compose up -d bdocs

Or if you prefer, start a ``bash`` session,

.. code-block:: bash

    $ docker-compose run --rm bdocs bash

and build the docs:

.. code-block:: bash

    root@a651959a1f2d:/usr/src/app# make -C docs html


Viewing the documentation
-------------------------
The docs will be hosted on port **55555**, and can be accessed over
[localhost](http:/localhost:33333), [127.0.0.1](http:/127.0.0.1:33333)
OR http:/HOST_IP:33333.

.. note:: If you are using ``docker-machine`` you need to replace ``localhost``
    with the ``ip`` of the machine (e.g.: ``docker-machine ip tm`` if your
    machine is named ``tm``).


Making changes
--------------
The necessary source code is mounted, which allows you to make modifications,
and view the changes by simply re-building the docs, and refreshing the
browser.
