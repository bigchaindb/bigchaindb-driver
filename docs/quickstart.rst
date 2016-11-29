=========================
Quickstart / Installation
=========================

The BigchainDB Python Driver depends on:

1. ``libffi/ffi.h``
2. Python 3.5+
3. A recent Python 3 version of ``pip``
4. A recent Python 3 version of ``setuptools``

If you're missing one of those, then see below. Otherwise, you can install the BigchainDB Python Driver (``bigchaindb_driver``) using:

.. code-block:: bash

    pip install bigchaindb_driver

and then you can try the :doc:`Basic Usage Examples <usage>`.


How to Install the Dependencies
-------------------------------

Dependency 1: ffi.h
^^^^^^^^^^^^^^^^^^^

BigchainDB (server and driver) depends on `cryptoconditions`_,
which depends on `PyNaCl`_ (`Networking and Cryptography library`_),
which depends on ``ffi.h``.
Hence, depending on your setup, you may need to install the
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


Dependency 2: Python 3.5+
^^^^^^^^^^^^^^^^^^^^^^^^^

The BigchainDB Python Driver uses Python 3.5+. You can check your version of Python using:

.. code-block:: bash

    python --version

An easy way to install a specific version of Python, and to switch between versions of Python, is to use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_. Another option is `conda <http://conda.pydata.org/docs/>`_.


Dependency 3: pip
^^^^^^^^^^^^^^^^^

You also need to get a recent, Python 3 version of ``pip``, the Python package manager.

If you're using virtualenv or conda, then each virtual environment should include an appropriate version of ``pip``.

You can check your version of ``pip`` using:

.. code-block:: bash

    pip --version

``pip`` was at version 9.0.0 as of November 2016.
If you need to upgrade your version of ``pip``,
then see `the pip documentation <https://pip.pypa.io/en/stable/installing/>`_
or our page about that in the `BigchainDB Server docs <https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-latest-pip.html>`_.


Dependency 4: setuptools
^^^^^^^^^^^^^^^^^^^^^^^^

Once you have a recent Python 3 version of ``pip``, you should be able to upgrade ``setuptools`` using:

.. code-block:: bash

    pip install --upgrade setuptools



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


.. include:: ../HACKING.rst


.. _Github repo: https://github.com/bigchaindb/bigchaindb-driver
.. _tarball: https://github.com/bigchaindb/bigchaindb-driver/tarball/master
.. _pynacl: https://github.com/pyca/pynacl/
.. _Networking and Cryptography library: https://nacl.cr.yp.to/
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
