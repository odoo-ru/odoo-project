from odoo_project import OdooModule


def test_string_path(module):
    assert OdooModule(str(module.path))


def test_repr(module):
    assert repr(module) == f'OdooModule({str(module.path)!r})'


def test_relative_path(module_a):
    assert module_a / 'models/model.py' == module_a.path / 'models/model.py'
