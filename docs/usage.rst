.. _basic-usage:

====================
Basic Usage Examples
====================

For the examples on this page,
we assume you're using a Python 3 version of IPython (or similar),
you've :doc:`installed the bigchaindb_driver Python package <quickstart>`,
and :doc:`you have determined the BigchainDB Root URL <connect>`
of the node or cluster you want to connect to.


Getting Started
---------------

We begin by creating an object of class BigchainDB:

.. ipython::

    In [0]: from bigchaindb_driver import BigchainDB

    In [0]: bdb_root_url = 'https://example.com:9984'  # Use YOUR BigchainDB Root URL here

If the BigchainDB node or cluster doesn't require authentication tokens, you can do:

.. ipython::

    In [0]: bdb = BigchainDB(bdb_root_url)

If it *does* require authentication tokens, you can do put them in a dict like so:

.. ipython::

    In [0]: tokens = {'app_id': 'your_app_id', 'app_key': 'your_app_key'}

    In [0]: bdb = BigchainDB(bdb_root_url, headers=tokens)



Digital Asset Definition
------------------------
As an example, let's consider the creation and transfer of a digital asset that
represents a bicycle:

.. ipython::

    In [0]: bicycle = {
       ...:     'data': {
       ...:         'bicycle': {
       ...:             'serial_number': 'abcd1234',
       ...:             'manufacturer': 'bkfab',
       ...:         },
       ...:     },
       ...: }

We'll suppose that the bike belongs to Alice, and that it will be transferred
to Bob.

In general, you may use any dictionary for the ``'data'`` property.


Metadata Definition (*optional*)
--------------------------------
You can `optionally` add metadata to a transaction. Any dictionary is accepted.

For example:

.. ipython::

    In [0]: metadata = {'planet': 'earth'}


Cryptographic Identities Generation
-----------------------------------
Alice and Bob are represented by public/private key pairs. The private key is
used to sign transactions, meanwhile the public key is used to verify that a
signed transaction was indeed signed by the one who claims to be the signee.

.. ipython::

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: alice, bob = generate_keypair(), generate_keypair()


.. _asset-creation:

Asset Creation
--------------
We're now ready to create the digital asset. First, let's prepare the
transaction:

.. ipython::

   In [0]: prepared_creation_tx = bdb.transactions.prepare(
      ...:     operation='CREATE',
      ...:     signers=alice.public_key,
      ...:     asset=bicycle,
      ...:     metadata=metadata,
      ...: )

The ``prepared_creation_tx`` dictionary should be similar to:

.. ipython::

    In [0]: prepared_creation_tx


The transaction now needs to be fulfilled by signing it with Alice's private
key:

.. ipython::

    In [0]: fulfilled_creation_tx = bdb.transactions.fulfill(
       ...:     prepared_creation_tx, private_keys=alice.private_key)

.. ipython::

    In [0]: fulfilled_creation_tx

And sent over to a BigchainDB node:

.. code-block:: python

    >>> sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)

Note that the response from the node should be the same as that which was sent:

.. code-block:: python

    >>> sent_creation_tx == fulfilled_creation_tx
    True

Notice the transaction ``id``:

.. ipython::

    In [0]: txid = fulfilled_creation_tx['id']

    In [0]: txid


.. _bicycle-transfer:


Asset Transfer
--------------
Imagine some time goes by, during which Alice is happy with her bicycle, and
one day, she meets Bob, who is interested in acquiring her bicycle. The timing
is good for Alice as she had been wanting to get a new bicycle.

To transfer the bicycle (asset) to Bob, Alice must consume the transaction in
which the Bicycle asset was created.

Alice could retrieve the transaction:

.. code-block:: python

    >>>  creation_tx = bdb.transactions.retrieve(txid)

or simply use ``fulfilled_creation_tx``:

.. ipython::

    In [0]: creation_tx = fulfilled_creation_tx

In order to prepare the transfer transaction, we first need to know the id of
the asset we'll be transferring. Here, because Alice is consuming a ``CREATE``
transaction, we have a special case in that the asset id is NOT found on the
``asset`` itself, but is simply the ``CREATE`` transaction's id:

