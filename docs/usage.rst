=====
Usage
=====

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


Connecting to a BigchainDB Node
-------------------------------
Connecting to a BigchainDB node, is done via the
:class:`BigchainDB class <bigchaindb_driver.BigchainDB>`:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

    bdb = BigchainDB('http://bdb-server:9984/api/v1')

.. note:: The URL you pass to :class:`~bigchaindb_driver.BigchainDB` needs to
    be pointing to a running server node. In the current example, it implies
    that you are running the docker-based dev setup that comes along with the
    `bigchaindb_driver`_ repository. See :ref:`devenv-docker` for instructions.

Asset Creation
--------------
We're now ready to create the digital asset.

Let's first connect to a BigchainDB node:

.. code-block:: python

    creation_tx = bdb.transactions.create(verifying_key=alice.verifying_key,
                                          signing_key=alice.signing_key)

The ``creation_tx`` dictionary should be similar to:

.. code-block:: bash

    {'id': 'b795cc579436d743b0e63ac00fecce8d79dd9ed5c450be9aaf7d916e53c118f5',
     'transaction': {'conditions': [{'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '6h93weebF6Zn8RwV9Kejcwmzbfcb3Rv8srPQeuuzRjZi',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:VJLFHYncUMIXusBIghrOVLXPAmec9VJWx6NJl0_9MKE:96'},
        'owners_after': ['6h93weebF6Zn8RwV9Kejcwmzbfcb3Rv8srPQeuuzRjZi']}],
      'data': None,
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:VJLFHYncUMIXusBIghrOVLXPAmec9VJWx6NJl0_9MKHONkikhxXjNFY03EW4c0MJFvsHYTZh97QxMM2ZBeoiljjge5Tn7wPoILjyLShEALQ9gzf_QK44KboStzpw0nUB',
        'input': None,
        'owners_before': ['6h93weebF6Zn8RwV9Kejcwmzbfcb3Rv8srPQeuuzRjZi']}],
      'operation': 'CREATE',
      'timestamp': '1474467828'},
     'version': 1}


Notice the transaction ``id``:

.. code-block:: python
 
    >>> txid = creation_tx['id']
    >>> txid
    'b795cc579436d743b0e63ac00fecce8d79dd9ed5c450be9aaf7d916e53c118f5'


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

    {'id': 'a28e86a93173350f51e8f5661b07def2e2e3399eaaad179d29ec2155e05e7413',
     'transaction': {'conditions': [{'cid': 0,
        'condition': {'details': {'bitmask': 32,
          'public_key': '3op6F4aU4kQhXVYG9tkEPM7AXJftAFTKjqM9iv11gBhQ',
          'signature': None,
          'type': 'fulfillment',
          'type_id': 4},
         'uri': 'cc:4:20:KbVWGmfin6ueqTPS62z3IoAEFY-bjYIVJU8oCQtCImc:96'},
        'owners_after': ['3op6F4aU4kQhXVYG9tkEPM7AXJftAFTKjqM9iv11gBhQ']}],
      'data': None,
      'fulfillments': [{'fid': 0,
        'fulfillment': 'cf:4:VJLFHYncUMIXusBIghrOVLXPAmec9VJWx6NJl0_9MKESz8EdircaOtIsIWhoK8XnddCIzNh__MaDEp026OIkH7SkLeAP5bEIcwjzHWefazle8NsTQmZraR4FEbPhV1cM',
        'input': {'cid': 0,
         'txid': 'b795cc579436d743b0e63ac00fecce8d79dd9ed5c450be9aaf7d916e53c118f5'},
        'owners_before': ['6h93weebF6Zn8RwV9Kejcwmzbfcb3Rv8srPQeuuzRjZi']}],
      'operation': 'TRANSFER',
      'timestamp': '1474468018'},
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
