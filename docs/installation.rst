.. highlight:: shell

============
Installation
============


Development release
-------------------

To install bigchaindb-driver, run this very simple command in your terminal:

.. code-block:: console

    $ pip install --no-binary :all: --no-cache-dir --process-dependency-links bigchaindb_driver

This is the preferred method to install bigchaindb-driver, meanwhile it is
under heavy development. Once stabilized, the even simpler command


.. code-block:: console

    $ pip install bigchaindb_driver

will work. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for bigchaindb-driver can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/bigchaindb/bigchaindb_driver

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/bigchaindb/bigchaindb_driver/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/bigchaindb/bigchaindb_driver
.. _tarball: https://github.com/bigchaindb/bigchaindb_driver/tarball/master
