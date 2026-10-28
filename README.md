Odoo Project
============
[![PyPI Version](https://img.shields.io/pypi/v/odoo-project)](https://pypi.org/project/odoo-project/ "Latest version on PyPI")
![PyPI Status](https://img.shields.io/pypi/status/odoo-project)
![Python Versions](https://img.shields.io/pypi/pyversions/odoo-project)
[![PyPI Versions from Framework Classifiers](https://img.shields.io/pypi/frameworkversions/odoo/odoo-project?color=A24689)](https://www.odoo.com/documentation/20.0/developer/reference.html "Odoo 20.0 developer docs")
[![Github Pages](https://img.shields.io/badge/github-pages-blue?logo=github)](https://odoo-ru.github.io/odoo-project/ "Documentation")
[![Coverage](https://coveralls.io/repos/github/odoo-ru/odoo-project/badge.svg?branch=main)](https://coveralls.io/github/odoo-ru/odoo-project?branch=main "Coverage")

Model Objects for Odoo modules and projects.

Install
-------
```console
uv add odoo-project
```

Usage
-----
```python
from odoo_project import OdooModule

module = OdooModule('./hr_payroll')
```
See [documentation](https://odoo-ru.github.io/odoo-project/).

Development
-----------
```console
git clone git@github.com:odoo-ru/odoo-project.git

cd odoo-project
```

Run tests:
```console
uv run pytest
```
