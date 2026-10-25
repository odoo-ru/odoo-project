
import pytest

from odoo_project.project import OdooModuleSet, OdooProject


@pytest.mark.skip
def test_topologic_dependencies(project_path):
    project = OdooProject(project_path)

    module = project.module('module_a')
    assert module.name == 'module_a'

    module_list = project.topologic_dependencies(project.expand_dependencies(OdooModuleSet({module})))
    assert [module.name for module in module_list] == [
        'module_c',
        'module_b',
        'module_a',
    ]
