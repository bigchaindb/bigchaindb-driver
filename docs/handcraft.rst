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

For convenience's sake, some utilites are provided to prepare and fulfill a
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


High-level view of a transaction in Python
==========================================
For detailled documentation on the transaction schema, please consult
`The Transaction Model`_ and `The Transaction Schema`_.

From the point of view of Python, a transaction is simply a dictionary:

.. code-block:: python

    {
        'id': 'c10671ba9b1d3be3cb68959416bf88a711a4eeff2dbe29f5aca13e8dc39579ff',
        'operation': 'CREATE',
        'asset': {
            'data': {
                'bicycle': {
                    'manufacturer': 'bkfab',
                    'serial_number': 'abcd1234',
                },
            },
        },
        'metadata': {'planet': 'earth'},
        'outputs': [{
            'amount': 1,
            'condition': {
                'details': {
                    'bitmask': 32,
                    'public_key': '6FCKbDMmCiM37pN9qzNmgJxKqebWzGxZUcAqB8CNg84J',
                    'signature': None,
                    'type': 'fulfillment',
                    'type_id': 4,
                },
                'uri': 'cc:4:20:Te1duSG0oFpsm-5Sn9uQT1QIngxmhZSOEry8xeCna8M:96',
            },
            'public_keys': ['6FCKbDMmCiM37pN9qzNmgJxKqebWzGxZUcAqB8CNg84J'],
        }],
        'inputs': [{
            'fulfillment': 'cf:4:Te1duSG0oFpsm-5Sn9uQT1QIngxmhZSOEry8xeCna8OJSbCmmVoQddD14yzvLRC0XxC5CsK7KnOORFOe5gOiCkEUh-KqCBgia_38jx4B-KDUkhcMaT-oP2TcjIRZhhkJ',
            'fulfills': None,
            'owners_before': ['6FCKbDMmCiM37pN9qzNmgJxKqebWzGxZUcAqB8CNg84J'],
        }],
        'version': '0.9',
    }

Because a transaction must be signed before being sent, the ``id`` and
``fulfillment`` must be provided by the client.

.. important:: **Implications of Signed Payloads**

    Because BigchainDB relies on cryptographic signatures, the payloads need to
    be fully prepared and signed on the client side. This prevents the
    server(s) from tempering with the provided data.

    This enhanced security puts more work on the clients, as various values
    that could traditionally be generated on the server side need to be
    generated on the client side.


.. _bicycle-asset-creation-revisited:

********************************
Bicycle Asset Creation Revisited
********************************

The Prepared Transaction
========================
Recall that in order to prepare a transaction, we had to do something similar
to:

.. ipython::

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: from bigchaindb_driver.offchain import prepare_transaction

    In [0]: alice = generate_keypair()

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
Until 1.0, each version of BigchainDB can be expected to contain
backwards-incompatible changes to the transaction model. To facilitate this,
the ``version`` in a transaction will correspond with the version of BigchainDB
that was used to create it. For BigchainDB 0.9, this will be:

.. ipython::

    In [0]: version = '0.9'

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

The difficult parts are the condition details and URI. We''ll now see how to
generate them using the ``cryptoconditions`` library:

.. ipython::

    In [0]: from cryptoconditions import Ed25519Fulfillment

    In [0]: ed25519 = Ed25519Fulfillment(public_key=alice.public_key)

generate the condition URI:

.. ipython::

    In [0]: ed25519.condition_uri

So now you have a condition URI for Alice's public key.

As for the details:

.. ipython::

    In [0]: ed25519.to_dict()

We can now easily assemble the ``dict`` for the output:

.. ipython::

    In [0]: output = {
       ...:     'amount': 1,
       ...:     'condition': {
       ...:         'details': ed25519.to_dict(),
       ...:         'uri': ed25519.condition_uri,
       ...:     },
       ...:     'public_keys': (alice.public_key,),
       ...: }

Let's recap and set the ``outputs`` key with our self-constructed condition:

