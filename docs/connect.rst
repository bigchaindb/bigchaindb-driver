.. _connect:

===============
Step 2: Connect
===============

If you want to use the BigchainDB Python driver to communicate
with a BigchainDB node or cluster, the first step is to connect to one.
This page explains how to do that.

First, make sure you're using Python 3 and you've
:doc:`installed the bigchaindb_driver Python package <quickstart>`.

Next, in Python, import the :class:`BigchainDB <bigchaindb_driver.BigchainDB>`
class so we can use it to connect:

.. code-block:: python

    from bigchaindb_driver import BigchainDB

Finally, to make the connection, you need to know the BigchainDB Root URL of
the BigchainDB node or cluster where HTTP requests can be sent. There are
several possible cases, listed below.

Case 1: BigchainDB on localhost
-------------------------------

If a BigchainDB node is running locally
(and the ``BIGCHAINDB_SERVER_BIND`` setting wasn't changed
from the default ``localhost:9984``),
you would connect to the local BigchainDB server using:

.. code-block:: python

    bdb = BigchainDB('http://localhost:9984')


Case 2: A Known BigchainDB API Root Endpoint
--------------------------------------------

If you're connecting to a BigchainDB cluster hosted
by someone else, then they'll tell you their
API Root Endpoint.
A BigchainDB API Root endpoint can take many forms.
It can use HTTP or HTTPS.
It can use a hostname or an IP address.
The port might not be 9984.
Here are some examples:

.. code-block:: python

    bdb = BigchainDB('http://example.com:9984')
    bdb = BigchaindB('http://api.example.com:9984')
    bdb = BigchaindB('http://example.com:1234')
    bdb = BigchaindB('http://example.com')  # http is port 80 by default
    bdb = BigchaindB('https://example.com')  # https is port 443 by default
    bdb = BigchaindB('http://12.34.56.123:9984')
    bdb = BigchaindB('http://12.34.56.123:5000')

Case 3: Docker Container on localhost
-------------------------------------

If you are running the Docker-based dev setup that comes along with the
`bigchaindb_driver`_ repository (see :ref:`devenv-docker` for more
information), and wish to connect to it from the ``bdb-driver`` linked
(container) service, use:

.. code-block:: python

    bdb = BigchainDB('http://bdb-server:9984')

Alternatively, you may connect to the containerized BigchainDB node from
"outside", in which case you need to know the port binding:

.. code-block:: bash

    $ docker-compose port bdb-server 9984
    0.0.0.0:32780

.. code-block:: python

    bdb = BigchainDB('http://0.0.0.0:32780')



.. _bigchaindb_driver: https://github.com/bigchaindb/bigchaindb-driver
