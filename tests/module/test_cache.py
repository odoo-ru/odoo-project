from odoo_project.module import OdooModule


def test_cache(modules_dir):
    module_a1 = OdooModule(modules_dir / 'module_a')
    module_a2 = OdooModule(modules_dir / 'module_a')
    assert module_a1 == module_a2
    assert module_a1 is module_a2


def test_no_cache(modules_dir):
    module_a1 = OdooModule(modules_dir / 'module_a')
    module_a2 = OdooModule(modules_dir / 'module_a', cache_module=False)
    assert module_a1 == module_a2
    assert module_a1 is not module_a2
