from pathlib import Path

from odoo_project.module import OdooModule


def test_module(project_path):
    module_a = OdooModule(project_path / 'addons/module_a')
    module_a2 = OdooModule(project_path / 'addons/module_a')
    assert module_a == module_a2
    assert module_a is module_a2


def test_relative_path(module_a):
    assert module_a / 'models/model.py' == Path(module_a.path, 'models/model.py')
