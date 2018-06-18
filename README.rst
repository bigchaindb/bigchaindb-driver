.. image:: media/repo-banner@2x.png

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

BigchainDB Python Driver
==========================

* Free software: Apache Software License 2.0
* Check our `Documentation`_

.. contents:: Table of Contents


Features
--------

* Support for preparing, fulfilling, and sending transactions to a BigchainDB
  node.
* Retrieval of transactions by id.

Install
----------

We recommend you use a virtual environment to install and update to the latest stable version using `pip` (or `pip3`):

.. code-block:: text

    pip install -U bigchaindb-driver

That will install the latest *stable* BigchainDB Python Driver. If you want to install an Alpha, Beta or RC version of the Python Driver, use something like:

.. code-block:: text

    pip install -U bigchaindb_driver==0.5.0a4

The above command will install version 0.5.0a4 (Alpha 4). You can find a list of all versions in `the release history page on PyPI <https://pypi.org/project/bigchaindb-driver/#history>`_.

More information on how to install the driver can be found in the `Quickstart`_

BigchainDB Documentation
------------------------------------
* `BigchainDB Server Quickstart`_
* `The Hitchhiker's Guide to BigchainDB`_
* `HTTP API Reference`_
* `All BigchainDB Documentation`_

Usage
----------
Example: Create a divisible asset for Alice who issues 10 token to Bob so that he can use her Game Boy.
Afterwards Bob spends 3 of these tokens.

.. code-block:: python

    # import BigchainDB and create an object
    from bigchaindb_driver import BigchainDB
    bdb_root_url = 'https://example.com:9984'
    bdb = BigchainDB(bdb_root_url)

    # generate a keypair
    from bigchaindb_driver.crypto import generate_keypair
    alice, bob = generate_keypair(), generate_keypair()

    # create a digital asset for Alice
    bike_token = {
        'data': {
            'token_for': {
                'game_boy': {
                    'serial_number': 'LR35902'
                }
            },
            'description': 'Time share token. Each token equals one hour of usage.',
        },
    }

    # prepare the transaction with the digital asset and issue 10 tokens for Bob
    prepared_token_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        recipients=[([bob.public_key], 10)],
        asset=bike_token)

    # fulfill and send the transaction
    fulfilled_token_tx = bdb.transactions.fulfill(
        prepared_token_tx,
        private_keys=alice.private_key)
    bdb.transactions.send_commit(fulfilled_token_tx)

    # Use the tokens
    # create the output and inout for the transaction
    transfer_asset = {'id': bike_token_id}
    output_index = 0
    output = fulfilled_token_tx['outputs'][output_index]
    transfer_input = {'fulfillment': output['condition']['details'],
                      'fulfills': {'output_index': output_index,
                                   'transaction_id': fulfilled_token_tx[
                                       'id']},
                      'owners_before': output['public_keys']}

    # prepare the transaction and use 3 tokens
    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=[([alice.public_key], 3), ([bob.public_key], 7)])

    # fulfill and send the transaction
    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=bob.private_key)
    sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

Compatibility Matrix
--------------------

+-----------------------+---------------------------+
| **BigchainDB Server** | **BigchainDB Driver**     |
+=======================+===========================+
| ``>= 2.0.0b1``        | ``0.5.0``               |
+-----------------------+---------------------------+
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

.. _Documentation: https://docs.bigchaindb.com/projects/py-driver/
.. _pypi history: https://pypi.org/project/bigchaindb-driver/#history
.. _Quickstart: https://docs.bigchaindb.com/projects/py-driver/en/latest/quickstart.html
.. _BigchainDB Server Quickstart: https://docs.bigchaindb.com/projects/server/en/latest/quickstart.html
.. _The Hitchhiker's Guide to BigchainDB: https://www.bigchaindb.com/developers/guide/
.. _HTTP API Reference: https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html
.. _All BigchainDB Documentation: https://docs.bigchaindb.com/
.. _licenses: https://github.com/bigchaindb/bigchaindb-driver/blob/master/LICENSES.md
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
