=====
Usage
=====
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
We're now ready to create the digital asset.

Let's first connect to a BigchainDB node:

.. code-block:: python

    creation_tx = bdb.transactions.create(verifying_key=alice.verifying_key,
                                          signing_key=alice.signing_key,
                                          asset=bicycle)

The ``creation_tx`` dictionary should be similar to:

.. code-block:: bash

    {'id': '9da5e3bfd34725b9c0a40c491bd27c23f4b225e027ce2f51a8c99e9fbd02d97a',
     'transaction': {'asset': {'data': {'bicycle': {'manufacturer': 'bkfab',
         'serial_number': 'abcd1234'}},
       'divisible': False,
       'id': 'd6a3b850-e960-4391-98c3-f16f1cd26a40',
       'refillable': False,
       'updatable': False},
      'conditions': [{'amount': 1,
        'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '3EnDZNgf9Ss7cEdiPaSJ8NZDbVjRE5aXG1UT9aoE7kRj',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:IT8NBLRPBWXt8qNmYlYaqVxux_KWfKiiymxeuqkIVmY:96'},
        'owners_after': ['3EnDZNgf9Ss7cEdiPaSJ8NZDbVjRE5aXG1UT9aoE7kRj']}],
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:IT8NBLRPBWXt8qNmYlYaqVxux_KWfKiiymxeuqkIVmYx2pP5XyS2KZJ3jN90hJausCTqaycqQZh4g8MczME8kSM4ApfrQs_3w6Uz4ZkcjhzxcUz2FXsysljqGIaLVaoL',
        'input': None,
        'owners_before': ['3EnDZNgf9Ss7cEdiPaSJ8NZDbVjRE5aXG1UT9aoE7kRj']}],
      'metadata': None,
      'operation': 'CREATE',
      'timestamp': '1476809307'},
     'version': 1}


Notice the transaction ``id``:

.. code-block:: python
 
    >>> txid = creation_tx['id']
    >>> txid
    '1dee8db53d86bbba7af7da2b2772ce58c699d29701e8e97bbaa3837a67c265d8'


Asset Transfer
--------------
Imagine some time goes by, during which Alice is happy with her bicycle, and
one day, she meets Bob, who is interested in acquiring her bicycle. The timing
is good for Alice as she had been wanting to get a new bicycle.

To transfer the bicycle (asset) to Bob, Alice first retrieves the transaction
in which the bicycle (asset) had been created:

.. code-block:: python

    creation_tx = bdb.transactions.retrieve(txid)

and then transfers it to Bob:

.. code-block:: python
    
    transfer_tx = bdb.transactions.transfer(
        creation_tx,
        bob.verifying_key,
        asset=creation_tx['transaction']['asset'],
        signing_key=alice.signing_key,
    )

The ``transfer_tx`` dictionary should look something like:

.. code-block:: bash

    {'id': 'ad1b4294bd6e255a579f51ae020be60da32256b0da979fd3df4ac6130e8eeed1',
     'transaction': {'asset': {'id': 'd6a3b850-e960-4391-98c3-f16f1cd26a40'},
      'conditions': [{'amount': 1,
        'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '35WbK4tqJWy4z98TzBr83iekhyY4xUmNWabiC9FQoEwp',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:Ht8oCVawCLOMNS758n5Q-5eFhxYr_xXbQ6X7AYsJZB8:96'},
        'owners_after': ['35WbK4tqJWy4z98TzBr83iekhyY4xUmNWabiC9FQoEwp']}],
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:IT8NBLRPBWXt8qNmYlYaqVxux_KWfKiiymxeuqkIVmac1bLg24vkQ_rW7BMnJFsvUjn1J8gwFbcr5q8WqUCCnRe_uBrEvxwiAG9aPlldkh8YjHibHdkLzTKEJJE41BAK',
        'input': {'cid': 0,
         'txid': '9da5e3bfd34725b9c0a40c491bd27c23f4b225e027ce2f51a8c99e9fbd02d97a'},
        'owners_before': ['3EnDZNgf9Ss7cEdiPaSJ8NZDbVjRE5aXG1UT9aoE7kRj']}],
      'metadata': None,
      'operation': 'TRANSFER',
      'timestamp': '1476809389'},
     'version': 1}


Bob is the new owner: 

.. code-block:: python

    >>> transfer_tx['transaction']['conditions'][0]['owners_after'][0] == bob.verifying_key
    True

Alice is the former owner:

.. code-block:: python

    >>> transfer_tx['transaction']['fulfillments'][0]['owners_before'][0] == alice.verifying_key
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
