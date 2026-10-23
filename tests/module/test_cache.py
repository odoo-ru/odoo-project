from odoo_project.module import OdooModule


def test_module(modules_dir):
    module_a1 = OdooModule(modules_dir / 'module_a')
    module_a2 = OdooModule(modules_dir / 'module_a')
    assert module_a1 == module_a2
    assert module_a1 is module_a2
