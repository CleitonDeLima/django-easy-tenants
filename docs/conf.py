# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import django
from django.conf import settings

here = Path(__file__).parent.resolve()
sys.path.insert(0, str(here / ".." / "src"))

# autodoc imports the package, so Django must be configured first.
settings.configure(
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "easy_tenants",
    ],
)
django.setup()

# -- Project information -----------------------------------------------------

with (here / ".." / "pyproject.toml").open("rb") as fp:
    pyproject_toml_data = tomllib.load(fp)

project = pyproject_toml_data["project"]["name"]
author = "Cleiton Lima"
copyright = "Cleiton Lima"
version = pyproject_toml_data["project"]["version"]
release = version

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

exclude_patterns = [
    ".venv",
    "_build",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

autodoc_member_order = "bysource"

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = f"{project} {version}"
html_theme_options = {
    "source_repository": (
        "https://github.com/CleitonDeLima/django-easy-tenants/"
    ),
    "source_branch": "main",
    "source_directory": "docs/",
}

# -- Options for Intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}
