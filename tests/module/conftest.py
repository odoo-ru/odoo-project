from pathlib import Path
import pytest

from odoo_project.module import OdooModuleBase



@pytest.fixture(scope='package')
def modules_dir():
    return Path(__file__).parent


@pytest.fixture
def module_a(modules_dir):
    return OdooModuleBase(modules_dir / 'module_a')


@pytest.fixture
def module(modules_dir):
    return OdooModuleBase(modules_dir / 'module_dumb')
