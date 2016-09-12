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

    .. automethod:: __init__

.. autoclass:: NamespacedDriver
    :members:

    .. automethod:: __init__

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

.. autoclass:: BigchaindbException

.. autoclass:: TransportError

.. autoclass:: ConnectionError

.. autoclass:: NotFoundError

.. autoclass:: KeypairNotFoundException

.. autoclass:: InvalidSigningKey

.. autoclass:: InvalidVerifyingKey
