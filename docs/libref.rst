Library Reference
=================

.. automodule:: bigchaindb_driver

``driver``
----------

.. autoclass:: BigchainDB
    :members:

    .. automethod:: __init__

.. automodule:: bigchaindb_driver.driver

.. autoclass:: TransactionsEndpoint
    :members:

.. autoclass:: OutputsEndpoint
    :members:

.. autoclass:: NamespacedDriver
    :members:

    .. automethod:: __init__


``offchain``
------------
.. automodule:: bigchaindb_driver.offchain
.. autofunction::  prepare_transaction
.. autofunction::  prepare_create_transaction
.. autofunction::  prepare_transfer_transaction
.. autofunction::  fulfill_transaction


``transport``
-------------
.. automodule:: bigchaindb_driver.transport

.. autoclass:: Transport
    :members:

    .. automethod:: __init__

``pool``
--------
.. automodule:: bigchaindb_driver.pool

.. autoclass:: Pool
    :members:

    .. automethod:: __init__

.. autoclass:: RoundRobinPicker
    :members:

    .. automethod:: __init__

.. autoclass:: AbstractPicker
    :members:


``connection``
--------------
.. automodule:: bigchaindb_driver.connection

.. autoclass:: Connection
    :members:

    .. automethod:: __init__


``crypto``
----------
.. automodule:: bigchaindb_driver.crypto
    :members:


``exceptions``
--------------

.. automodule:: bigchaindb_driver.exceptions

.. autoexception:: BigchaindbException

.. autoexception:: TransportError

.. autoexception:: ConnectionError

.. autoexception:: NotFoundError

.. autoexception:: KeypairNotFoundException

.. autoexception:: InvalidPrivateKey

.. autoexception:: InvalidPublicKey

.. autoexception:: MissingPrivateKeyError


``utils``
---------

.. automodule:: bigchaindb_driver.utils
    :members:
    :private-members:
