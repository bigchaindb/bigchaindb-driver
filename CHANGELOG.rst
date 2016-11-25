=========
Changelog
=========

0.0.3 (2016-11-25)
------------------
Added
^^^^^
* Support for "canonical" transaction operations:
    
    * ``prepare``
    * ``fulfill``
    * ``send``

Deprecated
^^^^^^^^^^
* ``create()`` and ``transfer()`` under ``TransactionEndpoint``, and available
  via ``BigchainDB.transactions``. Replaced by the above three "canonical"
  transaction operations: ``prepare()``, ``fulfill()``, and ``send()``.

Fixed
^^^^^
* ``BigchainDB()`` default node setting on its transport class. See commit
  `0a80206 <https://github.com/bigchaindb/bigchaindb-driver/commit/0a80206407ef155d220d25a337dc9a4f51046e70>`_


0.0.2 (2016-10-28)
------------------

Added
^^^^^
* Support for BigchainDB server 0.7.0


0.0.1dev1 (2016-08-25)
----------------------

* Development (pre-alpha) release on PyPI.

Added
^^^^^
* Minimal support for ``POST`` (via ``create()`` and ``transfer()``), and
  ``GET`` operations on the ``/transactions`` endpoint.


0.0.1a1 (2016-08-12)
--------------------

* Planning release on PyPI.
