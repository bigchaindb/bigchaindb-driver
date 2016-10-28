BigchainDB Python Driver
========================


.. image:: https://img.shields.io/pypi/v/bigchaindb-driver.svg
        :target: https://pypi.python.org/pypi/bigchaindb-driver

.. image:: https://img.shields.io/travis/bigchaindb/bigchaindb-driver.svg
        :target: https://travis-ci.org/bigchaindb/bigchaindb-driver

.. image:: https://img.shields.io/codecov/c/github/bigchaindb/bigchaindb-driver/master.svg
    :target: https://codecov.io/github/bigchaindb/bigchaindb-driver?branch=master

.. image:: https://readthedocs.org/projects/bigchaindb-python-driver/badge/?version=latest
        :target: http://bigchaindb.readthedocs.io/projects/py-driver/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/bigchaindb/bigchaindb-driver/shield.svg
     :target: https://pyup.io/repos/github/bigchaindb/bigchaindb-driver/
     :alt: Updates


Python driver for BigchainDB

* Development Status: Pre-Alpha
* Free software: Apache Software License 2.0
* Documentation: https://docs.bigchaindb.com/projects/py-driver/

Important
---------
Since the BigchainDB driver is under development, and may rapidly change, we  
recommend installing the latest version:

.. code-block:: bash

    pip install --upgrade bigchaindb_driver

Lastly, BigchainDB (server and driver) depend on `cryptoconditions`_, which now
uses `PyNaCl`_ (`Networking and Cryptography library`_) which depends on
``ffi.h``. Hence, depending on your setup you may need to install the
development files for ``libffi``. Please see
`How to Install OS-Level Dependencies <https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-os-level-deps.html#how-to-install-os-level-dependencies>`_.


Features
--------

* Minimal support for `CREATE`, `TRANSFER`, and `GET` operations on the
  `/transactions` endpoint.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
.. _pynacl: https://github.com/pyca/pynacl/
.. _Networking and Cryptography library: https://nacl.cr.yp.to/
