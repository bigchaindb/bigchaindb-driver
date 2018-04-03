.. _connect:

=================================
Determine the BigchainDB Root URL
=================================

If you want to use the BigchainDB Python Driver
to communicate with a BigchainDB node or cluster,
then you will need its BigchainDB Root URL.
This page is to help you determine it.


Case 1: BigchainDB on localhost
-------------------------------

If a BigchainDB node is running locally
(and the ``BIGCHAINDB_SERVER_BIND`` setting wasn't changed
from the default ``localhost:9984``),
then the BigchainDB Root URL is:

.. code-block:: python

   bdb_root_url = 'http://localhost:9984'


Case 2: A Cluster Hosted by Someone Else
----------------------------------------

If you're connecting to a BigchainDB cluster hosted
by someone else, then they'll tell you their
BigchaindB Root URL.
It can take many forms.
It can use HTTP or HTTPS.
It can use a hostname or an IP address.
The port might not be 9984.
Here are some examples:

.. code-block:: python

    bdb_root_url = 'http://example.com:9984'
    bdb_root_url = 'http://api.example.com:9984'
    bdb_root_url = 'http://example.com:1234'
    bdb_root_url = 'http://example.com'  # http is port 80 by default
    bdb_root_url = 'https://example.com'  # https is port 443 by default
    bdb_root_url = 'http://12.34.56.123:9984'
    bdb_root_url = 'http://12.34.56.123:5000'

Case 3: Docker Container on localhost
-------------------------------------

If you are running the Docker-based dev setup that comes along with the
`bigchaindb_driver`_ repository (see :ref:`devenv-docker` for more
information), and wish to connect to it from the ``bdb-driver`` linked
(container) service, use:

.. code-block:: python

    bdb_root_url = 'http://bdb-server:9984'

Alternatively, you may connect to the containerized BigchainDB node from
"outside", in which case you need to know the port binding:

.. code-block:: bash

    $ docker-compose port bigchaindb 9984
    0.0.0.0:32780

.. code-block:: python

    bdb_root_url = 'http://0.0.0.0:32780'


Next, try some of the :doc:`basic usage examples <usage>`.


.. _bigchaindb_driver: https://github.com/bigchaindb/bigchaindb-driver
