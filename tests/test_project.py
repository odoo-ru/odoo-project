
import pytest

from odoo_project.project import OdooModuleSet, OdooProject


def test_topologic_dependencies(project_path):
    project = OdooProject(project_path)
    # assert project.config.module_dirs == ['addons']

    module = project.module('module_a')
    assert module.name == 'module_a'

    module_list = project.topologic_dependencies(project.expand_dependencies(OdooModuleSet({module})))
    assert [module.name for module in module_list] == [
        'module_c',
        'module_b',
        'module_a',
    ]


@pytest.mark.skip
def test_module_graph(project_path):
    project = OdooProject(project_path, modules=['module_a'])
    # project = OdooProject(project_path)
    # assert project.config.module_dirs == ['addons']

    required_modules = project.required_modules
    # assert required_modules.names() == {'module_name', 'module_a', 'module_b'}
    # assert required_modules.names() == {'module_name'}
    # assert required_modules.names() == {'base', 'mail'}
    assert required_modules.names == {'module_a'}

    assert project.installed_modules.names > {
        'module_a',
        'module_b',
        'module_c',
    }
