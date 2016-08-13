#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import sphinx_rtd_theme

# Get the project root dir, which is the parent dir of this
cwd = os.getcwd()
project_root = os.path.dirname(cwd)

# Insert the project root dir as the first element in the PYTHONPATH.
# This lets us ensure that the source package is imported, and that its
# version is used.
sys.path.insert(0, project_root)

import bigchaindb_driver


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'bigchaindb-driver'
copyright = u"2016, BigchainDB"
version = bigchaindb_driver.__version__
release = bigchaindb_driver.__version__
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = True
suppress_warnings = ['image.nonlocal_uri']

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
htmlhelp_basename = 'bigchaindb_driverdoc'

latex_elements = {}

latex_documents = [
    ('index', 'bigchaindb_driver.tex',
     u'bigchaindb-driver Documentation',
     u'BigchainDB', 'manual'),
]

man_pages = [
    ('index', 'bigchaindb_driver',
     u'bigchaindb-driver Documentation',
     [u'BigchainDB'], 1)
]

texinfo_documents = [
    ('index', 'bigchaindb_driver',
     u'bigchaindb-driver Documentation',
     u'BigchainDB',
     'bigchaindb_driver',
     'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/3': None}
