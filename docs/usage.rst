.. _basic-usage:

====================
Basic Usage Examples
====================

.. note::

   You must :doc:`install the bigchaindb_driver Python package <quickstart>` first.

   You should use Python 3 for these examples.


The BigchainDB driver's main purpose is to connect to one or more BigchainDB
server nodes, in order to perform supported API calls documented under
:doc:`drivers-clients/http-client-server-api`.

Connecting to a BigchainDB node is done via the
:class:`BigchainDB class <bigchaindb_driver.BigchainDB>`:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('<api_endpoint>')

where ``<api_endpoint>`` is the root URL of the BigchainDB server API you wish
to connect to. 

For the simplest case in which a BigchainDB node would be running locally, (and
the ``BIGCHAINDB_SERVER_BIND`` setting wouldn't have been changed), you would
connect to the local BigchainDB server this way:

.. code-block:: python

    bdb = BigchainDB('http://localhost:9984/api/v1')

If you are running the docker-based dev setup that comes along with the
`bigchaindb_driver`_ repository (see :ref:`devenv-docker` for more
information), and wish to connect to it from the ``bdb-driver`` linked
(container) service:

.. code-block:: python

    >>> bdb = BigchainDB('http://bdb-server:9984/api/v1')

Alternatively, you may connect to the containerized BigchainDB node from
"outside", in which case you need to know the port binding:

.. code-block:: bash
    
    $ docker-compose port bdb-server 9984
    0.0.0.0:32780

.. code-block:: python

    >>> bdb = BigchainDB('http://0.0.0.0:32780/api/v1')

For the sake of this example:

.. ipython::

    In [0]: from bigchaindb_driver import BigchainDB

    In [0]: bdb = BigchainDB('http://bdb-server:9984/api/v1')


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


Metadata Definition (*optional*)
--------------------------------
You can `optionally` add metadata to a transaction. Any dictionary is accepted.

For example:

.. ipython::

    In [0]: metadata = {'planet': 'earth'}


Cryptographic Identities Generation
-----------------------------------
Alice, and Bob are represented by public/private key pairs. The private key is
used to sign transactions, meanwhile the public key is used to verify that a
signed transaction was indeed signed by the one who claims to be the signee. 

.. ipython::

    In [0]: from bigchaindb_driver.crypto import generate_keypair

    In [0]: alice, bob = generate_keypair(), generate_keypair()


Asset Creation
--------------
We're now ready to create the digital asset. First we prepare the transaction:

.. ipython::

   In [0]: prepared_creation_tx = bdb.transactions.prepare(
      ...:     operation='CREATE',
      ...:     owners_before=alice.public_key,
      ...:     asset=bicycle,
      ...:     metadata=metadata,
      ...: )

The ``prepared_creation_tx`` dictionary should be similar to:

.. ipython::

   In [0]: prepared_creation_tx


The transaction needs to be fulfilled:

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

    >>> trials = 0

    >>> while bdb.transactions.status(txid).get('status') != 'valid' and trials < 100:
    ...     trials += 1

    >>> bdb.transactions.status(txid)
    {'status': 'valid'}

.. note:: It may take a small amount of time before a BigchainDB cluster
    confirms a transaction as being valid.

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

Preparing the transfer transaction:

.. ipython::
    
    In [0]: cid = 0

    In [0]: condition = creation_tx['conditions'][cid]

    In [0]: transfer_input = {
       ...:     'fulfillment': condition['condition']['details'],
       ...:     'input': {
       ...:          'cid': cid,
       ...:          'txid': creation_tx['id'],
       ...:      },
       ...:      'owners_before': condition['owners_after'],
       ...: }

    In [0]: prepared_transfer_tx = bdb.transactions.prepare(
       ...:     operation='TRANSFER',
       ...:     asset=creation_tx['asset'],
       ...:     inputs=transfer_input,
       ...:     owners_after=bob.public_key,
       ...: )

and then fulfills the prepared transfer:

.. ipython::

    In [0]: fulfilled_transfer_tx = bdb.transactions.fulfill(
       ...:     prepared_transfer_tx,
       ...:     private_keys=alice.private_key,
       ...: )

and finally sends the fulfilled transaction to the connected BigchainDB node:

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

.. code-block:: python

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True

The ``fulfilled_transfer_tx`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_transfer_tx

Bob is the new owner: 

.. ipython::

    In [0]: fulfilled_transfer_tx['conditions'][0]['owners_after'][0] == bob.public_key

Alice is the former owner:

.. ipython::

    In [0]: fulfilled_transfer_tx['fulfillments'][0]['owners_before'][0] == alice.public_key


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

    # NOTE: You may need to change the URL.
    # E.g.: 'http://localhost:9984/api/v1'
    bdb = BigchainDB('http://bdb-server:9984/api/v1')
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


.. _bigchaindb_driver: https://github.com/bigchaindb/bigchaindb-driver


Divisible Assets
----------------

In BigchainDB all assets are non-divisible by default so if we want to make a
divisible asset we need to explicitly mark it as divisible.

Let's continue with the bicycle example. Bob is now the proud owner of the
bicycle and he decides he wants to rent the bicycle. Bob starts by creating a
time sharing token in which 1 token corresponds to 1 hour of riding time:

.. ipython::

    In [0]: bicycle_token = {
       ...:     'divisible': True,
       ...:     'data': {
       ...:         'token_for': {
       ...:             'bicycle': {
       ...:                 'serial_number': 'abcd1234',
       ...:                 'manufacturer': 'bkfab'
       ...:             }
       ...:         },
       ...:         'description': 'Time share token. Each token equals 1 hour of riding.'
       ...:     }
       ...: }

Bob has now decided to issue 10 tokens and assign them to Carly.

.. ipython::

    In [0]: bob, carly = generate_keypair(), generate_keypair()

    In [0]: prepared_token_tx = bdb.transactions.prepare(
       ...:     operation='CREATE',
       ...:     owners_before=bob.public_key,
       ...:     owners_after=[([carly.public_key], 10)],
       ...:     asset=bicycle_token
       ...: )

    In [0]: fulfilled_token_tx = bdb.transactions.fulfill(
       ...:     prepared_token_tx, private_keys=bob.private_key)

Sending the transaction:

.. code-block:: python
 
    >>> sent_token_tx = bdb.transactions.send(fulfilled_token_tx)

.. note:: Defining ``owners_after``.

    For divisible assets we need to specify the amounts togheter with the
    public keys. The way we do this is by passing a ``list`` of ``tuples`` in
    ``owners_after`` in which each ``tuple`` corresponds to a condition.

    For instance instead of creating a transaction with 1 condition with
    ``amount=10`` we could have created a transaction with 2 conditions with
    ``amount=5`` with:

    .. code-block:: python

        owners_after=[([carly.public_key], 5), ([carly.public_key], 5)]

    The reason why the addresses are contained in ``lists`` is because each
    condition can have multiple ownership. For instance we can create a
    condition with ``amount=10`` in which both Carly and Alice are owners
    with:

    .. code-block:: python

        owners_after=[([carly.public_key, alice.public_key], 10)]

.. code-block:: python

    >>> sent_token_tx == fulfilled_token_tx
    True

The ``fulfilled_token_tx`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_token_tx

Bob is the issuer: 

.. ipython::

    In [0]: fulfilled_token_tx['fulfillments'][0]['owners_before'][0] == bob.public_key

Carly is the owner of 10 tokens:

.. ipython::

    In [0]: fulfilled_token_tx['conditions'][0]['owners_after'][0] == carly.public_key

    In [0]: fulfilled_token_tx['conditions'][0]['amount'] == 10


Now Carly wants to ride the bicycle for 2 hours so she needs to send 2 tokens
to Bob:

.. ipython::

    In [0]: cid = 0

    In [0]: condition = prepared_token_tx['conditions'][cid]

    In [0]: transfer_input = {
       ...:     'fulfillment': condition['condition']['details'],
       ...:     'input': {
       ...:         'cid': cid,
       ...:         'txid': prepared_token_tx['id'],
       ...:     },
       ...:     'owners_before': condition['owners_after'],
       ...: }

    In [0]: prepared_transfer_tx = bdb.transactions.prepare(
       ...:     operation='TRANSFER',
       ...:     asset=prepared_token_tx['asset'],
       ...:     inputs=transfer_input,
       ...:     owners_after=[([bob.public_key], 2), ([carly.public_key], 8)]
       ...: )

    In [0]: fulfilled_transfer_tx = bdb.transactions.fulfill(
       ...:     prepared_transfer_tx, private_keys=carly.private_key)

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

.. code-block:: python

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True

When transferring divisible assets BigchainDB makes sure that the amount being
used is the same as the amount being spent. This ensures that no amounts are
lost. For this reason, if Carly wants to transfer 2 tokens of her 10 tokens she
needs to reassign the remaining 8 tokens to herself.

The ``fulfilled_transfer_tx`` with 2 conditions, one with ``amount=2`` and the other
with ``amount=8`` dictionary should look something like:

.. ipython::

    In [0]: fulfilled_transfer_tx