.. ipython::

    In [0]: asset_id = creation_tx['id']

    In [0]: transfer_asset = {
       ...:     'id': asset_id,
       ...: }

Let's now prepare the transfer transaction:

.. ipython::

    In [0]: output_index = 0

    In [0]: output = creation_tx['outputs'][output_index]

    In [0]: transfer_input = {
       ...:     'fulfillment': output['condition']['details'],
       ...:     'fulfills': {
       ...:          'output_index': output_index,
       ...:          'transaction_id': creation_tx['id'],
       ...:      },
       ...:      'owners_before': output['public_keys'],
       ...: }

    In [0]: prepared_transfer_tx = bdb.transactions.prepare(
       ...:     operation='TRANSFER',
       ...:     asset=transfer_asset,
       ...:     inputs=transfer_input,
       ...:     recipients=bob.public_key,
       ...: )

fulfill it:

.. ipython::

    In [0]: fulfilled_transfer_tx = bdb.transactions.fulfill(
       ...:     prepared_transfer_tx,
       ...:     private_keys=alice.private_key,
       ...: )

The ``fulfilled_transfer_tx`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_transfer_tx

and finally send it to the connected BigchainDB node:

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True

Bob is the new owner:

.. ipython::

    In [0]: fulfilled_transfer_tx['outputs'][0]['public_keys'][0] == bob.public_key

Alice is the former owner:

.. ipython::

    In [0]: fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == alice.public_key

.. note:: Obtaining asset ids:

    You might have noticed that we considered Alice's case of consuming a
    ``CREATE`` transaction as a special case. In order to obtain the asset id
    of a ``CREATE`` transaction, we had to use the ``CREATE`` transaction's
    id::

        transfer_asset_id = create_tx['id']

    If you instead wanted to consume ``TRANSFER`` transactions (for example,
    ``fulfilled_transfer_tx``), you could obtain the asset id to transfer from
    the ``asset['id']`` property::

        transfer_asset_id = transfer_tx['asset']['id']



Recap: Asset Creation & Transfer
--------------------------------

.. code-block:: python

    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.crypto import generate_keypair
    from time import sleep
    from sys import exit

    alice, bob = generate_keypair(), generate_keypair()

    bdb_root_url = 'https://example.com:9984'  # Use YOUR BigchainDB Root URL here

    bdb = BigchainDB(bdb_root_url)

    bicycle_asset = {
        'data': {
            'bicycle': {
                'serial_number': 'abcd1234',
                'manufacturer': 'bkfab'
            },
        },
    }

    bicycle_asset_metadata = {
        'planet': 'earth'
    }

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=bicycle_asset,
        metadata=bicycle_asset_metadata
    )

    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx,
        private_keys=alice.private_key
    )

    sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)

    txid = fulfilled_creation_tx['id']

    asset_id = txid

    transfer_asset = {
        'id': asset_id
    }

    output_index = 0
    output = fulfilled_creation_tx['outputs'][output_index]

    transfer_input = {
        'fulfillment': output['condition']['details'],
        'fulfills': {
            'output_index': output_index,
            'transaction_id': fulfilled_creation_tx['id']
        },
        'owners_before': output['public_keys']
    }

    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=bob.public_key,
    )

    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=alice.private_key,
    )

    sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

    print("Is Bob the owner?",
        sent_transfer_tx['outputs'][0]['public_keys'][0] == bob.public_key)

    print("Was Alice the previous owner?",
        fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == alice.public_key)




.. _bicycle-divisible-assets:

Divisible Assets
----------------

All assets in BigchainDB become implicitly divisible if a transaction contains
more than one of that asset (we'll see how this happens shortly).

Let's continue with the bicycle example. Bob is now the proud owner of the
bicycle and he decides he wants to rent the bicycle. Bob starts by creating a
time sharing token in which one token corresponds to one hour of riding time:

.. ipython::

    In [0]: bicycle_token = {
       ...:     'data': {
       ...:         'token_for': {
       ...:             'bicycle': {
       ...:                 'serial_number': 'abcd1234',
       ...:                 'manufacturer': 'bkfab'
       ...:             }
       ...:         },
       ...:         'description': 'Time share token. Each token equals one hour of riding.',
       ...:     },
       ...: }

Bob has now decided to issue 10 tokens and assigns them to Carly. Notice how we
denote Carly as receiving 10 tokens by using a tuple:
``([carly.public_key], 10)``.

.. ipython::

    In [0]: bob, carly = generate_keypair(), generate_keypair()

    In [0]: prepared_token_tx = bdb.transactions.prepare(
       ...:     operation='CREATE',
       ...:     signers=bob.public_key,
       ...:     recipients=[([carly.public_key], 10)],
       ...:     asset=bicycle_token,
       ...: )

    In [0]: fulfilled_token_tx = bdb.transactions.fulfill(
       ...:     prepared_token_tx, private_keys=bob.private_key)

The ``fulfilled_token_tx`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_token_tx

