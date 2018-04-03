#########################
Handcrafting Transactions
#########################

For those who wish to assemble transaction payloads "by hand", with examples in
Python.

.. contents::
    :local:
    :depth: 1

********
Overview
********

Submitting a transaction to a BigchainDB node consists of three main steps:

1. Preparing the transaction payload;
2. Fulfilling the prepared transaction payload; and
3. Sending the transaction payload via HTTPS.

Step 1 and 2 can be performed offline on the client. That is, they do not
require any connection to any BigchainDB node.

For convenience's sake, some utilities are provided to prepare and fulfill a
transaction via the :class:`~.bigchaindb_driver.BigchainDB` class, and via the
:mod:`~bigchaindb_driver.offchain` module. For an introduction on using these
utilities, see the :ref:`basic-usage` or :ref:`advanced-usage` sections.

The rest of this document will guide you through completing steps 1 and 2
manually by revisiting some of the examples provided in the usage sections.
We will:

* provide all values, including the default ones;
* generate the transaction id;
* learn to use crypto-conditions to generate a condition that locks the
  transaction, hence protecting it from being consumed by an unauthorized user;
* learn to use crypto-conditions to generate a fulfillment that unlocks
  the transaction asset, and consequently enact an ownership transfer.

In order to perform all of the above, we'll use the following Python libraries:

* :mod:`json`: to serialize the transaction dictionary into a JSON formatted
  string;
* `sha3`_: to hash the serialized transaction; and
* `cryptoconditions`_: to create conditions and fulfillments

With BigchainDB Server version 2.0 some changes on how to handcraft a transaction were introduced. You can read about
the changes to the BigchainDB Server in our `blog post`_.

High-level view of a transaction in Python
==========================================
For detailed documentation on the transaction schema, please consult
`The Transaction Model`_ and `The Transaction Schema`_.

From the point of view of Python, a transaction is simply a dictionary:

.. code-block:: python

    {
        'operation': 'CREATE',
        'asset': {
            'data': {
                'bicycle': {
                    'manufacturer': 'bkfab',
                    'serial_number': 'abcd1234'
                }
            }
        },
        'version': '2.0',
        'outputs': [
            {
                'condition': {
                    'details': {
                        'public_key': '2GoYB8cMZQrUBZzx9BH9Bq92eGWXBy3oanDXbRK3YRpW',
                        'type': 'ed25519-sha-256'
                    },
                    'uri': 'ni:///sha-256;1hBHivh6Nxhgi2b1ndUbP55ZlyUFdLC9BipPUBWth7U?fpt=ed25519-sha-256&cost=131072'
                },
                'public_keys': [
                    '2GoYB8cMZQrUBZzx9BH9Bq92eGWXBy3oanDXbRK3YRpW'
                ],
                'amount': '1'
            }
        ],
        'inputs': [
            {
                'fulfills': None,
                'owners_before': [
                    '2GoYB8cMZQrUBZzx9BH9Bq92eGWXBy3oanDXbRK3YRpW'
                ],
                'fulfillment': {
                    'public_key': '2GoYB8cMZQrUBZzx9BH9Bq92eGWXBy3oanDXbRK3YRpW',
                    'type': 'ed25519-sha-256'
                }
            }
        ],
        'id': None,
        'metadata': {
            'planet': 'earth'
        }
    }

Because a transaction must be signed before being sent, the
``fulfillment`` must be provided by the client.

.. important:: **Implications of Signed Payloads**

    Because BigchainDB relies on cryptographic signatures, the payloads need to
    be fully prepared and signed on the client side. This prevents the
    server(s) from tampering with the provided data.

    This enhanced security puts more work on the clients, as various values
    that could traditionally be generated on the server side need to be
    generated on the client side.


.. _bicycle-asset-creation-revisited:

********************************
Bicycle Asset Creation Revisited
********************************

We begin by creating a test user: alice

.. ipython::

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: alice = generate_keypair()

The Prepared Transaction
========================
Recall that in order to prepare a transaction, we had to do something similar
to:

.. ipython::

    In [0]: from bigchaindb_driver.offchain import prepare_transaction

    In [0]: bicycle = {
       ...:     'data': {
       ...:         'bicycle': {
       ...:             'serial_number': 'abcd1234',
       ...:             'manufacturer': 'bkfab',
       ...:         },
       ...:     },
       ...: }

    In [0]: metadata = {'planet': 'earth'}

    In [0]: prepared_creation_tx = prepare_transaction(
       ...:     operation='CREATE',
       ...:     signers=alice.public_key,
       ...:     asset=bicycle,
       ...:     metadata=metadata,
       ...: )

and the payload of the prepared transaction looked similar to:

.. ipython::

    In [0]: prepared_creation_tx

Note ``alice``'s public key is listed in the public keys of ``outputs``:

.. ipython::

    In [0]: alice.public_key

    In [0]: prepared_creation_tx['outputs'][0]['public_keys'][0] == alice.public_key

We are now going to craft this payload by hand.

version
-------
As of BigchainDB 2.0, the transaction ``version`` is set to 2.0.

.. ipython::

    In [0]: version = '2.0'

asset
-----
Because this is a ``CREATE`` transaction, we provide the data payload for the
asset to the transaction (see `the transfer example below <#bicycle-asset-transfer-revisited>`_
for how to construct assets in ``TRANSFER`` transactions):

.. ipython::

    In [0]: asset = {
       ...:     'data': {
       ...:         'bicycle': {
       ...:             'manufacturer': 'bkfab',
       ...:             'serial_number': 'abcd1234',
       ...:         },
       ...:     },
       ...: }

metadata
--------
.. ipython::

    In [0]: metadata = {'planet': 'earth'}

operation
---------
.. ipython::

    In [0]: operation = 'CREATE'

.. important::

    Case sensitive; all letters must be capitalized.

outputs
-------
The purpose of the output condition is to lock the transaction, such that a
valid input fulfillment is required to unlock it. In the case of
signature-based schemes, the lock is basically a public key, such that in order
to unlock the transaction one needs to have the private key.

Let's review the output payload of the prepared transaction, to see what we are
aiming for:

.. ipython::

    In [0]: prepared_creation_tx['outputs'][0]

The difficult parts are the condition details and URI. We'll now see how to
generate them using the ``cryptoconditions`` library:

.. note:: In BigchainDB keys are encoded in base58 but the cryptoconditions
    library expects an unencoded byte string so we will have to decode the
    base58 key before we can use it with cryptoconditions.

    .. ipython::

        In [0]: import base58

    A base58 encoded key:

    .. ipython::

        In [0]: alice.public_key

    Becomes:

    .. ipython::

        In [0]: base58.b58decode(alice.public_key)

.. ipython::

    In [0]: from cryptoconditions import Ed25519Sha256

    In [0]: ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

generate the condition URI:

.. ipython::

    In [0]: ed25519.condition_uri

