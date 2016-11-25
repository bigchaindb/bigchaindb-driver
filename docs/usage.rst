====================
Basic Usage Examples
====================

.. note::

   You must :doc:`install the bigchaindb_driver Python package <quickstart>` first.

   You should use Python 3 for these examples.


The BigchainDB driver's main purpose is to connect to one or more BigchainDB
server nodes, in order to perform supported API calls (such as
:http:post:`creating a transaction </transactions/>`, or
:http:get:`retrieving a transaction </transactions/{tx_id}>`). 

Connecting to a BigchainDB node, is done via the
:class:`BigchainDB class <bigchaindb_driver.BigchainDB>`:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('<api_endpoint>')

where ``<api_endpoint>`` is the root URL of the BigchainDB server API you wish
to connect to. 

If you do not know the URL, and have access to the server, you
can use the BigchainDB server command line. For instance, for the simplest case
in which a BigchainDB node would be running locally:

.. code-block:: bash

    $ bigchaindb show-config | grep api_endpoint
        "api_endpoint": "http://localhost:9984/api/v1",

You would then connect to the local BigchainDB server this way:

.. code-block:: python

    bdb = BigchainDB('http://localhost:9984/api/v1')

If you are running the docker-based dev setup that comes along with the
`bigchaindb_driver`_ repository (see :ref:`devenv-docker` for more
information), and wish to connect to it from the ``bdb-driver`` linked
(container) service:

.. code-block:: bash

    $ docker-compose run --rm bdb-server bigchaindb show-config | grep api_endpoint
        "api_endpoint": "http://bdb-server:9984/api/v1",

.. code-block:: bash
    
    $ docker-compose run --rm bdb-driver python

.. code-block:: python

    >>> from bigchaindb_driver import BigchainDB
    >>> bdb = BigchainDB('http://bdb-server:9984/api/v1')

Alternatively, you may connect to the containerized BigchainDB node from
"outside", in which case you need to know the port binding:

.. code-block:: bash
    
    $ docker-compose port bdb-server 9984
    0.0.0.0:32780

.. code-block:: python

    >>> from bigchaindb_driver import BigchainDB
    >>> bdb = BigchainDB('http://0.0.0.0:32780/api/v1')


Digital Asset Definition
------------------------
As an example, let's consider the creation and transfer of a digital asset that
represents a bicycle:

.. code-block:: python
    
    bicycle = {
        'data': {
            'bicycle': {
                'serial_number': 'abcd1234',
                'manufacturer': 'bkfab',
            },
        },
    }

We'll suppose that the bike belongs to Alice, and that it will be transferred
to Bob.


Metadata Definition (*optional*)
--------------------------------
You can `optionally` add metadata to a transaction. Any dictionary is accepted.

For example:

.. code-block:: python

    metadata = {'planet': 'earth'}


Cryptographic Identities Generation
-----------------------------------
Alice, and Bob are represented by signing/verifying key pairs. The signing
(private) key is used to sign transactions, meanwhile the verifying (public)
key is used to verify that a signed transaction was indeed signed by the one
who claims to be the signee. 

.. code-block:: python

    from bigchaindb_driver.crypto import generate_keypair

    alice, bob = generate_keypair(), generate_keypair()


Asset Creation
--------------
We're now ready to create the digital asset. First we prepare the transaction:

.. code-block:: python

   prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        owners_before=alice.verifying_key,
        asset=bicycle,
        metadata=metadata,
   )

The ``prepared_creation_tx`` dictionary should be similar to:

