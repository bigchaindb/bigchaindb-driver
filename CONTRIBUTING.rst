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

Ready to contribute? Here's how to set up `bigchaindb-driver`_ for local
development.

1. Fork the `bigchaindb-driver`_ repo on GitHub.
2. Clone your fork locally and enter into the project::

    $ git clone git@github.com:your_name_here/bigchaindb-driver.git
    $ cd bigchaindb-driver/

3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, check that your changes pass flake8
   and the tests. For the tests, you'll need to  start the RethinkDB and
   BigchainDB servers::

    $ docker-compose up -d rdb
    $ docker-compose up -d bdb-server

5. flake8 check::

    $ docker-compose run --rm bdb-driver flake8 bigchaindb_driver tests

6. To run the tests::

    $ docker-compose run --rm bdb-driver pytest -v

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.


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
development), you start a RethinkDB node, followed by the linked BigchainDB
node::

    $ docker-compose up -d rdb
    $ docker-compose up -d bdb-server

You can monitor the logs::

    $ docker-compose logs -f


Tests
~~~~~

To run a subset of tests::

    $ docker-compose run --rm bdb-driver pytest -v tests/test_driver.py

.. important:: When running tests, unless you are targeting a test that does
    not require a connection with the BigchainDB server, you need to run the
    BigchainDB and RethinkDB servers::

    $ docker-compose up -d rdb 
    $ docker-compose up -d bdb-server


Dependency on Bigchaindb
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the development requirements, `BigchainDB server Dockerfile <https://github.com/bigchaindb/bigchaindb-driver/blob/master/compose/server/Dockerfile>`_,
and `.travis.yml <https://github.com/bigchaindb/bigchaindb-driver/blob/master/.travis.yml>`_
are set to depend from BigchainDB's master branch to more easily track changes
against BigchainDB's API.


.. _bigchaindb-driver: https://github.com/bigchaindb/bigchaindb-driver
.. _docker-compose.yml: https://github.com/bigchaindb/bigchaindb-driver/blob/master/docker-compose.yml