So now you have a condition URI for Alice's public key.

As for the details:

.. ipython::

    In [0]: condition_details = {
       ...:     'type': ed25519.TYPE_NAME,
       ...:     'public_key': base58.b58encode(ed25519.public_key),
       ...: }

We can now easily assemble the ``dict`` for the output:

.. ipython::

    In [0]: output = {
       ...:     'amount': '1',
       ...:     'condition': {
       ...:         'details': condition_details,
       ...:         'uri': ed25519.condition_uri,
       ...:     },
       ...:     'public_keys': (alice.public_key,),
       ...: }

Let's recap and set the ``outputs`` key with our self-constructed condition:

.. ipython::

    In [0]: from cryptoconditions import Ed25519Sha256

    In [0]: ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    In [0]: output = {
       ...:     'amount': '1',
       ...:     'condition': {
       ...:         'details': {
       ...:             'type': ed25519.TYPE_NAME,
       ...:             'public_key': base58.b58encode(ed25519.public_key),
       ...:         },
       ...:         'uri': ed25519.condition_uri,
       ...:     },
       ...:     'public_keys': (alice.public_key,),
       ...: }

    In [0]: outputs = (output,)

The key part is the condition URI:

.. ipython::

    In [0]: ed25519.condition_uri

To know more about its meaning, you may read the `cryptoconditions internet
draft`_.


inputs
------
The input fulfillment for a ``CREATE`` operation is somewhat special, and
simplified:

.. ipython::

    In [0]: input_ = {
       ...:     'fulfillment': None,
       ...:     'fulfills': None,
       ...:     'owners_before': (alice.public_key,)
       ...: }

* The ``fulfills`` field is empty because it's a ``CREATE`` operation;
* The ``'fulfillment'`` value is ``None`` as it will be set during the
  `fulfillment step <#the-fulfilled-transaction>`_; and
* The ``'owners_before'`` field identifies the issuer(s) of the asset that is
  being created.


The ``inputs`` value is simply a list or tuple of all inputs:

.. ipython::

    In [0]: inputs = (input_,)


.. note:: You may rightfully observe that the input generated in
    ``prepared_creation_tx`` via ``prepare_transaction()`` differs:

    .. ipython::

        In [0]: prepared_creation_tx['inputs'][0]

    More precisely, the value of ``'fulfillment'`` is not ``None``:

    .. ipython::

        In [0]: prepared_creation_tx['inputs'][0]['fulfillment']

    The quick answer is that it simply is not needed, and can be set to
    ``None``.

Up to now
---------

Putting it all together:

.. ipython::

    In [0]: handcrafted_creation_tx = {
       ...:     'asset': asset,
       ...:     'metadata': metadata,
       ...:     'operation': operation,
       ...:     'outputs': outputs,
       ...:     'inputs': inputs,
       ...:     'version': version,
       ...:     'id': None,
       ...: }

Note how ``handcrafted_creation_tx`` includes a key-value pair ``'id': None``. The 'id' value is None as it will be set during the fulfillment step.

.. ipython::

    In [0]: handcrafted_creation_tx

You may observe that

.. ipython::

    In [0]: handcrafted_creation_tx == prepared_creation_tx

.. ipython::

    In [0]: from copy import deepcopy

    In [0]: # back up

    In [0]: prepared_creation_tx_bk = deepcopy(prepared_creation_tx)

    In [0]: # set input fulfillment to None

    In [0]: prepared_creation_tx['inputs'][0]['fulfillment'] = None

    In [0]: handcrafted_creation_tx == prepared_creation_tx

Are still not equal because we used tuples instead of lists.

.. ipython::

    In [0]: import json

    In [0]: # serialize to json str

    In [0]: json_str_handcrafted_tx = json.dumps(handcrafted_creation_tx, sort_keys=True)

    In [0]: json_str_prepared_tx = json.dumps(prepared_creation_tx, sort_keys=True)

.. ipython::

    In [0]: json_str_handcrafted_tx == json_str_prepared_tx

    In [0]: prepared_creation_tx = prepared_creation_tx_bk

Let's recap how we've put all the code together to generate the above payload:

.. code-block:: python

    from cryptoconditions import Ed25519Sha256
    from bigchaindb_driver.crypto import generate_keypair
    import base58

    alice = generate_keypair()

    operation = 'CREATE'

    version = '2.0'

    asset = {
        'data': {
            'bicycle': {
                'manufacturer': 'bkfab',
                'serial_number': 'abcd1234',
            },
        },
    }

    metadata = {'planet': 'earth'}

    ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    output = {
        'amount': '1',
        'condition': {
            'details': {
                'type': ed25519.TYPE_NAME,
                'public_key': base58.b58encode(ed25519.public_key),
            },
            'uri': ed25519.condition_uri,
        },
        'public_keys': (alice.public_key,),
    }
    outputs = (output,)

    input_ = {
        'fulfillment': None,
        'fulfills': None,
        'owners_before': (alice.public_key,)
    }
    inputs = (input_,)

    handcrafted_creation_tx = {
        'asset': asset,
        'metadata': metadata,
        'operation': operation,
        'outputs': outputs,
        'inputs': inputs,
        'version': version,
        'id': None,
    }

The Fulfilled Transaction
=========================

