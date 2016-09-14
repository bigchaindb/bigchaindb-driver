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

Report bugs at https://github.com/bigchaindb/bigchaindb_driver/issues.

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

The best way to send feedback is to file an issue at https://github.com/bigchaindb/bigchaindb_driver/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `bigchaindb_driver` for local
development.

1. Fork the `bigchaindb_driver` repo on GitHub.
2. Clone your fork locally and enter into the project::

    $ git clone git@github.com:your_name_here/bigchaindb_driver.git
    $ cd bigchaindb_driver/

3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8
   and the tests. For the tests, you'll need to  start the RethinkDB and
   BigchainDB servers::

    $ docker-compose up -d rethinkdb
    $ docker-compose up -d server

6.flake8 check::

    $ docker-compose run --rm driver flake8 bigchaindb_driver tests

7 To run the tests::

    $ docker-compose run --rm driver py.test -v

8.. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, and pass the flake8 check.
   Check https://travis-ci.org/bigchaindb/bigchaindb_driver/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

Dependency on Bigchaindb
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the `BigchainDB server Dockerfile <https://github.com/bigchaindb/bigchaindb-driver/blob/master/compose/server/Dockerfile>`_
and `.travis.yml <https://github.com/bigchaindb/bigchaindb-driver/blob/master/.travis.yml>`_
are set to depend from BigchainDB's master branch to more easily track changes
against BigchainDB's API.

Tests
~~~~~

To run a subset of tests::

    $ docker-compose run --rm driver py.test -v tests/test_driver.py

.. important:: When running tests, unless you are targeting a test that does
    not require a connection with the BigchainDB server, you need to run the
    BigchainDB and RethinkDB servers::

    $ docker-compose up -d rethinkdb
    $ docker-compose up -d server
