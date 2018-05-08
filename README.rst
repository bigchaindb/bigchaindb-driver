BigchainDB Python Driver
========================

.. image:: https://badges.gitter.im/bigchaindb/bigchaindb-driver.svg
   :alt: Join the chat at https://gitter.im/bigchaindb/bigchaindb-driver
   :target: https://gitter.im/bigchaindb/bigchaindb-driver?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


.. image:: https://img.shields.io/pypi/v/bigchaindb-driver.svg
        :target: https://pypi.python.org/pypi/bigchaindb-driver

.. image:: https://img.shields.io/travis/bigchaindb/bigchaindb-driver/master.svg
        :target: https://travis-ci.org/bigchaindb/bigchaindb-driver

.. image:: https://img.shields.io/codecov/c/github/bigchaindb/bigchaindb-driver/master.svg
    :target: https://codecov.io/github/bigchaindb/bigchaindb-driver?branch=master

.. image:: https://readthedocs.org/projects/bigchaindb-python-driver/badge/?version=latest
        :target: http://bigchaindb.readthedocs.io/projects/py-driver/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/bigchaindb/bigchaindb-driver/shield.svg
     :target: https://pyup.io/repos/github/bigchaindb/bigchaindb-driver/
     :alt: Updates


* Free software: Apache Software License 2.0
* Documentation: https://docs.bigchaindb.com/projects/py-driver/


Features
--------

* Support for preparing, fulfilling, and sending transactions to a BigchainDB
  node.
* Retrieval of transactions by id.

Install
----------

We recommend you use a virtual environment to install and update to the latest stable version using `pip`:

.. code-block:: text

    pip install -U bigchaindb-driver

If this fails, ensure you have python 3 installed, if you have both versions of python installed, to install and update using `pip`:

.. code-block:: text

    pip3 install -U bigchaindb-driver

If you want to install a non-stable version, i.e. a pre-release, check out the `pypi history`_ and choose your version to install.

Compatibility Matrix
--------------------

+-----------------------+---------------------------+
| **BigchainDB Server** | **BigchainDB Driver**     |
+=======================+===========================+
| ``>= 2.0.0a3``        | ``0.5.0a4``               |
+-----------------------+---------------------------+
| ``>= 2.0.0a2``        | ``0.5.0a2``               |
+-----------------------+---------------------------+
| ``>= 2.0.0a1``        | ``0.5.0a1``               |
+-----------------------+---------------------------+
| ``>= 1.0.0``          | ``0.4.x``                 |
+-----------------------+---------------------------+
| ``== 1.0.0rc1``       | ``0.3.x``                 |
+-----------------------+---------------------------+
| ``>= 0.9.1``          | ``0.2.x``                 |
+-----------------------+---------------------------+
| ``>= 0.8.2``          | ``>= 0.1.3``              |
+-----------------------+---------------------------+

`Although we do our best to keep the master branches in sync, there may be
occasional delays.`

License
--------
* `licenses`_ - open source & open content

Credits
-------

This package was initially created using Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template. Many BigchainDB developers have contributed since then.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
.. _pynacl: https://github.com/pyca/pynacl/
.. _Networking and Cryptography library: https://nacl.cr.yp.to/
.. _licenses: https://github.com/bigchaindb/bigchaindb-driver/blob/master/LICENSES.md
.. _pypi history: https://pypi.org/project/bigchaindb-driver/#history
