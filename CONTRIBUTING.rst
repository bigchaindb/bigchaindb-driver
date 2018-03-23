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
4. Follow the pull request template while creating new PRs, the template will
   be visible to you when you create a new pull request.

Tips
----

.. _devenv-docker:

Development Environment with Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Depending on what you are doing, you may need to run at least one BigchainDB
node. You can use the `docker-compose.yml`_ file to run a node, and perform
other tasks that depend on the running node. To run a BigchainDB node, (for
development), you start a MongoDB and Tendermint  node, followed by the linked BigchainDB
node::

    # Implicitly creates a MongoDB and Tendermint instance
    $ docker-compose up -d bigchaindb

You can monitor the logs::

    $ docker-compose logs -f


Tests
~~~~~

To run a subset of tests::

    $ docker-compose run --rm bigchaindb-driver pytest -v tests/test_driver.py

.. important:: When running tests, unless you are targeting a test that does
    not require a connection with the BigchainDB server, you need to run the
    BigchainDB, MongoDB and Tendermint servers::

    $ docker-compose up -d bigchaindb


Dependency on Bigchaindb
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the development requirements, `BigchainDB server Dockerfile <https://github.com/bigchaindb/bigchaindb-driver/blob/master/compose/bigchaindb_server/Dockerfile>`_,
and `.travis.yml <https://github.com/bigchaindb/bigchaindb-driver/blob/master/.travis.yml>`_
are set to depend from BigchainDB's master branch to more easily track changes
against BigchainDB's API.


.. _docker-compose.yml: https://github.com/bigchaindb/bigchaindb-driver/blob/master/docker-compose.yml
