=======================
Quickstart Installation
=======================

.. note::

    If you've already installed the BigchainDB Python Driver, you can skip to the :doc:`basic usage examples <usage>`.


Fast recipes for installing the Python driver (and its dependencies) on various operating systems. If you want to be more careful, understand what you're doing, be more selective in what you install, or install from the latest source code, then see :doc:`Advanced Installation <advanced-installation>`.


Ubuntu 14.04+
-------------

.. code-block:: bash

    sudo apt-get update

    sudo apt-get install python3 python3-pip libffi-dev

    pip3 install --upgrade pip setuptools bigchaindb_driver

To start an interactive Python 3 session, use:

.. code-block:: bash

    python3

You can now go to the :doc:`basic usage examples <usage>`.


Fedora 23+
----------

.. code-block:: bash

    sudo dnf update

    sudo dnf install python3 python3-pip libffi-devel

    pip3 install --upgrade pip setuptools bigchaindb_driver

To start an interactive Python 3 session, use:

.. code-block:: bash

    python3

You can now go to the :doc:`basic usage examples <usage>`.


Other Operating Systems
-----------------------

In the future, we may provide quick recipes for other operating systems. 
For now, see :doc:`Advanced Installation <advanced-installation>`.
