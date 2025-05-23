#!/usr/bin/env python
#
# icenet documentation build configuration file, created by
# sphinx-quickstart on Fri Jun  9 13:47:02 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
import datetime
import subprocess

import icenet

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_nb',
    # 'myst_parser',
    # 'sphinxcontrib.kroki',
    'sphinx_design',
    'sphinx_multiversion',
    ]

# Standardising on
napoleon_numpy_docstring = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = icenet.__name__
copyright = "{}, {}".format(
    datetime.datetime.utcnow().year, icenet.__copyright__)
author = icenet.__author__

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = ".".join(icenet.__version__.split(".")[0:2])
# The full version, including alpha/beta/rc tags.
release = icenet.__version__

# Change default title
html_title = 'IceNet documentation'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "repository_url": "https://github.com/icenet-ai/icenet",
    "use_issues_button": True,
    "use_download_button": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'icenetdoc'


# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'icenet.tex',
     'IceNet Documentation',
     'James Byrne', 'manual'),
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'icenet',
     'IceNet Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'icenet',
     'IceNet Documentation',
     author,
     'icenet',
     'One line description of project.',
     'Miscellaneous'),
]

# -- Sphinx Multiversion -----------------------------------------------

# Whitelist pattern for tags (set to None to ignore all tags)
# smv_tag_whitelist = r'^.*$'
# smv_tag_whitelist = r'^v(?!.*dev).*'
smv_tag_whitelist = r'^v(?!.*dev)(?!.*a\d$).*'
# smv_tag_whitelist = None

# Whitelist pattern for branches (set to None to ignore all branches)
# smv_branch_whitelist = r'^.*$'
smv_branch_whitelist = r'^v0\.\d+\.\d+(_dev)?+\d*$|main|master'

# Whitelist pattern for remotes (set to None to use local branches only)
smv_remote_whitelist = None

# Pattern for released versions
smv_released_pattern = r'^refs/tags/v(?!.*dev)(?!.*a\d$).*|main|master$'

def get_latest_git_tag():
    """Get the latest git tag of the icenet repository"""
    try:
        # Get the latest tag - this should be the latest released version of IceNet.
        latest_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], text=True).strip()
        return latest_tag
    except subprocess.CalledProcessError:
        return None  # Return None if there is an error, such as no tags

# Set smv_latest_version dynamically to the latest tag
smv_latest_version = get_latest_git_tag() or 'main'

# -- myst_nb -----------------------------------------------------------

nb_execution_mode = 'off'
myst_enable_extensions = ["colon_fence", "html_image", "linkify", "dollarmath", "tasklist"]
