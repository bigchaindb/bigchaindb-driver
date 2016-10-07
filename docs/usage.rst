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
        'bicycle': {
            'serial_number': 'abcd1234',
            'manufacturer': 'bkfab',
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
                                          payload=bicycle)

The ``creation_tx`` dictionary should be similar to:

.. code-block:: bash

    {'id': '1dee8db53d86bbba7af7da2b2772ce58c699d29701e8e97bbaa3837a67c265d8',
     'transaction': {'conditions': [{'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '6Nq4cVaKXsdpVLoaqJ8oYto7dSvp3BgzMgj7v8ZMNBuL',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:T-H5zquMLzqRX0U59K1eABKViOq5G_aaJmJb4fLU_As:96'},
        'owners_after': ['6Nq4cVaKXsdpVLoaqJ8oYto7dSvp3BgzMgj7v8ZMNBuL']}],
      'data': {'payload': {'bicycle': {'manufacturer': 'bkfab',
         'serial_number': 'abcd1234'}},
       'uuid': '26bf6f2e-70c5-4bad-88f8-ace9b60b78bb'},
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:T-H5zquMLzqRX0U59K1eABKViOq5G_aaJmJb4fLU_Atx3Abk4qmD5PNcI4R48Dxar9rYpbNoyLmD4jvkZK-x6XVQcEaIZKVmuLIxEpwbHuuuEBfPMk32Fl6vMo8zk2AF',
        'input': None,
        'owners_before': ['6Nq4cVaKXsdpVLoaqJ8oYto7dSvp3BgzMgj7v8ZMNBuL']}],
      'operation': 'CREATE',
      'timestamp': '1475749690'},
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
        creation_tx, bob.verifying_key, signing_key=alice.signing_key)

The ``transfer_tx`` dictionary should look something like:

.. code-block:: bash

    {'id': '8d89f9c97ddea72feee1286f428e38ab1479e9f2014c817a15eecfd661325312',
     'transaction': {'conditions': [{'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': 'CQztMZFEWJwF3Qf81vnGv6H15m6HUJ6LAcEj8FeUYNn2',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:qZZdtaETW9Ax-a-vqLJ4HHFoPe7uHjRncMtlC3Lzqs8:96'},
        'owners_after': ['CQztMZFEWJwF3Qf81vnGv6H15m6HUJ6LAcEj8FeUYNn2']}],
      'data': None,
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:T-H5zquMLzqRX0U59K1eABKViOq5G_aaJmJb4fLU_AsuvYww_nA3GtZvLmXeEvOIiAC0UyyyyihNcmm4WGKK7ot-i-ychkR5NpfIzxVOOXzrM14chmMJoi9W-QGW5woG',
        'input': {'cid': 0,
         'txid': '1dee8db53d86bbba7af7da2b2772ce58c699d29701e8e97bbaa3837a67c265d8'},
        'owners_before': ['6Nq4cVaKXsdpVLoaqJ8oYto7dSvp3BgzMgj7v8ZMNBuL']}],
      'operation': 'TRANSFER',
      'timestamp': '1475749812'},
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

    bdb = BigchainDB('http://bdb-server:9984/api/v1')
    txid = '12345'
    try:
        status = bdb.transactions.status(txid)
    except NotFoundError as e:
        logger.error('Transaction "%s" could was not found.',
                     txid,
                     extra={'status': e.status_code})

Running the above code should give something similar to:

.. code-block:: bash

    2016-09-29 15:06:30,606 404 Transaction "12345" could was not found.


.. _bigchaindb_driver: https://github.com/bigchaindb/bigchaindb-driver
