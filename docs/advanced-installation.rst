Advanced Installation Options
=============================

Installing from the Source Code
-------------------------------

The source code for the BigchainDB Python Driver can be downloaded from the `Github repo`_.
You can either clone the public repository:

.. code-block:: bash

    git clone git://github.com/bigchaindb/bigchaindb-driver

Or download the `tarball`_:

.. code-block:: bash

    curl  -OL https://github.com/bigchaindb/bigchaindb-driver/tarball/master

Once you have a copy of the source code, you can install it by going to the directory containing ``setup.py`` and doing:

.. code-block:: bash

    python setup.py install


Installing latest master with pip
---------------------------------

To work with the latest BigchainDB (server) master branch:

.. code-block:: bash

    $ pip install --process-dependency-links git+https://github.com/bigchaindb/bigchaindb-driver.git

Then connect to some BigchainDB node which is running BigchainDB server ``master``.


.. _Github repo: https://github.com/bigchaindb/bigchaindb-driver
.. _tarball: https://github.com/bigchaindb/bigchaindb-driver/tarball/master