Sending the transaction:

.. code-block:: python

    >>> sent_token_tx = bdb.transactions.send(fulfilled_token_tx)

    >>> sent_token_tx == fulfilled_token_tx
    True

.. note:: Defining ``recipients``:

    To create divisible assets, we need to specify an amount ``>1`` together
    with the public keys. The way we do this is by passing a ``list`` of
    ``tuples`` in ``recipients`` where each ``tuple`` corresponds to an output.

    For instance, instead of creating a transaction with one output containing
    ``amount=10`` we could have created a transaction with two outputs each
    holding ``amount=5``:

    .. code-block:: python

        recipients=[([carly.public_key], 5), ([carly.public_key], 5)]

    The reason why the addresses are contained in ``lists`` is because each
    output can have multiple recipients. For instance, we can create an
    output with ``amount=10`` in which both Carly and Alice are recipients
    (of the same asset):

    .. code-block:: python

        recipients=[([carly.public_key, alice.public_key], 10)]


Bob is the issuer:

.. ipython::

    In [0]: fulfilled_token_tx['inputs'][0]['owners_before'][0] == bob.public_key

Carly is the owner of 10 tokens:

.. ipython::

    In [0]: fulfilled_token_tx['outputs'][0]['public_keys'][0] == carly.public_key

    In [0]: fulfilled_token_tx['outputs'][0]['amount'] == '10'


Now in possession of the tokens, Carly wants to ride the bicycle for two hours.
To do so, she needs to send two tokens to Bob:

.. ipython::

    In [0]: output_index = 0

    In [0]: output = fulfilled_token_tx['outputs'][output_index]

    In [0]: transfer_input = {
       ...:     'fulfillment': output['condition']['details'],
       ...:     'fulfills': {
       ...:         'output_index': output_index,
       ...:         'transaction_id': fulfilled_token_tx['id'],
       ...:     },
       ...:     'owners_before': output['public_keys'],
       ...: }

    In [0]: transfer_asset = {
       ...:     'id': fulfilled_token_tx['id'],
       ...: }

    In [0]: prepared_transfer_tx = bdb.transactions.prepare(
       ...:     operation='TRANSFER',
       ...:     asset=transfer_asset,
       ...:     inputs=transfer_input,
       ...:     recipients=[([bob.public_key], 2), ([carly.public_key], 8)]
       ...: )

    In [0]: fulfilled_transfer_tx = bdb.transactions.fulfill(
       ...:     prepared_transfer_tx, private_keys=carly.private_key)

Notice how Carly needs to reassign the remaining eight tokens to herself if she
wants to only transfer two tokens (out of the available 10) to Bob. BigchainDB
ensures that the amount being consumed in each transaction (with divisible
assets) is the same as the amount being output. This ensures that no amounts
are lost.

Also note how, because we were consuming a ``TRANSFER`` transaction, we were
able to directly use the ``TRANSFER`` transaction's ``asset`` as the new
transaction's ``asset`` because it already contained the asset's id.

The ``fulfilled_transfer_tx`` dictionary should have two outputs, one with
``amount='2'`` and the other with ``amount='8'``:

.. ipython::

    In [0]: fulfilled_transfer_tx

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True


Querying for Assets
-------------------

