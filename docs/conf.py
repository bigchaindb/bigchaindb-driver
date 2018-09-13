# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import sys
import os
import datetime

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
    'sphinxcontrib.httpdomain',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
]

autodoc_default_options = {
    'show-inheritance': None,
}
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'BigchainDB Python Driver'
now = datetime.datetime.now()
copyright = str(now.year) + ', BigchainDB Contributors'
version = bigchaindb_driver.__version__
release = bigchaindb_driver.__version__
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = True
suppress_warnings = ['image.nonlocal_uri']

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
htmlhelp_basename = 'bigchaindb_python_driverdoc'

latex_elements = {}

latex_documents = [
    ('index', 'bigchaindb_python_driver.tex',
     'BigchainDB Python Driver Documentation',
     'BigchainDB', 'manual'),
]

man_pages = [
    ('index', 'bigchaindb_python_driver',
     'BigchainDB Python Driver Documentation',
     ['BigchainDB'], 1)
]

texinfo_documents = [
    ('index', 'bigchaindb_python_driver',
     'BigchainDB Python Driver Documentation',
     'BigchainDB',
     'bigchaindb_python_driver',
     '',
     'Miscellaneous'),
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'bigchaindb-server': (
        'https://docs.bigchaindb.com/projects/server/en/latest/', None),
}
