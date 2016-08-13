#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

install_requires = []

tests_require = [
    'coverage',
    'pep8',
    'pyflakes',
    'pylint',
    'pytest-cov',
    'pytest-xdist',
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
]


setup(
    name='bigchaindb_driver',
    version='0.0.1a1',
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
