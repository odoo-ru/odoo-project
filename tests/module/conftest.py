from pathlib import Path

import pytest

from odoo_project.module import OdooModule


@pytest.fixture(scope='package')
def modules_dir():
    return Path(__file__).parent


@pytest.fixture
def module_a(modules_dir):
    return OdooModule(modules_dir / 'module_a', cache_module=False)


@pytest.fixture
def module(modules_dir):
    return OdooModule(modules_dir / 'module_empty', cache_module=False)