.. ipython::

    In [0]: from cryptoconditions import Ed25519Fulfillment

    In [0]: ed25519 = Ed25519Fulfillment(public_key=alice.public_key)

    In [0]: output = {
       ...:     'amount': 1,
       ...:     'condition': {
       ...:         'details': ed25519.to_dict(),
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
       ...: }

    In [0]: handcrafted_creation_tx

The only thing we're missing now is the ``id``. We'll generate it soon, but
before that, let's recap how we've put all the code together to generate the
above payload:

.. code-block:: python

    from cryptoconditions import Ed25519Fulfillment
    from bigchaindb_driver.crypto import CryptoKeypair

    alice = CryptoKeypair(
        public_key=alice.public_key,
        private_key=alice.private_key,
    )

    operation = 'CREATE'

    version = '0.9'

    asset = {
        'data': {
            'bicycle': {
                'manufacturer': 'bkfab',
                'serial_number': 'abcd1234',
            },
        },
    }

    metadata = {'planet': 'earth'}

    ed25519 = Ed25519Fulfillment(public_key=alice.public_key)

    output = {
        'amount': 1,
        'condition': {
            'details': ed25519.to_dict(),
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
    }

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

    In [0]: txid = sha3_256(json_str_tx.encode()).hexdigest()

    In [0]: handcrafted_creation_tx['id'] = txid

Compare this to the txid of the transaction generated via
``prepare_transaction()``:

.. ipython::

    In [0]: txid == prepared_creation_tx['id']

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

    In [0]: # serialize to json str

    In [0]: json_str_handcrafted_tx = json.dumps(handcrafted_creation_tx, sort_keys=True)

    In [0]: json_str_prepared_tx = json.dumps(prepared_creation_tx, sort_keys=True)

.. ipython::

    In [0]: json_str_handcrafted_tx == json_str_prepared_tx

    In [0]: prepared_creation_tx = prepared_creation_tx_bk

The fully handcrafted, yet-to-be-fulfilled ``CREATE`` transaction payload:

.. ipython::

    In [0]: handcrafted_creation_tx


The Fulfilled Transaction
=========================

.. ipython::

    In [0]: from cryptoconditions.crypto import Ed25519SigningKey

    In [0]: # fulfill prepared transaction

    In [0]: from bigchaindb_driver.offchain import fulfill_transaction

    In [0]: fulfilled_creation_tx = fulfill_transaction(
       ...:     prepared_creation_tx,
       ...:     private_keys=alice.private_key,
       ...: )

    In [0]: # fulfill handcrafted transaction (with our previously built ED25519 fulfillment)

    In [0]: ed25519.to_dict()

    In [0]: sk = Ed25519SigningKey(alice.private_key)

    In [0]: message = json.dumps(
       ...:     handcrafted_creation_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: ed25519.sign(message.encode(), sk)

    In [0]: fulfillment_uri = ed25519.serialize_uri()

    In [0]: handcrafted_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Let's check this:

.. ipython::

    In [0]: fulfilled_creation_tx['inputs'][0]['fulfillment'] == fulfillment_uri

    In [0]: json.dumps(fulfilled_creation_tx, sort_keys=True) == json.dumps(handcrafted_creation_tx, sort_keys=True)


In a nutshell
=============

Handcrafting a ``CREATE`` transaction can be done as follows:

.. code-block:: python

    import json
    from uuid import uuid4

    import sha3
    import cryptoconditions

    from bigchaindb_driver.crypto import generate_keypair


    alice = generate_keypair()

    operation = 'CREATE'

    version = '0.9'

    asset = {
        'data': {
            'bicycle': {
                'manufacturer': 'bkfab',
                'serial_number': 'abcd1234',
            },
        },
    }

    metadata = {'planet': 'earth'}

    ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=alice.public_key)

    output = {
        'amount': 1,
        'condition': {
            'details': ed25519.to_dict(),
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
    }

    json_str_tx = json.dumps(
        handcrafted_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    creation_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    handcrafted_creation_tx['id'] = creation_txid

    sk = cryptoconditions.crypto.Ed25519SigningKey(alice.private_key)

    message = json.dumps(
        handcrafted_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    ed25519.sign(message.encode(), sk)

    fulfillment_uri = ed25519.serialize_uri()

    handcrafted_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Sending it over to a BigchainDB node:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_creation_tx = bdb.transactions.send(handcrafted_creation_tx)

A few checks:

.. code-block:: python

    >>> json.dumps(returned_creation_tx, sort_keys=True) == json.dumps(handcrafted_creation_tx, sort_keys=True)
    True

.. code-block:: python

    >>> bdb.transactions.status(creation_txid)
    {'status': 'valid'}

.. tip:: When checking for the status of a transaction, one should keep in
    mind tiny delays before a transaction reaches a valid status.


.. _bicycle-asset-transfer-revisited:

********************************
Bicycle Asset Transfer Revisited
********************************
In the :ref:`bicycle transfer example <bicycle-transfer>` , we showed that the
transfer transaction was prepared and fulfilled as follows:

.. ipython::

    In [0]: creation_tx = fulfilled_creation_tx

    In [0]: bob = generate_keypair()

    In [0]: output_index = 0

    In [0]: output = creation_tx['outputs'][output_index]

    In [0]: transfer_input = {
       ...:     'fulfillment': output['condition']['details'],
       ...:     'fulfills': {
       ...:          'output': output_index,
       ...:          'txid': creation_tx['id'],
       ...:      },
       ...:      'owners_before': output['public_keys'],
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

    In [0]: version = '0.9'

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

    In [0]: from cryptoconditions import Ed25519Fulfillment

    In [0]: ed25519 = Ed25519Fulfillment(public_key=bob.public_key)

    In [0]: output = {
       ...:     'amount': 1,
       ...:     'condition': {
       ...:         'details': ed25519.to_dict(),
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
       ...:         'txid': creation_tx['id'],
       ...:         'output': 0,
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
       ...: }

    In [0]: handcrafted_transfer_tx

Up to now
---------

Before we generate the ``id``, let's recap how we got here:

.. code-block:: python

    from cryptoconditions import Ed25519Fulfillment
    from bigchaindb_driver.crypto import CryptoKeypair

    bob = CryptoKeypair(
        public_key=bob.public_key,
        private_key=bob.private_key,
    )

    operation = 'TRANSFER'
    version = '0.9'
    asset = {'id': creation_tx['id']}
    metadata = None

    ed25519 = Ed25519Fulfillment(public_key=bob.public_key)

    output = {
        'amount': 1,
        'condition': {
            'details': ed25519.to_dict(),
            'uri': ed25519.condition_uri,
        },
        'public_keys': (bob.public_key,),
    }
    outputs = (output,)

    input_ = {
        'fulfillment': None,
        'fulfills': {
            'txid': creation_tx['id'],
            'output': 0,
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
    }

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

    In [0]: txid = sha3_256(json_str_tx.encode()).hexdigest()

    In [0]: handcrafted_transfer_tx['id'] = txid

Compare this to the txid of the transaction generated via
``prepare_transaction()``

.. ipython::

    In [0]: txid == prepared_transfer_tx['id']

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

    In [0]: json_str_handcrafted_tx = json.dumps(handcrafted_transfer_tx, sort_keys=True)

    In [0]: json_str_prepared_tx = json.dumps(prepared_transfer_tx, sort_keys=True)

.. ipython::

    In [0]: json_str_handcrafted_tx == json_str_prepared_tx

    In [0]: prepared_transfer_tx = prepared_transfer_tx_bk

The fully handcrafted, yet-to-be-fulfilled ``TRANSFER`` transaction payload:

.. ipython::

    In [0]: handcrafted_transfer_tx


The Fulfilled Transaction
=========================

.. ipython::

    In [0]: from cryptoconditions.crypto import Ed25519SigningKey

    In [0]: from bigchaindb_driver.offchain import fulfill_transaction

    In [0]: # fulfill prepared transaction

    In [0]: fulfilled_transfer_tx = fulfill_transaction(
       ...:     prepared_transfer_tx,
       ...:     private_keys=alice.private_key,
       ...: )

    In [0]: # fulfill handcrafted transaction (with our previously built ED25519 fulfillment)

    In [0]: ed25519.to_dict()

    In [0]: sk = Ed25519SigningKey(alice.private_key)

    In [0]: message = json.dumps(
       ...:     handcrafted_transfer_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: ed25519.sign(message.encode(), sk)

    In [0]: fulfillment_uri = ed25519.serialize_uri()

    In [0]: handcrafted_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Let's check this:

.. ipython::

    In [0]: fulfilled_transfer_tx['inputs'][0]['fulfillment'] == fulfillment_uri

    In [0]: json.dumps(fulfilled_transfer_tx, sort_keys=True) == json.dumps(handcrafted_transfer_tx, sort_keys=True)


In a nutshell
=============

.. code-block:: python

    import json

    import sha3
    import cryptoconditions

    from bigchaindb_driver.crypto import generate_keypair


    bob = generate_keypair()

    operation = 'TRANSFER'
    version = '0.9'
    asset = {'id': creation_tx['id']}
    metadata = None

    ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=bob.public_key)

    output = {
        'amount': 1,
        'condition': {
            'details': ed25519.to_dict(),
            'uri': ed25519.condition_uri,
        },
        'public_keys': (bob.public_key,),
    }
    outputs = (output,)

    input_ = {
        'fulfillment': None,
        'fulfills': {
            'txid': creation_txid,
            'output': 0,
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
    }

    json_str_tx = json.dumps(
        handcrafted_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    transfer_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    handcrafted_transfer_tx['id'] = transfer_txid

    sk = cryptoconditions.crypto.Ed25519SigningKey(alice.private_key)

    message = json.dumps(
        handcrafted_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    ed25519.sign(message.encode(), sk)

    fulfillment_uri = ed25519.serialize_uri()

    handcrafted_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Sending it over to a BigchainDB node:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_transfer_tx = bdb.transactions.send(handcrafted_transfer_tx)

A few checks:

.. code-block:: python

    >>> json.dumps(returned_transfer_tx, sort_keys=True) == json.dumps(handcrafted_transfer_tx, sort_keys=True)
    True

.. code-block:: python

    >>> bdb.transactions.status(transfer_txid)
    {'status': 'valid'}

.. tip:: When checking for the status of a transaction, one should keep in
    mind tiny delays before a transaction reaches a valid status.


*************************
Bicycle Sharing Revisited
*************************

Handcrafting the ``CREATE`` transaction for our :ref:`bicycle sharing example
<bicycle-divisible-assets>`:

.. code-block:: python

    import json
    from uuid import uuid4

    import sha3
    import cryptoconditions

    from bigchaindb_driver.crypto import generate_keypair


    bob, carly = generate_keypair(), generate_keypair()
    version = '0.9'

    asset = {
        'data': {
            'token_for': {
                'bicycle': {
                    'manufacturer': 'bkfab',
                    'serial_number': 'abcd1234',
                },
                'description': 'time share token. each token equals 1 hour of riding.'
            },
        },
    }

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for carly
    ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=carly.public_key)

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri = ed25519.condition.serialize_uri()

    # CRYPTO-CONDITIONS: get the unsigned fulfillment dictionary (details)
    unsigned_fulfillment_dict = ed25519.to_dict()

    output = {
        'amount': 10,
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
        'asset': asset,
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
    }

    # JSON: serialize the id-less transaction to a json formatted string
    json_str_tx = json.dumps(
        token_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # SHA3: hash the serialized id-less transaction to generate the id
    creation_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    # add the id
    token_creation_tx['id'] = creation_txid

    # JSON: serialize the transaction-with-id to a json formatted string
    message = json.dumps(
        token_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # CRYPTO-CONDITIONS: sign the serialized transaction-with-id
    ed25519.sign(message.encode(),
                 cryptoconditions.crypto.Ed25519SigningKey(bob.private_key))

    # CRYPTO-CONDITIONS: generate the fulfillment uri
    fulfillment_uri = ed25519.serialize_uri()

    # add the fulfillment uri (signature)
    token_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Sending it over to a BigchainDB node:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_creation_tx = bdb.transactions.send(token_creation_tx)

A few checks:

.. code-block:: python

    >>> json.dumps(returned_creation_tx, sort_keys=True) == json.dumps(token_creation_tx, sort_keys=True)
    True

    >>> token_creation_tx['inputs'][0]['owners_before'][0] == bob.public_key
    True

    >>> token_creation_tx['outputs'][0]['public_keys'][0] == carly.public_key
    True

    >>> token_creation_tx['outputs'][0]['amount'] == 10
    True


.. code-block:: python

    >>> bdb.transactions.status(creation_txid)
    {'status': 'valid'}

.. tip:: When checking for the status of a transaction, one should keep in
    mind tiny delays before a transaction reaches a valid status.


Now Carly wants to ride the bicycle for 2 hours so she needs to send 2 tokens
to Bob:

.. code-block:: python

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for carly
    bob_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=bob.public_key)

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for carly
    carly_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=carly.public_key)

    # CRYPTO-CONDITIONS: generate the condition uris
    bob_condition_uri = bob_ed25519.condition.serialize_uri()
    carly_condition_uri = carly_ed25519.condition.serialize_uri()

    # CRYPTO-CONDITIONS: get the unsigned fulfillment dictionary (details)
    bob_unsigned_fulfillment_dict = bob_ed25519.to_dict()
    carly_unsigned_fulfillment_dict = carly_ed25519.to_dict()

    bob_output = {
        'amount': 2,
        'condition': {
            'details': bob_unsigned_fulfillment_dict,
            'uri': bob_condition_uri,
        },
        'public_keys': (bob.public_key,),
    }
    carly_output = {
        'amount': 8,
        'condition': {
            'details': carly_unsigned_fulfillment_dict,
            'uri': carly_condition_uri,
        },
        'public_keys': (carly.public_key,),
    }

    input_ = {
        'fulfillment': None,
        'fulfills': {
            'txid': token_creation_tx['id'],
            'output': 0,
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
    }

    # JSON: serialize the id-less transaction to a json formatted string
    json_str_tx = json.dumps(
        token_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # SHA3: hash the serialized id-less transaction to generate the id
    transfer_txid = sha3.sha3_256(json_str_tx.encode()).hexdigest()

    # add the id
    token_transfer_tx['id'] = transfer_txid

    # JSON: serialize the transaction-with-id to a json formatted string
    message = json.dumps(
        token_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # CRYPTO-CONDITIONS: sign the serialized transaction-with-id for bob
    carly_ed25519.sign(message.encode(),
                       cryptoconditions.crypto.Ed25519SigningKey(carly.private_key))

    # CRYPTO-CONDITIONS: generate bob's fulfillment uri
    fulfillment_uri = carly_ed25519.serialize_uri()

    # add bob's fulfillment uri (signature)
    token_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Sending it over to a BigchainDB node:

.. code-block:: python

    bdb = BigchainDB('http://bdb-server:9984')
    returned_transfer_tx = bdb.transactions.send(token_transfer_tx)

A few checks:

.. code-block:: python

    >>> json.dumps(returned_transfer_tx, sort_keys=True) == json.dumps(token_transfer_tx, sort_keys=True)
    True

    >>> token_transfer_tx['inputs'][0]['owners_before'][0] == carly.public_key
    True


.. code-block:: python

    >>> bdb.transactions.status(creation_txid)
    {'status': 'valid'}

.. tip:: When checking for the status of a transaction, one should keep in
    mind tiny delays before a transaction reaches a valid status.

*************************
Multiple Owners Revisited
*************************

Walkthrough
===========

We'll re-use the :ref:`example of Alice and Bob owning a car together
<car-multiple-owners>` to handcraft transactions with multiple owners.

Say ``alice`` and ``bob`` own a car together:

.. ipython::

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: from bigchaindb_driver import offchain

    In [0]: alice, bob = generate_keypair(), generate_keypair()

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


.. code-block:: python

    sent_car_tx = bdb.transactions.send(signed_car_creation_tx)

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
       ...:         'output': output_index,
       ...:         'txid': signed_car_creation_tx['id'],
       ...:     },
       ...:     'owners_before': output['public_keys'],
       ...: }

    In [0]: asset = signed_car_creation_tx['id']

    In [0]: car_transfer_tx = offchain.prepare_transaction(
       ...:     operation='TRANSFER',
       ...:     recipients=carol.public_key,
       ...:     asset={'id': car_creation_tx['id']},
       ...:     inputs=input_,
       ...: )

    In [0]: signed_car_transfer_tx = offchain.fulfill_transaction(
       ...:     car_transfer_tx, private_keys=[alice.private_key, bob.private_key]
       ...: )

    In [0]: signed_car_transfer_tx

Sending the transaction to a BigchainDB node:

.. code-block:: python

    sent_car_transfer_tx = bdb.transactions.send(signed_car_transfer_tx)

Doing this manually
-------------------

In order to do this manually, let's first import the necessary tools (json,
sha3, and cryptoconditions):

.. ipython::

    In [0]: import json

    In [0]: from sha3 import sha3_256

    In [0]: from cryptoconditions import Ed25519Fulfillment, ThresholdSha256Fulfillment

    In [0]: from cryptoconditions.crypto import Ed25519SigningKey

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

    In [0]: alice_ed25519 = Ed25519Fulfillment(public_key=alice.public_key)

    In [0]: bob_ed25519 = Ed25519Fulfillment(public_key=bob.public_key)

    In [0]: threshold_sha256 = ThresholdSha256Fulfillment(threshold=2)

    In [0]: threshold_sha256.add_subfulfillment(alice_ed25519)

    In [0]: threshold_sha256.add_subfulfillment(bob_ed25519)

    In [0]: unsigned_subfulfillments_dict = threshold_sha256.to_dict()

    In [0]: condition_uri = threshold_sha256.condition.serialize_uri()

    In [0]: output = {
       ...:     'amount': 1,
       ...:     'condition': {
       ...:         'details': unsigned_subfulfillments_dict,
       ...:         'uri': condition_uri,
       ...:     },
       ...:     'public_keys': (alice.public_key, bob.public_key),
       ...: }

.. tip:: The condition ``uri`` could have been generated in a slightly
    different way, which may be more intuitive to you. You can think of the
    threshold condition containing sub conditions:

    .. ipython::

        In [0]: alt_threshold_sha256 = ThresholdSha256Fulfillment(threshold=2)

        In [0]: alt_threshold_sha256.add_subcondition(alice_ed25519.condition)

        In [0]: alt_threshold_sha256.add_subcondition(bob_ed25519.condition)

        In [0]: alt_threshold_sha256.condition.serialize_uri() == condition_uri

    The ``details`` on the other hand holds the associated fulfillments not yet
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

    In [0]: version = '0.9'

    In [0]: handcrafted_car_creation_tx = {
       ...:     'operation': 'CREATE',
       ...:     'asset': car_asset,
       ...:     'metadata': None,
       ...:     'outputs': (output,),
       ...:     'inputs': (input_,),
       ...:     'version': version,
       ...: }

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

    In [0]: handcrafted_car_creation_tx['id'] == car_creation_tx['id']

Sign the transaction:

.. ipython::

    In [0]: message = json.dumps(
       ...:     handcrafted_car_creation_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: alice_ed25519.sign(message.encode(), Ed25519SigningKey(alice.private_key))

    In [0]: fulfillment_uri = alice_ed25519.serialize_uri()

    In [0]: handcrafted_car_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Compare our signed ``CREATE`` transaction with the driver's:

.. ipython::

    In [0]: (json.dumps(handcrafted_car_creation_tx, sort_keys=True) ==
       ...:  json.dumps(signed_car_creation_tx, sort_keys=True))

The transfer to Carol:

.. ipython::

    In [0]: alice_ed25519 = Ed25519Fulfillment(public_key=alice.public_key)

    In [0]: bob_ed25519 = Ed25519Fulfillment(public_key=bob.public_key)

    In [0]: carol_ed25519 = Ed25519Fulfillment(public_key=carol.public_key)

    In [0]: unsigned_fulfillments_dict = carol_ed25519.to_dict()

    In [0]: condition_uri = carol_ed25519.condition.serialize_uri()

    In [0]: output = {
       ...:     'amount': 1,
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
       ...:         'txid': handcrafted_car_creation_tx['id'],
       ...:         'output': 0,
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
       ...: }

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

    In [0]: handcrafted_car_transfer_tx['id'] == car_transfer_tx['id']

Sign the transaction:

.. ipython::

    In [0]: message = json.dumps(
       ...:     handcrafted_car_transfer_tx,
       ...:     sort_keys=True,
       ...:     separators=(',', ':'),
       ...:     ensure_ascii=False,
       ...: )

    In [0]: alice_sk = Ed25519SigningKey(alice.private_key)

    In [0]: bob_sk = Ed25519SigningKey(bob.private_key)

    In [0]: threshold_sha256 = ThresholdSha256Fulfillment(threshold=2)

    In [0]: threshold_sha256.add_subfulfillment(alice_ed25519)

    In [0]: threshold_sha256.add_subfulfillment(bob_ed25519)

    In [102]: alice_condition = threshold_sha256.get_subcondition_from_vk(alice.public_key)[0]

    In [103]: bob_condition = threshold_sha256.get_subcondition_from_vk(bob.public_key)[0]

    In [106]: alice_condition.sign(message.encode(), private_key=alice_sk)

    In [107]: bob_condition.sign(message.encode(), private_key=bob_sk)

    In [0]: fulfillment_uri = threshold_sha256.serialize_uri()

    In [0]: handcrafted_car_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Compare our signed ``TRANSFER`` transaction with the driver's:

.. ipython::

    In [0]: (json.dumps(handcrafted_car_transfer_tx, sort_keys=True) ==
       ...:  json.dumps(signed_car_transfer_tx, sort_keys=True))

In a nutshell
=============

Handcrafting the ``'CREATE'`` transaction
-----------------------------------------

.. code-block:: python

    import json

    import sha3
    import cryptoconditions

    from bigchaindb_driver.crypto import generate_keypair


    version = '0.9'

    car_asset = {
        'data': {
            'car': {
                'vin': '5YJRE11B781000196',
            },
        },
    }

    alice, bob = generate_keypair(), generate_keypair()

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for alice
    alice_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=alice.public_key)

    # CRYPTO-CONDITIONS: instantiate an Ed25519 crypto-condition for bob
    bob_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=bob.public_key)

    # CRYPTO-CONDITIONS: instantiate a threshold SHA 256 crypto-condition
    threshold_sha256 = cryptoconditions.ThresholdSha256Fulfillment(threshold=2)

    # CRYPTO-CONDITIONS: add alice ed25519 to the threshold SHA 256 condition
    threshold_sha256.add_subfulfillment(alice_ed25519)

    # CRYPTO-CONDITIONS: add bob ed25519 to the threshold SHA 256 condition
    threshold_sha256.add_subfulfillment(bob_ed25519)

    # CRYPTO-CONDITIONS: get the unsigned fulfillment dictionary (details)
    unsigned_subfulfillments_dict = threshold_sha256.to_dict()

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri = threshold_sha256.condition.serialize_uri()

    output = {
        'amount': 1,
        'condition': {
            'details': unsigned_subfulfillments_dict,
            'uri': threshold_sha256.condition_uri,
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
    }

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

    # JSON: serialize the transaction-with-id to a json formatted string
    message = json.dumps(
        handcrafted_car_creation_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    # CRYPTO-CONDITIONS: sign the serialized transaction-with-id
    alice_ed25519.sign(message.encode(),
                       cryptoconditions.crypto.Ed25519SigningKey(alice.private_key))

    # CRYPTO-CONDITIONS: generate the fulfillment uri
    fulfillment_uri = alice_ed25519.serialize_uri()

    # add the fulfillment uri (signature)
    handcrafted_car_creation_tx['inputs'][0]['fulfillment'] = fulfillment_uri


Sending it over to a BigchainDB node:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984')
    returned_car_creation_tx = bdb.transactions.send(handcrafted_car_creation_tx)

Wait for some nano seconds, and check the status:

.. code-block:: python

    >>> bdb.transactions.status(returned_car_creation_tx['id'])
    {'status': 'valid'}

Handcrafting the ``'TRANSFER'`` transaction
-------------------------------------------

.. code-block:: python

    version = '0.9'

    carol = generate_keypair()

    alice_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=alice.public_key)

    bob_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=bob.public_key)

    carol_ed25519 = cryptoconditions.Ed25519Fulfillment(public_key=carol.public_key)

    unsigned_fulfillments_dict = carol_ed25519.to_dict()

    condition_uri = carol_ed25519.condition.serialize_uri()

    output = {
        'amount': 1,
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
            'txid': handcrafted_car_creation_tx['id'],
            'output': 0,
        },
        'owners_before': (alice.public_key, bob.public_key),
    }

    # Craft the payload:
    handcrafted_car_transfer_tx = {
        'operation': 'TRANSFER',
        'asset': {'id': car_asset['id']},
        'metadata': None,
        'outputs': (output,),
        'inputs': (input_,),
        'version': version,
    }

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

    # Sign the transaction:
    message = json.dumps(
        handcrafted_car_transfer_tx,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )

    alice_sk = cryptoconditions.crypto.Ed25519SigningKey(alice.private_key)

    bob_sk = cryptoconditions.crypto.Ed25519SigningKey(bob.private_key)

    threshold_sha256 = cryptoconditions.ThresholdSha256Fulfillment(threshold=2)

    threshold_sha256.add_subfulfillment(alice_ed25519)

    threshold_sha256.add_subfulfillment(bob_ed25519)

    alice_condition = threshold_sha256.get_subcondition_from_vk(alice.public_key)[0]

    bob_condition = threshold_sha256.get_subcondition_from_vk(bob.public_key)[0]

    alice_condition.sign(message.encode(), private_key=alice_sk)

    bob_condition.sign(message.encode(), private_key=bob_sk)

    fulfillment_uri = threshold_sha256.serialize_uri()

    handcrafted_car_transfer_tx['inputs'][0]['fulfillment'] = fulfillment_uri

Sending it over to a BigchainDB node:

.. code-block:: python

    bdb = BigchainDB('http://bdb-server:9984')
    returned_car_transfer_tx = bdb.transactions.send(handcrafted_car_transfer_tx)

Wait for some nano seconds, and check the status:

.. code-block:: python

    >>> bdb.transactions.status(returned_car_transfer_tx['id'])
    {'status': 'valid'}



.. _sha3: https://github.com/tiran/pysha3
.. _cryptoconditions: https://github.com/bigchaindb/cryptoconditions
.. _cryptoconditions internet draft: https://tools.ietf.org/html/draft-thomas-crypto-conditions-01
.. _The Transaction Model: https://docs.bigchaindb.com/projects/server/en/latest/data-models/transaction-model.html
.. _The Transaction Schema: https://docs.bigchaindb.com/projects/server/en/latest/schema/transaction.html
