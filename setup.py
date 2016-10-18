#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

install_requires = [
    'bigchaindb_common>=0.0.6',
    'requests>=2.11.0',
]

tests_require = [
    'tox>=2.3.1',
    'coverage>=4.1',
    'flake8>=2.6.0',
    'pytest>=3.0.1',
    'pytest-cov',
    'pytest-sugar',
    'pytest-xdist',
    'responses',
    'bigchaindb',
]

dev_require = [
    'ipdb',
    'ipython',
]

docs_require = [
    'Sphinx>=1.3.5',
    'sphinx-autobuild',
    'sphinxcontrib-napoleon>=0.4.4',
    'sphinx_rtd_theme',
    'sphinxcontrib-httpdomain',
]

setup(
    name='bigchaindb_driver',
    version='0.0.2.dev11',
    description="Python driver for BigchainDB",
    long_description=readme + '\n\n' + history,
    author="BigchainDB",
    author_email='dev@bigchaindb.com',
    url='https://github.com/bigchaindb/bigchaindb_driver',
    packages=[
        'bigchaindb_driver',
    ],
    package_dir={'bigchaindb_driver':
                 'bigchaindb_driver'},
    include_package_data=True,
    install_requires=install_requires,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='bigchaindb_driver',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    extras_require={
        'test': tests_require,
        'dev': dev_require + tests_require + docs_require,
        'docs': docs_require,
    },
)
