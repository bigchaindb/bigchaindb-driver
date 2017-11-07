.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/bigchaindb/bigchaindb-driver/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

bigchaindb-driver could always use more documentation, whether as part of the
official bigchaindb-driver docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/bigchaindb/bigchaindb-driver/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute?
See the :doc:`Installation Guide for Developers <quickstart>` page.


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, and pass the flake8 check.
   Check https://travis-ci.org/bigchaindb/bigchaindb-driver/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

.. _devenv-docker:

Development Environment with Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Depending on what you are doing, you may need to run at least one BigchainDB
node. You can use the `docker-compose.yml`_ file to run a node, and perform
other tasks that depend on the running node. To run a BigchainDB node, (for
development), you start a MongoDB node, followed by the linked BigchainDB
node::

    $ docker-compose up -d db
    $ docker-compose up -d bdb-server

You can monitor the logs::

    $ docker-compose logs -f


Tests
~~~~~

To run a subset of tests::

    $ docker-compose run --rm bdb pytest -v tests/test_driver.py

.. important:: When running tests, unless you are targeting a test that does
    not require a connection with the BigchainDB server, you need to run the
    BigchainDB and MongoDB servers::

    $ docker-compose up -d db
    $ docker-compose up -d bdb-server


Using RethinkDB as the backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default docker-compose file runs MongoDB as a backend. In order to work
with RethinkDB, one has to use the ``docker-compose.rdb.yml`` file, which
implies working with `multiple compose files`_. The workflow is the same as
with MongoDB.

First start RethinkDB::

    $ docker-compose -f docker-compose.rdb.yml up -d db

then one BigchainDB server node::

    $ docker-compose -f docker-compose.rdb.yml up -d bdb-server

and run the tests::

    $ docker-compose -f docker-compose.rdb.yml run --rm bdb pytest -v


Dependency on Bigchaindb
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the development requirements, `BigchainDB server Dockerfile <https://github.com/bigchaindb/bigchaindb-driver/blob/master/compose/server/Dockerfile>`_,
and `.travis.yml <https://github.com/bigchaindb/bigchaindb-driver/blob/master/.travis.yml>`_
are set to depend from BigchainDB's master branch to more easily track changes
against BigchainDB's API.


.. _docker-compose.yml: https://github.com/bigchaindb/bigchaindb-driver/blob/master/docker-compose.yml
.. _multiple compose files: https://docs.docker.com/compose/extends/#multiple-compose-files
