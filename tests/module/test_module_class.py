from odoo_project import OdooModule


def test_string_path(module):
    assert OdooModule(str(module.path))


def test_repr(module):
    assert repr(module) == f'OdooModule({str(module.path)!r})'


def test_relative_path(module):
    assert module / 'models/model.py' == module.path / 'models/model.py'