BigchainDB allows you to query for assets using simple text search. This search
is applied to all the strings inside the asset payload and returns all the
assets that match a given text search string.

Let's create 3 assets:

.. code-block:: python

    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.crypto import generate_keypair

    bdb_root_url = 'https://example.com:9984'

    bdb = BigchainDB(bdb_root_url)

    alice = generate_keypair()

    hello_1 = {'data': {'msg': 'Hello BigchainDB 1!'},}
    hello_2 = {'data': {'msg': 'Hello BigchainDB 2!'},}
    hello_3 = {'data': {'msg': 'Hello BigchainDB 3!'},}

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=hello_1
    )
    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)
    bdb.transactions.send(fulfilled_creation_tx)

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=hello_2
    )
    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)
    bdb.transactions.send(fulfilled_creation_tx)

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=hello_3
    )
    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)
    bdb.transactions.send(fulfilled_creation_tx)

Let's perform a text search for all assets that contain the word ``bigchaindb``:

.. code-block:: python

    >> bdb.assets.get(search='bigchaindb')
    [
        {
            'data': {'msg': 'Hello BigchainDB 1!'},
            'id': '7582d7a81652d0230fefb47dafc360ff09b2c2566b68f05c3a004d57e7fe7610'
        },
        {
            'data': {'msg': 'Hello BigchainDB 2!'},
            'id': 'e40f4b6ac70b9c1b3b237ec13f4174384fd4d54d36dfde25520171577c49caa4'
        },
        {
            'data': {'msg': 'Hello BigchainDB 3!'},
            'id': '748f6c30daaf771c9020d84db9ad8ac4d1f7c8de7013db55e16f10ba090f7013'
        }
    ]

This call returns all the assets that match the string ``bigchaindb``, sorted
by `text score
<https://docs.mongodb.com/manual/reference/operator/query/text/#text-operator-text-score>`_,
as well as the asset ``id``. This is the same ``id`` of the transaction that
created the asset.

It's also possible to limit the amount of returned results using the ``limit``
argument:

.. code-block:: python

    >> bdb.assets.get(search='bigchaindb', limit=2)
    [
        {
            'data': {'msg': 'Hello BigchainDB 1!'},
            'id': '7582d7a81652d0230fefb47dafc360ff09b2c2566b68f05c3a004d57e7fe7610'
        },
        {
            'data': {'msg': 'Hello BigchainDB 2!'},
            'id': 'e40f4b6ac70b9c1b3b237ec13f4174384fd4d54d36dfde25520171577c49caa4'
        }
    ]

Querying for Transactions
-------------------------

For this query we need to provide an ``asset_id`` and we will get back a list of transactions
that use the asset with the ID ``asset_id``.

.. note::
    Please note that the id of an asset in BigchainDB is actually the id of the
    transaction which created the asset. In other words, when querying for an asset
    id with the operation set to ``CREATE``, only one transaction should be expected.
    This transaction will be the transaction in which the asset was created, and the
    transaction id will be equal to the given asset id.

We will use the id of our last example :ref:`Divisible Assets <bicycle-divisible-assets>`.
Let's try it:

