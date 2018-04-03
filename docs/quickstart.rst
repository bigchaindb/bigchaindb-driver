=========================
Quickstart / Installation
=========================

The BigchainDB Python Driver depends on:

1. Python 3.5+
2. A recent Python 3 version of ``pip``
3. A recent Python 3 version of ``setuptools``
4. cryptography and cryptoconditions

If you're missing one of those, then see below. Otherwise, you can install the BigchainDB Python Driver (``bigchaindb_driver``) using:

.. code-block:: bash

    $ pip3 install bigchaindb_driver

Next: :doc:`determine the BigchainDB Root URL of the BigchainDB node or cluster you want to connect to <connect>`.


How to Install the Dependencies
-------------------------------


Dependency 1: Python 3.5+
^^^^^^^^^^^^^^^^^^^^^^^^^

The BigchainDB Python Driver uses Python 3.5+. You can check your version of Python using:

.. code-block:: bash

    $ python --version

    OR

    $ python3 --version

An easy way to install a specific version of Python, and to switch between versions of Python, is to use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_. Another option is `conda <http://conda.pydata.org/docs/>`_.


Dependency 2: pip
^^^^^^^^^^^^^^^^^

You also need to get a recent, Python 3 version of ``pip``, the Python package manager.

If you're using virtualenv or conda, then each virtual environment should include an appropriate version of ``pip``.

You can check your version of ``pip`` using:

.. code-block:: bash

    $ pip --version

    OR

    $ pip3 --version

``pip`` was at version 9.0.0 as of November 2016.
If you need to upgrade your version of ``pip``,
then see `the pip documentation <https://pip.pypa.io/en/stable/installing/>`_
or our page about that in the `BigchainDB Server docs <https://docs.bigchaindb.com/projects/server/en/latest/appendices/install-latest-pip.html>`_.


Dependency 3: setuptools
^^^^^^^^^^^^^^^^^^^^^^^^

Once you have a recent Python 3 version of ``pip``, you should be able to upgrade ``setuptools`` using:

.. code-block:: bash

    $ pip install --upgrade setuptools

    OR

    $ pip3 install --upgrade setuptools


Dependency 4: cryptography and cryptoconditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

BigchainDB(server and driver) also depends on `cryptography`_ and `cryptoconditions`_.

* `cryptography`_ depends on `libssl`_, `libcrypto`_ which also depends on (`Python development library and header files`_).
* `cryptoconditions`_ depends on `PyNaCl`_ (`Networking and Cryptography library`_) which depends on ``ffi.h``.

On Ubuntu 14.04 and 16.04, this works:

.. code-block:: bash

    $ sudo apt-get update

    $ sudo apt-get install python3-dev libssl-dev libffi-dev

On Fedora 23 and 24, this works:

.. code-block:: bash

    $ sudo dnf update

    $ sudo dnf install python-devel openssl-devel libffi-devel

For other operating systems, please refer to `the cryptography installation guide <https://cryptography.io/en/latest/installation/#installation>`_.


Installing the Driver
---------------------

Now you can install the BigchainDB Python Driver (``bigchaindb_driver``) using:

.. code-block:: bash

    $ pip install bigchaindb_driver

    OR

    $ pip3 install bigchaindb_driver

Next: :doc:`determine the BigchainDB Root URL of the BigchainDB node or cluster you want to connect to <connect>`.


Advanced Installation Options
-----------------------------

See the :doc:`Advanced Installation Options <advanced-installation>` page.


.. _pynacl: https://github.com/pyca/pynacl/
.. _Networking and Cryptography library: https://nacl.cr.yp.to/
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
.. _cryptography: https://cryptography.io/en/latest/
.. _libssl-dev: https://packages.debian.org/jessie/libssl-dev
.. _openssl-devel: https://rpmfind.net/linux/rpm2html/search.php?query=openssl-devel
.. _libssl: https://github.com/openssl/openssl
.. _libcrypto: https://github.com/openssl/openssl
.. _Python development library and header files: https://github.com/python/cpython


Installation Guide for Developers
----------------------------------

Here's how to set up `bigchaindb-driver`_ for local
development.

1. Fork the `bigchaindb-driver`_ repo on GitHub.
2. Clone your fork locally and enter into the project::

    $ git clone git@github.com:your_name_here/bigchaindb-driver.git
    $ cd bigchaindb-driver/

3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, check that your changes pass flake8
   and the tests. For the tests, you'll need to  start the MongoDB, Tendermint
   and BigchainDB servers::

    $ docker-compose up -d bigchaindb

5. flake8 check::

    $ docker-compose run --rm bigchaindb-driver flake8 bigchaindb_driver tests

6. To run the tests::

    $ docker-compose run --rm bigchaindb-driver pytest -v

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

..

    We use pre-commit_ which should be triggered with every commit. Some hooks will change files but others will give errors that needs to be fixed. Every time a hook is failing you need to add the changed files again.
    The hooks we use can be found in the yaml_ config file.

8. Submit a pull request through the GitHub website.

.. _pre-commit: http://pre-commit.com/
.. _yaml: https://github.com/bigchaindb/bigchaindb-driver/blob/master/.pre-commit-config.yaml
.. _bigchaindb-driver: https://github.com/bigchaindb/bigchaindb-driver
