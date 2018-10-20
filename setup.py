#!/usr/bin/env python
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

install_requires = [
    'requests>=2.11.0',
    'cryptoconditions==0.8.0',
    'pysha3~=1.0.2',
    'python-rapidjson==0.6.0',
    'python-rapidjson-schema==0.1.1',
]

tests_require = [
    'tox>=2.3.1',
    'coverage>=4.1',
    'flake8>=2.6.0',
    'pytest>=3.0.1',
    'pytest-cov',
    'pytest-env',
    'pytest-sugar',
    'pytest-xdist',
    'responses~=0.5.1',
]

dev_require = [
    'ipdb',
    'ipython',
    'pre-commit'
]

docs_require = [
    'Sphinx~=1.0',
    'sphinx-autobuild',
    'sphinxcontrib-autorun',
    'sphinxcontrib-napoleon>=0.4.4',
    'sphinx_rtd_theme',
    'sphinxcontrib-httpdomain',
    'matplotlib',
]

setup(
    name='bigchaindb_driver',
    version='0.6.0',
    description="Python driver for BigchainDB",
    long_description=readme + '\n\n' + changelog,
    author="BigchainDB",
    author_email='dev@bigchaindb.com',
    url='https://github.com/bigchaindb/bigchaindb-driver',
    packages=find_packages(exclude=['tests*']),
    package_dir={'bigchaindb_driver':
                 'bigchaindb_driver'},
    include_package_data=True,
    install_requires=install_requires,
    python_requires='>=3.5',
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='bigchaindb_driver',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    extras_require={
        'test': tests_require,
        'dev': dev_require + tests_require + docs_require,
        'docs': docs_require,
    },
)