.. code-block:: bash

    {'id': 'f713f1c662bcf7e72805c51222b82d0408df5a0cadddfb040d9a2e7171204471',
     'transaction': {'asset': {'data': {'bicycle': {'manufacturer': 'bkfab',
         'serial_number': 'abcd1234'}},
       'divisible': False,
       'id': 'd591879f-aa02-417a-825a-f55154676f00',
       'refillable': False,
       'updatable': False},
      'conditions': [{'amount': 1,
        'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:IMe7QSL5xRAYIlXon76ZonWktR0NI02M8rAG1bN-ugg:96'},
        'owners_after': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
      'fulfillments': [{'fid': 0,
        'fulfillment': {'bitmask': 32,
         'public_key': '3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf',
         'signature': None,
         'type': 'fulfillment',
         'type_id': 4},
        'input': None,
        'owners_before': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
      'metadata': {'data': {'planet': 'earth'},
       'id': '4d406690-d6e3-48b2-ac64-9fff714f0ff3'},
      'operation': 'CREATE',
     'version': 1}

The transaction needs to be fulfilled:

.. code-block:: python

    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.signing_key)

.. code-block:: python

    >>> fulfilled_creation_tx
    {'id': 'f713f1c662bcf7e72805c51222b82d0408df5a0cadddfb040d9a2e7171204471',
     'transaction': {'asset': {'data': {'bicycle': {'manufacturer': 'bkfab',
         'serial_number': 'abcd1234'}},
       'divisible': False,
       'id': 'd591879f-aa02-417a-825a-f55154676f00',
       'refillable': False,
       'updatable': False},
      'conditions': [{'amount': 1,
        'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:IMe7QSL5xRAYIlXon76ZonWktR0NI02M8rAG1bN-ugg:96'},
        'owners_after': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:IMe7QSL5xRAYIlXon76ZonWktR0NI02M8rAG1bN-ugjCpOCtzI1L59uV2Mw7wg2bHAnzj5AyA0dXkquAeENBAsSR0DVhKFUf3JH7Ii2gPqhln7rlOYpk8EsQKLD6K2YJ',
        'input': None,
        'owners_before': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
      'metadata': {'data': {'planet': 'earth'},
       'id': '4d406690-d6e3-48b2-ac64-9fff714f0ff3'},
      'operation': 'CREATE',
     'version': 1}

And sent over to a BigchainDB node:

.. code-block:: python

    sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)

.. code-block:: python

    >>> sent_creation_tx == fulfilled_creation_tx
    True

Notice the transaction ``id``:

.. code-block:: python

    >>> txid = sent_creation_tx['id']
    >>> txid
    'f713f1c662bcf7e72805c51222b82d0408df5a0cadddfb040d9a2e7171204471'

To check the status of the transaction:

.. code-block:: python

    >>> bdb.transactions.status(txid)
    {'status': 'valid'}


Asset Transfer
--------------
Imagine some time goes by, during which Alice is happy with her bicycle, and
one day, she meets Bob, who is interested in acquiring her bicycle. The timing
is good for Alice as she had been wanting to get a new bicycle.

To transfer the bicycle (asset) to Bob, Alice first retrieves the transaction
in which the bicycle (asset) had been created:

.. code-block:: python

    creation_tx = bdb.transactions.retrieve(txid)

and then prepares a transfer transaction:

.. code-block:: python
    
    cid = 0
    condition = creation_tx['transaction']['conditions'][cid]
    transfer_input = {
        'fulfillment': condition['condition']['details'],
        'input': {
            'cid': cid,
            'txid': creation_tx['id'],
        },
        'owners_before': condition['owners_after'],
    }

    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=creation_tx['transaction']['asset'],
        inputs=transfer_input,
        owners_after=bob.verifying_key,
    )

and then fulfills the prepared transfer:

.. code-block:: python

    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=alice.signing_key,
    )

and finally sends the fulfilled transaction to the connected BigchainDB node:

.. code-block:: python

    >>> sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

.. code-block:: python

    >>> sent_transfer_tx == fulfilled_transfer_tx
    True

The ``sent_transfer_tx`` dictionary should look something like:

.. code-block:: bash

    {'id': '554dc17744baa9c2d954022f4ed49a9672c8a497ac0ae37a30cf3be20c9f8000',
     'transaction': {'asset': {'id': 'd591879f-aa02-417a-825a-f55154676f00'},
      'conditions': [{'amount': 1,
        'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': 'EcRawy3Y22eAUSS94vLF8BVJi62wbqbD9iSUSUNU9wAA',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:yjsOmwsugrgj_QAcdaLZdZWKHWTB2T5yVmBf8IfdV_s:96'},
        'owners_after': ['EcRawy3Y22eAUSS94vLF8BVJi62wbqbD9iSUSUNU9wAA']}],
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:IMe7QSL5xRAYIlXon76ZonWktR0NI02M8rAG1bN-ugjQ2I3H7d2hUHgJhY-8CipIxnCrmF554ZKsZTGxjA86Y68MJR9kRC_270x9DejFGSg7DKJ1kRjen8DevtYWCg0B',
        'input': {'cid': 0,
         'txid': 'f713f1c662bcf7e72805c51222b82d0408df5a0cadddfb040d9a2e7171204471'},
        'owners_before': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
      'metadata': None,
      'operation': 'TRANSFER',
     'version': 1}

Bob is the new owner: 

.. code-block:: python

    >>> sent_transfer_tx['transaction']['conditions'][0]['owners_after'][0] == bob.verifying_key
    True

Alice is the former owner:

.. code-block:: python

    >>> sent_transfer_tx['transaction']['fulfillments'][0]['owners_before'][0] == alice.verifying_key
    True


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

Lets continue with the bicycle example. Bob is now the proud owner of the
bicycle and he decides he wants to rent the bicycle. Bob starts by creating a
time sharing token in which 1 token corresponds to 1 hour of riding time:

.. code-block:: python

    bicycle_token = {
        'divisible': True,
        'data': {
            'token_for': {
                'bicycle': {
                    'serial_number': 'abcd1234',
                    'manufacturer': 'bkfab'
                }
            },
            'description': 'Time share token. Each token equals 1 hour of riding.'
        }
    }

Bob has now decided to issue 10 tokens and assign them to Carly.

.. code-block:: python

    bob, carly = generate_keypair(), generate_keypair()

    prepared_token_tx = bdb.transactions.prepare(
        operation='CREATE',
        owners_before=bob.verifying_key,
        owners_after=[([carly.verifying_key], 10)]
        asset=bicycle_token
    )

    fulfilled_token_tx = bdb.transactions.fulfill(
        prepared_token_tx, private_keys=bob.signing_key)

    sent_token_tx = bdb.transactions.send(fulfilled_token_tx)

.. note:: Defining ``owners_after``.

    For divisible assets we need to specify the amounts togheter with the
    public keys. The way we do this is by passing a ``list`` of ``tuples`` in
    ``owners_after`` in which each ``tuple`` corresponds to a condition.

    For instance instead of creating a transaction with 1 condition with
    ``amount=10`` we could have created a transaction with 2 conditions with
    ``amount=5`` with:

    .. code-block:: python

        owners_after=[([carly.verifying_key], 5), ([carly.verifying_key], 5)]

    The reason why the addresses are contained in ``lists`` its because each
    condition can have multiple ownership. For instance we can create a
    condition with ``amount=10`` in which both Carly and Alice are owners
    with:

    .. code-block:: python

        owners_after=[([carly.verifying_key, alice.verifying_key], 10)]

The ``sent_token_tx`` dictionary should look something like:

.. code-block:: bash

   {'id': 'd97f44d490fc6865d30d1192394cac40a3651872a463f5b8e60c153ef2ae495f',
 'transaction': {'asset': {'data': {'description': 'Time share token. Each token equals 1 hour of riding.',
    'token_for': {'bicycle': {'manufacturer': 'bkfab',
      'serial_number': 'abcd1234'}}},
   'divisible': True,
   'id': 'fb5769e3-e9f3-4b8c-98a2-4604d93a7aeb',
   'refillable': False,
   'updatable': False},
  'conditions': [{'amount': 10,
    'cid': 0,
    'condition': {'details': {'bitmask': 32,
      'public_key': 'GTqE9XHunryuBrS9pkyzLUMTTDKaa1vqqirF4fHFTf7f',
      'signature': None,
      'type': 'fulfillment',
      'type_id': 4},
     'uri': 'cc:4:20:5b7vXE_5Ht2_vfc1D8P7Pak5PRMSePAFhtH79e71Zso:96'},
    'owners_after': ['GTqE9XHunryuBrS9pkyzLUMTTDKaa1vqqirF4fHFTf7f']}],
  'fulfillments': [{'fid': 0,
    'fulfillment': 'cf:4:d5mfbc9zapn7oAoYgX_tX9fzLiLCfDdLOC94tVswcYyJ-NW5L959kw0TLw3SpsJdDKcw1KQKWRZ2xzS4xAnMNbjgK9WRYvXGHYV7SOhrOWJoRAyNqjlMmdTRdGzHUNwC',
    'input': None,
    'owners_before': ['93sP5ycRLRRxsec15HDpaa1u1bBSeo17XEVJSHSArbZm']}],
  'metadata': None,
  'operation': 'CREATE'},
 'version': 1} 

Bob is the issuer: 

.. code-block:: python

    >>> sent_token_tx['transaction']['fulfillments'][0]['owners_before'][0] == bob.verifying_key
    True

Carly is the owner of 10 tokens:

.. code-block:: python

    >>> sent_token_tx['transaction']['conditions'][0]['owners_after'][0] == carly.verifying_key
    True
    >>> sent_token_tx['transaction']['conditions'][0]['amount'] == 10
    True


Now Carly wants to ride the bicycle for 2 hours so she needs to send 2 tokens
to Bob:

.. code:: python

    cid = 0
    condition = prepared_token_tx['transaction']['conditions'][cid]
    transfer_input = {
        'fulfillment': condition['condition']['details'],
        'input': {
            'cid': cid,
            'txid': prepared_token_tx['id'],
        },
        'owners_before': condition['owners_after'],
    }

    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=prepared_token_tx['transaction']['asset'],
        inputs=transfer_input,
        owners_after=[([bob.verifying_key], 2), ([carly.verifying_key], 8)]
    )

    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx, private_keys=carly.signing_key)

    sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

When transferring divisible assets BigchainDB makes sure that the amount being
used is the same as the amount being spent. This ensures that no amounts are
lost. For this reason, if Carly wants to transfer 2 tokens of her 10 tokens she
needs to reassign the remaining 8 tokens to herself.

The ``sent_transfer_tx`` with 2 conditions, one with ``amount=2`` and the other
with ``amount=8`` dictionary should look something like:

.. code-block:: bash

	{'id': '773ad928417859350bdc999899b7e5815bce58527ea49b852c11076ab79751a3',
	 'transaction': {'asset': {'id': 'fb5769e3-e9f3-4b8c-98a2-4604d93a7aeb'},
	  'conditions': [{'amount': 2,
		'cid': 0,
		'condition': {'details': {'bitmask': 32,
		  'public_key': '93sP5ycRLRRxsec15HDpaa1u1bBSeo17XEVJSHSArbZm',
		  'signature': None,
		  'type': 'fulfillment',
		  'type_id': 4},
		 'uri': 'cc:4:20:d5mfbc9zapn7oAoYgX_tX9fzLiLCfDdLOC94tVswcYw:96'},
		'owners_after': ['93sP5ycRLRRxsec15HDpaa1u1bBSeo17XEVJSHSArbZm']},
	   {'amount': 8,
		'cid': 1,
		'condition': {'details': {'bitmask': 32,
		  'public_key': 'GTqE9XHunryuBrS9pkyzLUMTTDKaa1vqqirF4fHFTf7f',
		  'signature': None,
		  'type': 'fulfillment',
		  'type_id': 4},
		 'uri': 'cc:4:20:5b7vXE_5Ht2_vfc1D8P7Pak5PRMSePAFhtH79e71Zso:96'},
		'owners_after': ['GTqE9XHunryuBrS9pkyzLUMTTDKaa1vqqirF4fHFTf7f']}],
	  'fulfillments': [{'fid': 0,
		'fulfillment': 'cf:4:5b7vXE_5Ht2_vfc1D8P7Pak5PRMSePAFhtH79e71ZsqNmkEEwI1gt-2Xk9T-3-gxOo8vOS8itIPMM7SrARJWVruH4ORFH7kVqis1gsBM54pP39FBD3T_jjCuWu75HTcO',
		'input': {'cid': 0,
		 'txid': 'd97f44d490fc6865d30d1192394cac40a3651872a463f5b8e60c153ef2ae495f'},
		'owners_before': ['GTqE9XHunryuBrS9pkyzLUMTTDKaa1vqqirF4fHFTf7f']}],
	  'metadata': None,
	  'operation': 'TRANSFER'},
	 'version': 1}