.. ipython::

    In [0]: from cryptoconditions.crypto import Ed25519SigningKey

    In [0]: import json

    In [0]: from sha3 import sha3_256

    In [0]: # fulfill prepared transaction

    In [0]: from bigchaindb_driver.offchain import fulfill_transaction

    In [0]: fulfilled_creation_tx = fulfill_transaction(
       ...:     prepared_creation_tx,
       ...:     private_keys=alice.private_key,
       ...: )

    In [0]: # fulfill handcrafted transaction (with our previously built ED25519 fulfillment)

    In [0]: ed25519.to_dict()

    In [0]: message = json.dumps(
       ...:     handcrafted_creation_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: message = sha3_256(message.encode())

    In [0]: ed25519.sign(message.digest(), base58.b58decode(alice.private_key))

    In [0]: fulfillment_uri = ed25519.serialize_uri()

    In [0]: handcrafted_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

id
--

The transaction's id is essentially a SHA3-256 hash of the entire transaction
(up to now), with a few additional tweaks:

.. ipython::

    In [0]: import json

    In [0]: from sha3 import sha3_256

    In [0]: json_str_tx = json.dumps(
       ...:     handcrafted_creation_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: creation_txid = sha3_256(json_str_tx.encode()).hexdigest()

    In [0]: handcrafted_creation_tx['id'] = creation_txid

Compare this to the txid of the transaction generated via
``prepare_transaction()``:

.. ipython::

    In [0]: creation_txid == fulfilled_creation_tx['id']

Let's check this:

.. ipython::

    In [0]: fulfilled_creation_tx['inputs'][0]['fulfillment'] == fulfillment_uri

    In [0]: json.dumps(fulfilled_creation_tx, sort_keys=True) == json.dumps(handcrafted_creation_tx, sort_keys=True)

The fulfilled transaction, ready to be sent over to a BigchainDB node:

.. ipython::

    In [0]: fulfilled_creation_tx


In a nutshell
=============

Handcrafting a ``CREATE`` transaction can be done as follows:

.. code-block:: python

    import json

    import base58
    import sha3
    from cryptoconditions import Ed25519Sha256

    from bigchaindb_driver.crypto import generate_keypair


    alice = generate_keypair()

    operation = 'CREATE'

    version = '2.0'

    asset = {
        'data': {
            'bicycle': {
                'manufacturer': 'bkfab',
                'serial_number': 'abcd1234',
            },
        },
    }

    metadata = {'planet': 'earth'}

    ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    output = {
        'amount': '1',
        'condition': {
            'details': {
                'type': ed25519.TYPE_NAME,
                'public_key': base58.b58encode(ed25519.public_key),
            },
            'uri': ed25519.condition_uri,
        },
        'public_keys': (alice.public_key,),
    }
    outputs = (output,)

    input_ = {
        'fulfillment': None,
        'fulfills': None,
        'owners_before': (alice.public_key,)
    }
    inputs = (input_,)

    handcrafted_creation_tx = {
        'asset': asset,
        'metadata': metadata,
        'operation': operation,
        'outputs': outputs,
        'inputs': inputs,
        'version': version,
        'id': None,
    }

    message = json.dumps(
        handcrafted_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3.sha3_256(message.encode())

    ed25519.sign(message.digest(), base58.b58decode(alice.private_key))

    fulfillment_uri = ed25519.serialize_uri()

    handcrafted_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    json_str_tx = json.dumps(
    handcrafted_creation_tx,
    sort_keys=True,
    separators=(',', ':'),
    ensure_ascii=False,
    )

    creation_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    handcrafted_creation_tx['id'] = creation_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_creation_tx = bdb.transactions.send(handcrafted_creation_tx, mode='sync')

A quick check:

.. code-block:: python

    >>> json.dumps(returned_creation_tx, sort_keys=True) == json.dumps(handcrafted_creation_tx, sort_keys=True)
    True


.. _bicycle-asset-transfer-revisited:

********************************
Bicycle Asset Transfer Revisited
********************************
In the :ref:`bicycle transfer example <bicycle-transfer>` , we showed that the
transfer transaction was prepared and fulfilled as follows:

.. ipython::

    In [0]: from bigchaindb_driver import BigchainDB

    In [0]: from bigchaindb_driver.offchain import fulfill_transaction, prepare_transaction

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: alice, bob = generate_keypair(), generate_keypair()

    In [0]: bdb = BigchainDB('https://example.com:9984') # Use YOUR BigchainDB Root URL here

    In [0]: bicycle_asset = {
       ...:     'data': {
       ...:          'bicycle': {
       ...:               'serial_number': 'abcd1234',
       ...:               'manufacturer': 'bkfab'
       ...:          },
       ...:     },
       ...: }

    In [0]: bicycle_asset_metadata = {
       ...:     'planet': 'earth'
       ...: }

    In [0]: prepared_creation_tx = bdb.transactions.prepare(
       ...:     operation='CREATE',
       ...:     signers=alice.public_key,
       ...:     asset=bicycle_asset,
       ...:     metadata=bicycle_asset_metadata
       ...: )

    In [0]: fulfilled_creation_tx = bdb.transactions.fulfill(
       ...:     prepared_creation_tx,
       ...:     private_keys=alice.private_key
       ...: )

    In [0]: creation_tx = fulfilled_creation_tx

    In [0]: output_index = 0

    In [0]: output = creation_tx['outputs'][output_index]

    In [0]: transfer_input = {
       ...:     'fulfillment': output['condition']['details'],
       ...:     'fulfills': {
       ...:          'output_index': output_index,
       ...:          'transaction_id': creation_tx['id'],
       ...:     },
       ...:     'owners_before': output['public_keys'],
       ...: }

    In [0]: transfer_asset = {
       ...:     'id': creation_tx['id'],
       ...: }

    In [0]: prepared_transfer_tx = prepare_transaction(
       ...:     operation='TRANSFER',
       ...:     asset=transfer_asset,
       ...:     inputs=transfer_input,
       ...:     recipients=bob.public_key,
       ...: )

    In [0]: fulfilled_transfer_tx = fulfill_transaction(
       ...:     prepared_transfer_tx,
       ...:     private_keys=alice.private_key,
       ...: )

    In [0]: fulfilled_transfer_tx

Our goal is now to handcraft a payload equal to ``fulfilled_transfer_tx`` with
the help of

* :mod:`json`: to serialize the transaction dictionary into a JSON formatted
  string.
* `sha3`_: to hash the serialized transaction
* `cryptoconditions`_: to create conditions and fulfillments

The Prepared Transaction
========================

version
-------
.. ipython::

    In [0]: version = '2.0'

asset
-----
The asset payload for ``TRANSFER`` transaction is a ``dict`` with only the
asset id (i.e. the id of the ``CREATE`` transaction for the asset):

.. ipython::

    In [0]: asset = {'id': creation_tx['id']}

metadata
--------
.. ipython::

    In [0]: metadata = None

operation
---------
.. ipython::

    In [0]: operation = 'TRANSFER'

outputs
-------
.. ipython::

    In [0]: from cryptoconditions import Ed25519Sha256

    In [0]: import base58

    In [0]: ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    In [0]: output = {
       ...:     'amount': '1',
       ...:     'condition': {
       ...:         'details': {
       ...:             'type': ed25519.TYPE_NAME,
       ...:             'public_key': base58.b58encode(ed25519.public_key),
       ...:         },
       ...:         'uri': ed25519.condition_uri,
       ...:     },
       ...:     'public_keys': (bob.public_key,),
       ...: }

    In [0]: outputs = (output,)

fulfillments
------------
.. ipython::

    In [0]: input_ = {
       ...:     'fulfillment': None,
       ...:     'fulfills': {
       ...:         'transaction_id': creation_tx['id'],
       ...:         'output_index': 0,
       ...:     },
       ...:     'owners_before': (alice.public_key,)
       ...: }

    In [0]: inputs = (input_,)

A few notes:

* The ``fulfills`` field points to the condition (in a transaction) that needs
  to be fulfilled;
* The ``'fulfillment'`` value is ``None`` as it will be set during the
  fulfillment step; and
* The ``'owners_before'`` field identifies the fulfiller(s).

Putting it all together:

.. ipython::

    In [0]: handcrafted_transfer_tx = {
       ...:     'asset': asset,
       ...:     'metadata': metadata,
       ...:     'operation': operation,
       ...:     'outputs': outputs,
       ...:     'inputs': inputs,
       ...:     'version': version,
       ...:     'id': None,
       ...: }

    In [0]: handcrafted_transfer_tx

Note how ``handcrafted_creation_tx`` includes a key-value pair ``'id': None``. The ‘id’ value is None as it will be set during the fulfillment step.

You may observe that

.. ipython::

    In [0]: handcrafted_transfer_tx == prepared_transfer_tx

.. ipython::

    In [0]: from copy import deepcopy

    In [0]: # back up

    In [0]: prepared_transfer_tx_bk = deepcopy(prepared_transfer_tx)

    In [0]: # set fulfillment to None

    In [0]: prepared_transfer_tx['inputs'][0]['fulfillment'] = None

    In [0]: handcrafted_transfer_tx == prepared_transfer_tx

Are still not equal because we used tuples instead of lists.

.. ipython::

    In [0]: # serialize to json str

    In [0]: import json

    In [0]: json_str_handcrafted_tx = json.dumps(handcrafted_transfer_tx, sort_keys=True)

    In [0]: json_str_prepared_tx = json.dumps(prepared_transfer_tx, sort_keys=True)

.. ipython::

    In [0]: json_str_handcrafted_tx == json_str_prepared_tx

    In [0]: prepared_transfer_tx = prepared_transfer_tx_bk

Up to now
---------

Let's recap how we got here:

.. code-block:: python

    from cryptoconditions import Ed25519Sha256
    from bigchaindb_driver.crypto import CryptoKeypair
    import base58

    bob = CryptoKeypair(
        public_key=bob.public_key,
        private_key=bob.private_key,
    )

    operation = 'TRANSFER'
    version = '2.0'
    asset = {'id': handcrafted_creation_tx['id']}
    metadata = None

    ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    output = {
        'amount': '1',
        'condition': {
            'details': {
                'type': ed25519.TYPE_NAME,
                'public_key': base58.b58encode(ed25519.public_key),
            },
            'uri': ed25519.condition_uri,
        },
        'public_keys': (bob.public_key,),
    }
    outputs = (output,)

    input_ = {
        'fulfillment': None,
        'fulfills': {
            'transaction_id': handcrafted_creation_tx['id'],
            'output_index': 0,
        },
        'owners_before': (alice.public_key,)
    }
    inputs = (input_,)

    handcrafted_transfer_tx = {
        'asset': asset,
        'metadata': metadata,
        'operation': operation,
        'outputs': outputs,
        'inputs': inputs,
        'version': version,
        'id': None,
    }


The Fulfilled Transaction
=========================

.. ipython::

    In [0]: from bigchaindb_driver.offchain import fulfill_transaction

    In [0]: from sha3 import sha3_256

    In [0]: # fulfill prepared transaction

    In [0]: fulfilled_transfer_tx = fulfill_transaction(
       ...:     prepared_transfer_tx,
       ...:     private_keys=alice.private_key,
       ...: )

    In [0]: # fulfill handcrafted transaction (with our previously built ED25519 fulfillment)

    In [0]: ed25519.to_dict()

    In [0]: message = json.dumps(
       ...:     handcrafted_transfer_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: message = sha3_256(message.encode())

    In [0]: message.update('{}{}'.format(
       ...:     handcrafted_transfer_tx['inputs'][0]['fulfills']['transaction_id'],
       ...:     handcrafted_transfer_tx['inputs'][0]['fulfills']['output_index']).encode()
       ...: )

    In [0]: ed25519.sign(message.digest(), base58.b58decode(alice.private_key))

    In [0]: fulfillment_uri = ed25519.serialize_uri()

    In [0]: handcrafted_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

id
--

.. ipython::

    In [0]: import json

    In [0]: from sha3 import sha3_256

    In [0]: json_str_tx = json.dumps(
       ...:     handcrafted_transfer_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: transfer_txid = sha3_256(json_str_tx.encode()).hexdigest()

    In [0]: handcrafted_transfer_tx['id'] = transfer_txid

Compare this to the txid of the transaction generated via
``prepare_transaction()``

.. ipython::

    In [0]: transfer_txid == fulfilled_transfer_tx['id']

Let's check this:

.. ipython::

    In [0]: fulfilled_transfer_tx['inputs'][0]['fulfillment'] == fulfillment_uri

    In [0]: json.dumps(fulfilled_transfer_tx, sort_keys=True) == json.dumps(handcrafted_transfer_tx, sort_keys=True)


In a nutshell
=============

.. code-block:: python

    import json

    import base58
    import sha3
    from cryptoconditions import Ed25519Sha256

    from bigchaindb_driver.crypto import generate_keypair

    bob = generate_keypair()

    operation = 'TRANSFER'
    version = '2.0'
    asset = {'id': handcrafted_creation_tx['id']}
    metadata = None

    ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    output = {
        'amount': '1',
        'condition': {
            'details': {
                'type': ed25519.TYPE_NAME,
                'public_key': base58.b58encode(ed25519.public_key),
            },
            'uri': ed25519.condition_uri,
        },
        'public_keys': (bob.public_key,),
    }
    outputs = (output,)

    input_ = {
        'fulfillment': None,
        'fulfills': {
            'transaction_id': handcrafted_creation_tx['id'],
            'output_index': 0,
        },
        'owners_before': (alice.public_key,)
    }
    inputs = (input_,)

    handcrafted_transfer_tx = {
        'asset': asset,
        'metadata': metadata,
        'operation': operation,
        'outputs': outputs,
        'inputs': inputs,
        'version': version,
        'id': None,
    }

    message = json.dumps(
        handcrafted_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3.sha3_256(message.encode())

    message.update('{}{}'.format(
        handcrafted_transfer_tx['inputs'][0]['fulfills']['transaction_id'],
        handcrafted_transfer_tx['inputs'][0]['fulfills']['output_index']).encode()
    )

    ed25519.sign(message.digest(), base58.b58decode(alice.private_key))

    fulfillment_uri = ed25519.serialize_uri()

    handcrafted_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    json_str_tx = json.dumps(
        handcrafted_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    transfer_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    handcrafted_transfer_tx['id'] = transfer_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_transfer_tx = bdb.transactions.send(handcrafted_transfer_tx, mode='sync')

A quick check:

.. code-block:: python

    >>> json.dumps(returned_transfer_tx, sort_keys=True) == json.dumps(handcrafted_transfer_tx, sort_keys=True)
    True


*************************
Bicycle Sharing Revisited
*************************

Handcrafting the ``CREATE`` transaction for our :ref:`bicycle sharing example
<bicycle-divisible-assets>`:

.. code-block:: python

    import json

    import base58
    import sha3
    from cryptoconditions import Ed25519Sha256

    from bigchaindb_driver.crypto import generate_keypair


    bob, carly = generate_keypair(), generate_keypair()
    version = '2.0'

    bicycle_token = {
        'data': {
            'token_for': {
                'bicycle': {
                    'serial_number': 'abcd1234',
                    'manufacturer': 'bkfab'
                }
            },
            'description': 'Time share token. Each token equals one hour of riding.',
        },
    }

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for carly
    ed25519 = Ed25519Sha256(public_key=base58.b58decode(carly.public_key))

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri = ed25519.condition.serialize_uri()

    # CRYPTO-CONDITIONS: construct an unsigned fulfillment dictionary
    unsigned_fulfillment_dict = {
        'type': ed25519.TYPE_NAME,
        'public_key': base58.b58encode(ed25519.public_key),
    }

    output = {
        'amount': '10',
        'condition': {
            'details': unsigned_fulfillment_dict,
            'uri': condition_uri,
        },
        'public_keys': (carly.public_key,),
    }

    input_ = {
        'fulfillment': None,
        'fulfills': None,
        'owners_before': (bob.public_key,)
    }

    token_creation_tx = {
        'operation': 'CREATE',
        'asset': bicycle_token,
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
        'id': None,
    }

    # JSON: serialize the transaction-without-id to a json formatted string
    message = json.dumps(
        token_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3.sha3_256(message.encode())

    # CRYPTO-CONDITIONS: sign the serialized transaction-without-id
    ed25519.sign(message.digest(), base58.b58decode(bob.private_key))

    # CRYPTO-CONDITIONS: generate the fulfillment uri
    fulfillment_uri = ed25519.serialize_uri()

    # add the fulfillment uri (signature)
    token_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    # JSON: serialize the id-less transaction to a json formatted string
    json_str_tx = json.dumps(
        token_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # SHA3: hash the serialized id-less transaction to generate the id
    shared_creation_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    # add the id
    token_creation_tx['id'] = shared_creation_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_creation_tx = bdb.transactions.send(token_creation_tx, mode='sync')

A few checks:

.. code-block:: python

    >>> json.dumps(returned_creation_tx, sort_keys=True) == json.dumps(token_creation_tx, sort_keys=True)
    True

    >>> token_creation_tx['inputs'][0]['owners_before'][0] == bob.public_key
    True

    >>> token_creation_tx['outputs'][0]['public_keys'][0] == carly.public_key
    True

    >>> token_creation_tx['outputs'][0]['amount'] == '10'
    True


Now Carly wants to ride the bicycle for 2 hours so she needs to send 2 tokens
to Bob:

.. code-block:: python

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for carly
    bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for carly
    carly_ed25519 = Ed25519Sha256(public_key=base58.b58decode(carly.public_key))

    # CRYPTO-CONDITIONS: generate the condition uris
    bob_condition_uri = bob_ed25519.condition.serialize_uri()
    carly_condition_uri = carly_ed25519.condition.serialize_uri()

    # CRYPTO-CONDITIONS: get the unsigned fulfillment dictionary (details)
    bob_unsigned_fulfillment_dict = {
        'type': bob_ed25519.TYPE_NAME,
        'public_key': base58.b58encode(bob_ed25519.public_key),
    }

    carly_unsigned_fulfillment_dict = {
        'type': carly_ed25519.TYPE_NAME,
        'public_key': base58.b58encode(carly_ed25519.public_key),
    }

    bob_output = {
        'amount': '2',
        'condition': {
            'details': bob_unsigned_fulfillment_dict,
            'uri': bob_condition_uri,
        },
        'public_keys': (bob.public_key,),
    }

    carly_output = {
        'amount': '8',
        'condition': {
            'details': carly_unsigned_fulfillment_dict,
            'uri': carly_condition_uri,
        },
        'public_keys': (carly.public_key,),
    }

    input_ = {
        'fulfillment': None,
        'fulfills': {
            'transaction_id': token_creation_tx['id'],
            'output_index': 0,
        },
        'owners_before': (carly.public_key,)
    }

    token_transfer_tx = {
        'operation': 'TRANSFER',
        'asset': {'id': token_creation_tx['id']},
        'metadata': None,
        'outputs': (bob_output, carly_output),
        'inputs': (input_,),
        'version': version,
        'id': None,
    }

    # JSON: serialize the transaction-without-id to a json formatted string
    message = json.dumps(
        token_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3.sha3_256(message.encode())

    message.update('{}{}'.format(
        token_transfer_tx['inputs'][0]['fulfills']['transaction_id'],
        token_transfer_tx['inputs'][0]['fulfills']['output_index']).encode()
    )

    # CRYPTO-CONDITIONS: sign the serialized transaction-without-id for bob
    carly_ed25519.sign(message.digest(), base58.b58decode(carly.private_key))

    # CRYPTO-CONDITIONS: generate bob's fulfillment uri
    fulfillment_uri = carly_ed25519.serialize_uri()

    # add bob's fulfillment uri (signature)
    token_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    # JSON: serialize the id-less transaction to a json formatted string
    json_str_tx = json.dumps(
        token_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # SHA3: hash the serialized id-less transaction to generate the id
    shared_transfer_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    # add the id
    token_transfer_tx['id'] = shared_transfer_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_transfer_tx = bdb.transactions.send(token_transfer_tx, mode='sync')

A few checks:

.. code-block:: python

    >>> json.dumps(returned_transfer_tx, sort_keys=True) == json.dumps(token_transfer_tx, sort_keys=True)
    True

    >>> token_transfer_tx['inputs'][0]['owners_before'][0] == carly.public_key
    True


*************************
Multiple Owners Revisited
*************************

Walkthrough
===========

We'll re-use the :ref:`example of Alice and Bob owning a car together
<car-multiple-owners>` to handcraft transactions with multiple owners.

Create test user: alice and bob

.. ipython::

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: alice, bob = generate_keypair(), generate_keypair()

Say ``alice`` and ``bob`` own a car together:

.. ipython::

    In [0]: from bigchaindb_driver import offchain

    In [0]: from bigchaindb_driver import BigchainDB

    In [0]: bdb_root_url = 'https://example.com:9984' # Use YOUR BigchainDB Root URL here

    In [0]: bdb = BigchainDB(bdb_root_url)

    In [0]: car_asset = {'data': {'car': {'vin': '5YJRE11B781000196'}}}

    In [0]: car_creation_tx = offchain.prepare_transaction(
       ...:     operation='CREATE',
       ...:     signers=alice.public_key,
       ...:     recipients=(alice.public_key, bob.public_key),
       ...:     asset=car_asset,
       ...: )

    In [0]: signed_car_creation_tx = offchain.fulfill_transaction(
       ...:     car_creation_tx,
       ...:     private_keys=alice.private_key,
       ...: )

    In [0]: signed_car_creation_tx

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    sent_car_tx = bdb.transactions.send(signed_car_creation_tx, mode='sync')

One day, ``alice`` and ``bob``, having figured out how to teleport themselves,
and realizing they no longer need their car, wish to transfer the ownership of
their car over to ``carol``:

.. ipython::

    In [0]: carol = generate_keypair()

    In [0]: output_index = 0

    In [0]: output = signed_car_creation_tx['outputs'][output_index]

    In [0]: input_ = {
       ...:     'fulfillment': output['condition']['details'],
       ...:     'fulfills': {
       ...:         'output_index': output_index,
       ...:         'transaction_id': signed_car_creation_tx['id'],
       ...:     },
       ...:     'owners_before': output['public_keys'],
       ...: }

    In [0]: asset = signed_car_creation_tx['id']

    In [0]: car_transfer_tx = offchain.prepare_transaction(
       ...:     operation='TRANSFER',
       ...:     recipients=carol.public_key,
       ...:     asset={'id': asset},
       ...:     inputs=input_,
       ...: )

    In [0]: signed_car_transfer_tx = offchain.fulfill_transaction(
       ...:     car_transfer_tx, private_keys=[alice.private_key, bob.private_key]
       ...: )

    In [0]: signed_car_transfer_tx

.. code-block:: python

    sent_car_transfer_tx = bdb.transactions.send(signed_car_transfer_tx, mode='sync')

Doing this manually
-------------------

In order to do this manually, let's first import the necessary tools (json,
sha3, and cryptoconditions):

.. ipython::

    In [0]: import json

    In [0]: import base58

    In [0]: from sha3 import sha3_256

    In [0]: from cryptoconditions import Ed25519Sha256, ThresholdSha256

Create the asset, setting all values:

.. ipython::

    In [0]: car_asset = {
       ...:     'data': {
       ...:         'car': {
       ...:             'vin': '5YJRE11B781000196',
       ...:         },
       ...:     },
       ...: }

Generate the output condition:

.. ipython::

    In [0]: alice_ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    In [0]: bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    In [0]: threshold_sha256 = ThresholdSha256(threshold=2)

    In [0]: threshold_sha256.add_subfulfillment(alice_ed25519)

    In [0]: threshold_sha256.add_subfulfillment(bob_ed25519)

    In [0]: condition_uri = threshold_sha256.condition.serialize_uri()

    In [0]: condition_details = {
       ...:     'subconditions': [
       ...:         {'type': s['body'].TYPE_NAME,
       ...:          'public_key': base58.b58encode(s['body'].public_key)}
       ...:         for s in threshold_sha256.subconditions
       ...:         if (s['type'] == 'fulfillment' and
       ...:             s['body'].TYPE_NAME == 'ed25519-sha-256')
       ...:      ],
       ...:     'threshold': threshold_sha256.threshold,
       ...:     'type': threshold_sha256.TYPE_NAME,
       ...: }

    In [0]: output = {
       ...:     'amount': '1',
       ...:     'condition': {
       ...:         'details': condition_details,
       ...:         'uri': condition_uri,
       ...:     },
       ...:     'public_keys': (alice.public_key, bob.public_key),
       ...: }

.. tip:: The condition ``uri`` could have been generated in a slightly
    different way, which may be more intuitive to you. You can think of the
    threshold condition containing sub conditions:

    .. ipython::

        In [0]: alt_threshold_sha256 = ThresholdSha256(threshold=2)

        In [0]: alt_threshold_sha256.add_subcondition(alice_ed25519.condition)

        In [0]: alt_threshold_sha256.add_subcondition(bob_ed25519.condition)

        In [0]: alt_threshold_sha256.condition.serialize_uri() == condition_uri

    The ``details`` on the other hand hold the associated fulfillments not yet
    fulfilled.

The yet to be fulfilled input:

.. ipython::

    In [0]: input_ = {
       ...:     'fulfillment': None,
       ...:     'fulfills': None,
       ...:     'owners_before': (alice.public_key,),
       ...: }

Craft the payload:

.. ipython::

    In [0]: version = '2.0'

    In [0]: handcrafted_car_creation_tx = {
       ...:     'operation': 'CREATE',
       ...:     'asset': car_asset,
       ...:     'metadata': None,
       ...:     'outputs': (output,),
       ...:     'inputs': (input_,),
       ...:     'version': version,
       ...:     'id': None,
       ...: }

Sign the transaction:

.. ipython::

    In [0]: message = json.dumps(
       ...:     handcrafted_car_creation_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: alice_ed25519.sign(message.encode(), base58.b58decode(alice.private_key))

    In [0]: fulfillment_uri = alice_ed25519.serialize_uri()

    In [0]: handcrafted_car_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Generate the id, by hashing the encoded json formatted string representation of
the transaction:

.. ipython::

    In [0]: json_str_tx = json.dumps(
       ...:     handcrafted_car_creation_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: car_creation_txid = sha3_256(json_str_tx.encode()).hexdigest()

    In [0]: handcrafted_car_creation_tx['id'] = car_creation_txid

Let's make sure our txid is the same as the one provided by the driver:

.. ipython::

    In [0]: handcrafted_car_creation_tx['id'] == signed_car_creation_tx['id']

Compare our ``CREATE`` transaction with the driver's:

.. ipython::

    In [0]: (json.dumps(handcrafted_car_creation_tx, sort_keys=True) ==
       ...:  json.dumps(signed_car_creation_tx, sort_keys=True))

The transfer to Carol:

.. ipython::

    In [0]: alice_ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    In [0]: bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    In [0]: carol_ed25519 = Ed25519Sha256(public_key=base58.b58decode(carol.public_key))

    In [0]: unsigned_fulfillments_dict = {
       ...:     'type': carol_ed25519.TYPE_NAME,
       ...:     'public_key': base58.b58encode(carol_ed25519.public_key),
       ...: }

    In [0]: condition_uri = carol_ed25519.condition.serialize_uri()

    In [0]: output = {
       ...:     'amount': '1',
       ...:     'condition': {
       ...:         'details': unsigned_fulfillments_dict,
       ...:         'uri': condition_uri,
       ...:     },
       ...:     'public_keys': (carol.public_key,),
       ...: }

The yet to be fulfilled input:

.. ipython::

    In [0]: input_ = {
       ...:     'fulfillment': None,
       ...:     'fulfills': {
       ...:         'transaction_id': handcrafted_car_creation_tx['id'],
       ...:         'output_index': 0,
       ...:     },
       ...:     'owners_before': (alice.public_key, bob.public_key),
       ...: }

Craft the payload:

.. ipython::

    In [0]: handcrafted_car_transfer_tx = {
       ...:     'operation': 'TRANSFER',
       ...:     'asset': {'id': handcrafted_car_creation_tx['id']},
       ...:     'metadata': None,
       ...:     'outputs': (output,),
       ...:     'inputs': (input_,),
       ...:     'version': version,
       ...:     'id': None,
       ...: }

Sign the transaction:

.. ipython::

    In [0]: message = json.dumps(
       ...:     handcrafted_car_transfer_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: threshold_sha256 = ThresholdSha256(threshold=2)

    In [0]: alice_ed25519.sign(message=message.encode(),
       ...:     private_key=base58.b58decode(alice.private_key))

    In [0]: bob_ed25519.sign(message=message.encode(),
       ...:     private_key=base58.b58decode(bob.private_key))

    In [0]: threshold_sha256.add_subfulfillment(alice_ed25519)

    In [0]: threshold_sha256.add_subfulfillment(bob_ed25519)

    In [0]: fulfillment_uri = threshold_sha256.serialize_uri()

    In [0]: handcrafted_car_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Generate the id, by hashing the encoded json formatted string representation of
the transaction:

.. ipython::

    In [0]: json_str_tx = json.dumps(
       ...:     handcrafted_car_transfer_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: car_transfer_txid = sha3_256(json_str_tx.encode()).hexdigest()

    In [0]: handcrafted_car_transfer_tx['id'] = car_transfer_txid

Let's make sure our txid is the same as the one provided by the driver:

.. ipython::

    In [0]: handcrafted_car_transfer_tx['id'] == signed_car_transfer_tx['id']

Compare our ``TRANSFER`` transaction with the driver's:

.. ipython::

    In [0]: (json.dumps(handcrafted_car_transfer_tx, sort_keys=True) ==
       ...:  json.dumps(signed_car_transfer_tx, sort_keys=True))

In a nutshell
=============

Handcrafting the ``'CREATE'`` transaction
-----------------------------------------

.. code-block:: python

    import json

    import base58
    from sha3 import sha3_256
    from cryptoconditions import Ed25519Sha256, ThresholdSha256

    from bigchaindb_driver.crypto import generate_keypair

    version = '2.0'

    car_asset = {
        'data': {
            'car': {
                'vin': '5YJRE11B781000196',
            },
        },
    }

    alice, bob = generate_keypair(), generate_keypair()

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for alice
    alice_ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for bob
    bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    # CRYPTO-CONDITIONS: instantiate a threshold SHA 256 crypto-condition
    threshold_sha256 = ThresholdSha256(threshold=2)

    # CRYPTO-CONDITIONS: add alice ed25519 to the threshold SHA 256 condition
    threshold_sha256.add_subfulfillment(alice_ed25519)

    # CRYPTO-CONDITIONS: add bob ed25519 to the threshold SHA 256 condition
    threshold_sha256.add_subfulfillment(bob_ed25519)

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri = threshold_sha256.condition.serialize_uri()

    # CRYPTO-CONDITIONS: get the unsigned fulfillment dictionary (details)
    condition_details = {
        'subconditions': [
            {'type': s['body'].TYPE_NAME,
             'public_key': base58.b58encode(s['body'].public_key)}
            for s in threshold_sha256.subconditions
            if (s['type'] == 'fulfillment' and
                s['body'].TYPE_NAME == 'ed25519-sha-256')
        ],
        'threshold': threshold_sha256.threshold,
        'type': threshold_sha256.TYPE_NAME,
    }

    output = {
        'amount': '1',
        'condition': {
            'details': condition_details,
            'uri': condition_uri,
        },
        'public_keys': (alice.public_key, bob.public_key),
    }

    # The yet to be fulfilled input:
    input_ = {
        'fulfillment': None,
        'fulfills': None,
        'owners_before': (alice.public_key,),
    }

    # Craft the payload:
    handcrafted_car_creation_tx = {
        'operation': 'CREATE',
        'asset': car_asset,
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
        'id': None,
    }

    # JSON: serialize the transaction-without-id to a json formatted string
    message = json.dumps(
        handcrafted_car_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    message = sha3_256(message.encode())

    # CRYPTO-CONDITIONS: sign the serialized transaction-without-id
    alice_ed25519.sign(message.digest(), base58.b58decode(alice.private_key))

    # CRYPTO-CONDITIONS: generate the fulfillment uri
    fulfillment_uri = alice_ed25519.serialize_uri()

    # add the fulfillment uri (signature)
    handcrafted_car_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    # JSON: serialize the id-less transaction to a json formatted string
    # Generate the id, by hashing the encoded json formatted string representation of
    # the transaction:
    json_str_tx = json.dumps(
        handcrafted_car_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # SHA3: hash the serialized id-less transaction to generate the id
    car_creation_txid = sha3_256(json_str_tx.encode()).hexdigest()

    # add the id
    handcrafted_car_creation_tx['id'] = car_creation_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_car_creation_tx = bdb.transactions.send(handcrafted_car_creation_tx, mode='sync')


Handcrafting the ``'TRANSFER'`` transaction
-------------------------------------------

.. code-block:: python

    carol = generate_keypair()

    alice_ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    carol_ed25519 = Ed25519Sha256(public_key=base58.b58decode(carol.public_key))

    unsigned_fulfillments_dict = {
        'type': carol_ed25519.TYPE_NAME,
        'public_key': base58.b58encode(carol_ed25519.public_key),
    }

    condition_uri = carol_ed25519.condition.serialize_uri()

    output = {
        'amount': '1',
        'condition': {
            'details': unsigned_fulfillments_dict,
            'uri': condition_uri,
        },
        'public_keys': (carol.public_key,),
    }

    # The yet to be fulfilled input:
    input_ = {
        'fulfillment': None,
        'fulfills': {
            'transaction_id': handcrafted_car_creation_tx['id'],
            'output_index': 0,
        },
        'owners_before': (alice.public_key, bob.public_key),
    }

    # Craft the payload:
    handcrafted_car_transfer_tx = {
        'operation': 'TRANSFER',
        'asset': {'id': handcrafted_car_creation_tx['id']},
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
        'id': None,
    }

    # Sign the transaction:
    message = json.dumps(
        handcrafted_car_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3_256(message.encode())

    message.update('{}{}'.format(
        handcrafted_car_transfer_tx['inputs'][0]['fulfills']['transaction_id'],
        handcrafted_car_transfer_tx['inputs'][0]['fulfills']['output_index']).encode()
    )

    threshold_sha256 = ThresholdSha256(threshold=2)

    alice_ed25519.sign(message=message.digest(),
                       private_key=base58.b58decode(alice.private_key))
    bob_ed25519.sign(message=message.digest(),
                     private_key=base58.b58decode(bob.private_key))

    threshold_sha256.add_subfulfillment(alice_ed25519)

    threshold_sha256.add_subfulfillment(bob_ed25519)

    fulfillment_uri = threshold_sha256.serialize_uri()

    handcrafted_car_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    # Generate the id, by hashing the encoded json formatted string
    # representation of the transaction:
    json_str_tx = json.dumps(
        handcrafted_car_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    car_transfer_txid = sha3_256(json_str_tx.encode()).hexdigest()

    handcrafted_car_transfer_tx['id'] = car_transfer_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    bdb = BigchainDB('http://bdb-server:9984')
    returned_car_transfer_tx = bdb.transactions.send(handcrafted_car_transfer_tx, mode='sync')


**************************************
Multiple Owners with m-of-n Signatures
**************************************
In this example, ``alice`` and ``bob`` co-own a car asset such that only one
of them is required to sign the transfer transaction. The example is very
similar to the one where both owners are required to sign, but with minor
differences that are very important, in order to make the fulfillment URI
valid.

We only show the "nutshell" version for now. The example is self-contained.

In a nutshell
=============

Handcrafting the ``'CREATE'`` transaction
-----------------------------------------

.. code-block:: python

    import json

    import base58
    import sha3
    from cryptoconditions import Ed25519Sha256, ThresholdSha256

    from bigchaindb_driver.crypto import generate_keypair


    version = '2.0'

    car_asset = {
        'data': {
            'car': {
                'vin': '5YJRE11B781000196',
            },
        },
    }

    alice, bob = generate_keypair(), generate_keypair()

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for alice
    alice_ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for bob
    bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    # CRYPTO-CONDITIONS: instantiate a threshold SHA 256 crypto-condition
    # NOTICE that the threshold is set to 1, not 2
    threshold_sha256 = ThresholdSha256(threshold=1)

    # CRYPTO-CONDITIONS: add alice ed25519 to the threshold SHA 256 condition
    threshold_sha256.add_subfulfillment(alice_ed25519)

    # CRYPTO-CONDITIONS: add bob ed25519 to the threshold SHA 256 condition
    threshold_sha256.add_subfulfillment(bob_ed25519)

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri = threshold_sha256.condition.serialize_uri()

    # CRYPTO-CONDITIONS: get the unsigned fulfillment dictionary (details)
    condition_details = {
        'subconditions': [
            {'type': s['body'].TYPE_NAME,
             'public_key': base58.b58encode(s['body'].public_key)}
            for s in threshold_sha256.subconditions
            if (s['type'] == 'fulfillment' and
                s['body'].TYPE_NAME == 'ed25519-sha-256')
        ],
        'threshold': threshold_sha256.threshold,
        'type': threshold_sha256.TYPE_NAME,
    }

    output = {
        'amount': '1',
        'condition': {
            'details': condition_details,
            'uri': condition_uri,
        },
        'public_keys': (alice.public_key, bob.public_key),
    }

    # The yet to be fulfilled input:
    input_ = {
        'fulfillment': None,
        'fulfills': None,
        'owners_before': (alice.public_key,),
    }

    # Craft the payload:
    handcrafted_car_creation_tx = {
        'operation': 'CREATE',
        'asset': car_asset,
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
        'id': None,
    }

    # JSON: serialize the transaction-without-id to a json formatted string
    message = json.dumps(
        handcrafted_car_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3.sha3_256(message.encode())

    # CRYPTO-CONDITIONS: sign the serialized transaction-without-id
    alice_ed25519.sign(message.digest(), base58.b58decode(alice.private_key))

    # CRYPTO-CONDITIONS: generate the fulfillment uri
    fulfillment_uri = alice_ed25519.serialize_uri()

    # add the fulfillment uri (signature)
    handcrafted_car_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    # JSON: serialize the id-less transaction to a json formatted string
    # Generate the id, by hashing the encoded json formatted string representation of
    # the transaction:
    json_str_tx = json.dumps(
        handcrafted_car_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # SHA3: hash the serialized id-less transaction to generate the id
    car_creation_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    # add the id
    handcrafted_car_creation_tx['id'] = car_creation_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_car_creation_tx = bdb.transactions.send(handcrafted_car_creation_tx, mode='sync')



Handcrafting the ``'TRANSFER'`` transaction
-------------------------------------------

.. code-block:: python

    version = '2.0'

    carol = generate_keypair()

    alice_ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice.public_key))

    bob_ed25519 = Ed25519Sha256(public_key=base58.b58decode(bob.public_key))

    carol_ed25519 = Ed25519Sha256(public_key=base58.b58decode(carol.public_key))

    condition_uri = carol_ed25519.condition.serialize_uri()

    output = {
        'amount': '1',
        'condition': {
            'details': {
                'type': carol_ed25519.TYPE_NAME,
                'public_key': base58.b58encode(carol_ed25519.public_key),
            },
            'uri': condition_uri,
        },
        'public_keys': (carol.public_key,),
    }

    # The yet to be fulfilled input:
    input_ = {
        'fulfillment': None,
        'fulfills': {
            'transaction_id': handcrafted_car_creation_tx['id'],
            'output_index': 0,
        },
        'owners_before': (alice.public_key, bob.public_key),
    }

    # Craft the payload:
    handcrafted_car_transfer_tx = {
        'operation': 'TRANSFER',
        'asset': {'id': handcrafted_car_creation_tx['id']},
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
        'id': None,
    }

    # Sign the transaction:
    message = json.dumps(
        handcrafted_car_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    message = sha3.sha3_256(message.encode())

    message.update('{}{}'.format(
        handcrafted_car_transfer_tx['inputs'][0]['fulfills']['transaction_id'],
        handcrafted_car_transfer_tx['inputs'][0]['fulfills']['output_index']).encode())

    threshold_sha256 = ThresholdSha256(threshold=1)

    alice_ed25519.sign(message.digest(),
                       private_key=base58.b58decode(alice.private_key))

    threshold_sha256.add_subfulfillment(alice_ed25519)

    threshold_sha256.add_subcondition(bob_ed25519.condition)

    fulfillment_uri = threshold_sha256.serialize_uri()

    handcrafted_car_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

    # Generate the id, by hashing the encoded json formatted string
    # representation of the transaction:
    json_str_tx = json.dumps(
        handcrafted_car_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    car_transfer_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    handcrafted_car_transfer_tx['id'] = car_transfer_txid

To send it over to BigchainDB we have different options. A `mode` parameter can be used to change the broadcasting API
used in `Tendermint <http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api>`_.
By setting the mode, a new transaction can be pushed with a different mode than the default. The default mode is
``async``, which will return immediately and not wait to see if the transaction is valid. The ``sync`` mode will return
after the transaction is validated, while ``commit`` returns after the transaction is committed to a block.

.. code-block:: python

    bdb = BigchainDB('http://bdb-server:9984')
    returned_car_transfer_tx = bdb.transactions.send(handcrafted_car_transfer_tx, mode='sync')


.. _sha3: https://github.com/tiran/pysha3
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
.. _cryptoconditions internet draft: https://tools.ietf.org/html/draft-thomas-crypto-conditions-02
.. _The Transaction Model: https://docs.bigchaindb.com/projects/server/en/latest/data-models/transaction-model.html
.. _The Transaction Schema: https://docs.bigchaindb.com/projects/server/en/latest/schema/transaction.html
.. _blog post: https://blog.bigchaindb.com/three-transaction-model-changes-in-the-next-release-dadbac50094a
