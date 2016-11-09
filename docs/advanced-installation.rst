=====================
Advanced Installation
=====================


Prerequisites
-------------

ffi.h
^^^^^

BigchainDB (server and driver) depends on `cryptoconditions`_, which now
uses `PyNaCl`_ (`Networking and Cryptography library`_), which depends on
``ffi.h``. Hence, depending on your setup, you may need to install the
development files for ``libffi``.

On Ubuntu 14.04 and 16.04, this works:

.. code-block:: bash

    sudo apt-get update

    sudo apt-get install libffi-dev

On Fedora 23 and 24, this works:

.. code-block:: bash

    sudo dnf update

    sudo dnf install libffi-devel

For other operating systems, just do some web searches for "ffi.h" with the name of your OS.


Python 3
^^^^^^^^

The BigchainDB Python Driver uses Python 3, preferably a recent version. You can check your version of Python using:

.. code-block:: bash

    python --version

If it says your version is 2.x, try:

.. code-block:: bash

    python3 --version

An easy way to install a specific version of Python, and to switch between versions of Python, is to use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_. Another option is `conda <http://conda.pydata.org/docs/>`_.


pip
^^^

You also need to get a recent Python 3 version of ``pip``, the Python package manager. It might be called ``pip3`` on your OS.

If you're using virtualenv or conda, then each virtual environment should include an appropriate version of ``pip``.

You can check your version of ``pip`` using:

.. code-block::

    pip --version

(You might also try the same command with ``pip3`` in place of ``pip``.)

``pip`` was at version 9.0.0 as of November 2016. If you need to upgrade your version of pip, see the page about that in the `BigchainDB Server docs <https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-latest-pip.html>`_.


Installing the BigchainDB Python Driver
---------------------------------------

Here we cover two ways to install the BigchainDB Python Driver: you can download and install the latest ``bigchaindb_driver`` package from PyPI (the Python Package Index) or you can dowload the latest source code from GitHub, and install that.


Installing from PyPI
^^^^^^^^^^^^^^^^^^^^

You can use ``pip`` (or ``pip3`` if necessary):

.. code-block:: bash

    pip install bigchaindb_driver

Since the BigchainDB Python Driver is under development, and may change rapidly, we  
recommend upgrading to the latest version from time to time:

.. code-block:: bash

    pip install --upgrade bigchaindb_driver


Installing from the Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The source code for the BigchainDB Python Driver can be downloaded from the `Github repo`_.
You can either clone the public repository:

.. code-block:: bash

    git clone git://github.com/bigchaindb/bigchaindb-driver

Or download the `tarball`_:

.. code-block:: bash

    curl  -OL https://github.com/bigchaindb/bigchaindb-driver/tarball/master

Once you have a copy of the source code, you can install it with:

.. code-block:: bash

    python setup.py install


.. _Github repo: https://github.com/bigchaindb/bigchaindb-driver
.. _tarball: https://github.com/bigchaindb/bigchaindb-driver/tarball/master
.. _pynacl: https://github.com/pyca/pynacl/
.. _Networking and Cryptography library: https://nacl.cr.yp.to/
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
