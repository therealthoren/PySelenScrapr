# Configuration file for the Sphinx documentation builder.

# -- Project information
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))

project = 'PySelenScrapr'
copyright = '2024, Thoren Lederer'
author = 'donnercody'

release = '0.0.7'
version = '0.0.7'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

# autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': True,
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}
