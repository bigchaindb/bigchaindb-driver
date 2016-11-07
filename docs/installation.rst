============
Installation
============

Prerequisites
-------------

OS-Level Prerequisites
^^^^^^^^^^^^^^^^^^^^^^

BigchainDB (server and driver) depends on `cryptoconditions`_, which now
uses `PyNaCl`_ (`Networking and Cryptography library`_), which depends on
``ffi.h``. Hence, depending on your setup, you may need to install the
development files for ``libffi``. Please see
`How to Install OS-Level Dependencies <https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-os-level-deps.html#how-to-install-os-level-dependencies>`_.


Python 3
^^^^^^^^

The BigchainDB Python Driver uses Python 3, preferably a recent version. You can check your version of Python using:

.. code-block:: bash

    python --version

An easy way to install a specific version of Python, and to switch between versions of Python, is to use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_. Another option is `conda <http://conda.pydata.org/docs/>`_.


pip
^^^

You also need to get a recent version of ``pip``, the Python package manager. See the `BigchainDB Server docs about how to do that <https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-latest-pip.html>`_.


Installing the BigchainDB Python Driver
---------------------------------------

Here we cover two ways to install the BigchainDB Python Driver: you can download and install the latest ``bigchaindb_driver`` package from PyPI (the Python Package Index) or you can dowload the latest source code from GitHub, and install that.


Installing from PyPI
^^^^^^^^^^^^^^^^^^^^

You can use ``pip``:

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
