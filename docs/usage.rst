.. _basic-usage:

====================
Basic Usage Examples
====================

First, make sure you're using Python 3,
you've :doc:`installed the bigchaindb_driver Python package <quickstart>`,
and you've :doc:`connected to a BigchainDB node or cluster <connect>`.

For the sake of these examples, we'll assume:

.. ipython::

    In [0]: from bigchaindb_driver import BigchainDB

    In [0]: bdb = BigchainDB('http://bdb-server:9984')

.. important::

    You will want to change the instances of ``'http://bdb-server:9984'``
    to be the URL of the node you want to connect to. See the :doc:`docs on
    connecting <connect>` for more information.

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

To check the status of the transaction:

.. code-block:: python

    >>> bdb.transactions.status(txid)

.. note:: It may take a small amount of time before a BigchainDB cluster
    confirms a transaction as being valid.

Here's some code that keeps checking the status of the transaction until it is valid:

.. code-block:: python

    >>> trials = 0

    >>> while trials < 100:
    ...     try:
    ...         if bdb.transactions.status(txid).get('status') == 'valid':
    ...             break
    ...     except bigchaindb_driver.exceptions.NotFoundError:
    ...         trials += 1

    >>> bdb.transactions.status(txid)
    {'status': 'valid'}

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
       ...:          'output': output_index,
       ...:          'txid': creation_tx['id'],
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

and finally send it to the connected BigchainDB node:

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True

The ``fulfilled_transfer_tx`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_transfer_tx

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

    bdb = BigchainDB('http://bdb-server:9984')

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

    trials = 0
    while trials < 60:
        try:
            if bdb.transactions.status(txid).get('status') == 'valid':
                print('Tx valid in:', trials, 'secs')
                break
        except bigchaindb_driver.exceptions.NotFoundError:
            trials += 1
            sleep(1)

    if trials == 60:
        print('Tx is still being processed... Bye!')
        exit(0)

    asset_id = txid

    transfer_asset = {
        'id': asset_id
    }

    output_index = 0
    output = fulfilled_creation_tx['outputs'][output_index]

    transfer_input = {
        'fulfillment': output['condition']['details'],
        'fulfills': {
            'output': output_index,
            'txid': fulfilled_creation_tx['id']
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


Transaction Status
------------------
Using the ``id`` of a transaction, its status can be obtained:

.. code-block:: python

    >>> bdb.transactions.status(creation_tx['id'])
    {'status': 'valid'}

Handling cases for which the transaction ``id`` may not be found:

.. code-block:: python

    import logging

    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.exceptions import NotFoundError

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)-15s %(status)-3s %(message)s')

    bdb = BigchainDB('http://bdb-server:9984')
    txid = '12345'
    try:
        status = bdb.transactions.status(txid)
    except NotFoundError as e:
        logger.error('Transaction "%s" was not found.',
                     txid,
                     extra={'status': e.status_code})

Running the above code should give something similar to:

.. code-block:: bash

    2016-09-29 15:06:30,606 404 Transaction "12345" was not found.


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


The ``fulfilled_token_tx`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_token_tx

Bob is the issuer:

.. ipython::

    In [0]: fulfilled_token_tx['inputs'][0]['owners_before'][0] == bob.public_key

Carly is the owner of 10 tokens:

.. ipython::

    In [0]: fulfilled_token_tx['outputs'][0]['public_keys'][0] == carly.public_key

    In [0]: fulfilled_token_tx['outputs'][0]['amount'] == 10


Now in possession of the tokens, Carly wants to ride the bicycle for two hours.
To do so, she needs to send two tokens to Bob:

.. ipython::

    In [0]: output_index = 0

    In [0]: output = prepared_token_tx['outputs'][output_index]

    In [0]: transfer_input = {
       ...:     'fulfillment': output['condition']['details'],
       ...:     'fulfills': {
       ...:         'output': output_index,
       ...:         'txid': prepared_token_tx['id'],
       ...:     },
       ...:     'owners_before': output['public_keys'],
       ...: }

    In [0]: transfer_asset = {
       ...:     'id': prepared_token_tx['id'],
       ...: }

    In [0]: prepared_transfer_tx = bdb.transactions.prepare(
       ...:     operation='TRANSFER',
       ...:     asset=transfer_asset,
       ...:     inputs=transfer_input,
       ...:     recipients=[([bob.public_key], 2), ([carly.public_key], 8)]
       ...: )

    In [0]: fulfilled_transfer_tx = bdb.transactions.fulfill(
       ...:     prepared_transfer_tx, private_keys=carly.private_key)

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True

Notice how Carly needs to reassign the remaining eight tokens to herself if she
wants to only transfer two tokens (out of the available 10) to Bob. BigchainDB
ensures that the amount being consumed in each transaction (with divisible
assets) is the same as the amount being output. This ensures that no amounts
are lost.

Also note how, because we were consuming a ``TRANSFER`` transaction, we were
able to directly use the ``TRANSFER`` transaction's ``asset`` as the new
transaction's ``asset`` because it already contained the asset's id.

The ``fulfilled_transfer_tx`` dictionary should have two outputs, one with
``amount=2`` and the other with ``amount=8``:

.. ipython::

    In [0]: fulfilled_transfer_tx
