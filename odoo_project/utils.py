from pathlib import Path


def import_odoo():
    # ruff:ignore[import-outside-top-level]
    import odoo

    return odoo


def odoo_core_modules_path():
    odoo = import_odoo()
    return Path(odoo.__path__[0]) / 'addons'
