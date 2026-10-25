from odoo_project.module import OdooModule


def test_cache(modules_dir):
    module_1 = OdooModule(modules_dir / 'module_empty')
    module_2 = OdooModule(modules_dir / 'module_empty')
    assert module_1 == module_2
    assert module_1 is module_2


def test_no_cache(modules_dir):
    module_1 = OdooModule(modules_dir / 'module_empty')
    module_2 = OdooModule(modules_dir / 'module_empty', cache_module=False)
    assert module_1 == module_2
    assert module_1 is not module_2