.. code-block:: python

    >>> bdb.transactions.get(asset_id=sent_token_tx['id'])
    [{'asset': {'data': {'description': 'Time share token. Each token equals one '
                                    'hour of riding.',
                     'token_for': {'bicycle': {'manufacturer': 'bkfab',
                                               'serial_number': 'abcd1234'}}}},
    'id': 'b2403bb6bb7f9c0af2bc2b5b03b291a378fd8499f44cade4aa14dd5419e5b7c7',
    'inputs': [{'fulfillment': 'pGSAIFetX0Fz6ZUN20tJp_dWJKs0_nDDz7oOmTaToGrzzw5zgUBPJsUGHcm8R-ntQSHvK3tgoyHIvCrrNrI6lJkud81cZKWFb9XehNAvWswPWSx1_6EwFKVYV-fjlxPvExm8XZIH',
              'fulfills': None,
              'owners_before': ['6uFoT6vd38qGqo2dRMBQsSojytUadyijBH4wgZGrPhZt']}],
    'metadata': None,
    'operation': 'CREATE',
    'outputs': [{'amount': '10',
               'condition': {'details': {'public_key': '8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne',
                                         'type': 'ed25519-sha-256'},
                             'uri': 'ni:///sha-256;PN3UO9GztlEBitIZf5m4iYNgyexvOk6Sdjq3PANsxko?fpt=ed25519-sha-256&cost=131072'},
               'public_keys': ['8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne']}],
    'version': '2.0'},
    {'asset': {'id': 'b2403bb6bb7f9c0af2bc2b5b03b291a378fd8499f44cade4aa14dd5419e5b7c7'},
    'id': '3ce3a5d4d984ca92f4a34967a2c181dbe8da8d6e4477220d7869ada9379dc410',
    'inputs': [{'fulfillment': 'pGSAIHTmVLbdfDFHTBx6gVr4NczRN-D1MhHltB0nn79luYlfgUCrppCotKAZoVW7nKye4I2HzGxlgwjmx47w_HxGXOFVbvCppNTLeVX4NrHYFRJlv8QKgj_ZaLctHpT6HPLLYIIG',
              'fulfills': {'output_index': 0,
                           'transaction_id': 'b2403bb6bb7f9c0af2bc2b5b03b291a378fd8499f44cade4aa14dd5419e5b7c7'},
              'owners_before': ['8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne']}],
    'metadata': None,
    'operation': 'TRANSFER',
    'outputs': [{'amount': '2',
               'condition': {'details': {'public_key': '6uFoT6vd38qGqo2dRMBQsSojytUadyijBH4wgZGrPhZt',
                                         'type': 'ed25519-sha-256'},
                             'uri': 'ni:///sha-256;HapGwR7oqOS3oZSICryoGJL0SfQF2LcSJe98jBKmdqo?fpt=ed25519-sha-256&cost=131072'},
               'public_keys': ['6uFoT6vd38qGqo2dRMBQsSojytUadyijBH4wgZGrPhZt']},
              {'amount': '8',
               'condition': {'details': {'public_key': '8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne',
                                         'type': 'ed25519-sha-256'},
                             'uri': 'ni:///sha-256;PN3UO9GztlEBitIZf5m4iYNgyexvOk6Sdjq3PANsxko?fpt=ed25519-sha-256&cost=131072'},
               'public_keys': ['8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne']}],
    'version': '2.0'}]


If you were busy sharing your bicycle with the whole city you might have a really long list.
So let's limit the results and just see the ``CREATE`` transaction.

.. code-block:: python

    >>> bdb.transactions.get(asset_id=sent_token_tx['id'], operation='CREATE')
    [{'asset': {'data': {'description': 'Time share token. Each token equals one '
                                    'hour of riding.',
                     'token_for': {'bicycle': {'manufacturer': 'bkfab',
                                               'serial_number': 'abcd1234'}}}},
    'id': 'b2403bb6bb7f9c0af2bc2b5b03b291a378fd8499f44cade4aa14dd5419e5b7c7',
    'inputs': [{'fulfillment': 'pGSAIFetX0Fz6ZUN20tJp_dWJKs0_nDDz7oOmTaToGrzzw5zgUBPJsUGHcm8R-ntQSHvK3tgoyHIvCrrNrI6lJkud81cZKWFb9XehNAvWswPWSx1_6EwFKVYV-fjlxPvExm8XZIH',
              'fulfills': None,
              'owners_before': ['6uFoT6vd38qGqo2dRMBQsSojytUadyijBH4wgZGrPhZt']}],
    'metadata': None,
    'operation': 'CREATE',
    'outputs': [{'amount': '10',
               'condition': {'details': {'public_key': '8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne',
                                         'type': 'ed25519-sha-256'},
                             'uri': 'ni:///sha-256;PN3UO9GztlEBitIZf5m4iYNgyexvOk6Sdjq3PANsxko?fpt=ed25519-sha-256&cost=131072'},
               'public_keys': ['8sKzvruHPhH3LKoGZDJE9MRzpgfFQJGZhzHTghebbFne']}],
    'version': '2.0'}]
