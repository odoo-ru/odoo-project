import dataclasses
from collections.abc import Container, Iterable
from functools import cached_property, lru_cache
from pathlib import Path

from odoo_project.config import Config, read_config
from odoo_project.module import OdooModule, is_module
from odoo_project.module_set import OdooModuleSet


class OdooProject:
    def __init__(self, path, **options):
        self.path = Path(path).resolve()

        config_dict = dataclasses.asdict(self.project_file_config)
        config_dict.update(options)
        self.project_config = Config(**config_dict)

    @property
    def project_file_config(self):
        return read_config(self.path / 'odoo-project.toml')

    @property
    def project_module_paths(self):
        return [(self.path / path) for path in self.project_config.project_module_dirs]

    @property
    def third_party_module_paths(self):
        return [(self.path / path) for path in self.project_config.third_party_module_dirs]

    @cached_property
    def modules_paths(self):
        # In fact core_modules_path is os.path.join(odoo.tools.config['root_path'], 'addons').
        # We don't want to import odoo. It's long one second almost.

        # ruff:ignore[import-outside-top-level]
        import importlib
        odoo_module_spec = importlib.util.find_spec('odoo')
        odoo_module_path = odoo_module_spec.submodule_search_locations[0]
        core_modules_path = Path(odoo_module_path, 'addons').resolve()

        return (
            self.project_module_paths
            + self.third_party_module_paths
            + [core_modules_path]
        )

    def collect_modules(self, paths: Iterable[Path], exclude: Container[str] = ()):
        modules = OdooModuleSet()
        for module_path in paths:
            for subdir in module_path.iterdir():
                if subdir.name not in exclude and is_module(subdir):
                    modules.add(OdooModule(subdir))
        return modules

    # ruff:ignore[cached-instance-method]
    @lru_cache(maxsize=1024)
    def module(self, module_name):
        for modules_path in self.modules_paths:
            module_path = modules_path / module_name
            if is_module(module_path):
                # TODO Cache?
                return OdooModule(module_path)
        msg = f'No module found: {module_name}'
        raise LookupError(msg)

    def find_modules(self, module_names):
        return OdooModuleSet(self.module(module_name) for module_name in module_names)

    @property
    def required_modules(self) -> OdooModuleSet:
        return (
            self.collect_modules(self.project_module_paths, exclude=self.project_config.exclude_modules)
            | self.find_modules(self.project_config.include_modules)
        )

    def expand_dependencies(self, modules):
        modules_to_check_depends = modules

        while True:
            module_depends_names = modules_to_check_depends.depends()
            if module_depends_names:
                modules_to_check_depends = self.find_modules(module_depends_names)
                modules |= modules_to_check_depends
            else:
                break

        return modules

    def auto_install_modules(self, modules: OdooModuleSet):
        auto_install_modules = OdooModuleSet()
        for module in self.collect_modules(self.modules_paths, exclude=modules.names):
            if module.is_auto_install and set(module.depends) <= modules.names:
                auto_install_modules.add(module)
        return auto_install_modules

    @property
    def installed_modules(self):
        modules = self.expand_dependencies(self.required_modules)

        while True:
            auto_install_modules = self.auto_install_modules(modules)
            if auto_install_modules:
                modules |= auto_install_modules
            else:
                break

        return modules

    def topologic_dependencies(self, modules: OdooModuleSet):
        result = []
        visited = set()

        def visit(modd):
            if modd not in visited:
                visited.add(modd)
                if modd in modules:
                    for depend_module in self.find_modules(modd.depends).sorted():
                        visit(depend_module)
                    result.append(modd)

        for module in modules.sorted():
            visit(module)

        return result

    # @lru_cache
    def installed_modules_list(self, *, inversed=False):
        modules = self.topologic_dependencies(self.installed_modules)
        if inversed:
            modules = modules.reverse()
        return modules

    # =======================================================================
    def module_graph(self, module_name):
        processed_modules = set()

        def recursive_module_graph(module):
            edges = []
            processed_modules.add(module)
            for dependency_module_name in module.depends:
                dependency_module = self.module(dependency_module_name)
                edges.append((module, dependency_module))
                if dependency_module not in processed_modules:
                    edges.extend(self.module_graph(dependency_module))
            return edges

        return recursive_module_graph(self.module(module_name))

    # ============= create db ====================
    def cache_key(self, module_names, timestamp):
        raise NotImplementedError

    # Env
    @cached_property
    def env(self):
        # Keep ref on generator force close generator later
        return self._get_env('soma', self.installed_modules)

    def _get_env(self, db_name, installed_modules: OdooModule | OdooModuleSet):
        # ruff:ignore[unsorted-imports]
        # ruff:ignore[import-outside-top-level]
        from unittest import mock
        # ruff:ignore[import-outside-top-level]
        import odoo
        # ruff:ignore[import-outside-top-level]
        from odoo_project.database_mock import CursorMock, FakeDatabase

        CursorMock.databases[db_name] = FakeDatabase(installed_modules)

        with (
            mock.patch('odoo.sql_db.Cursor', CursorMock),
            odoo.registry(db_name).cursor() as cr,
        ):
            return odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    # ========== Translation ==========
    def search_translation(self, tupl, lang=None):
        for module in self.installed_modules_list():
            translations = module.translations(lang or self.lang)
            if tupl in translations:
                return translations[tupl]
        return None

    def code_translation(self, file_path, value, lineno=None):
        return self.search_translation(('code', file_path, lineno, value))

    def selection(self, model_name, field_name, value, lang=None):
        field = self.env[model_name]._fields[field_name]
        for selection_value, _selection_string in field.selection:
            if value == selection_value:
                break
        else:
            msg = 'Invalid selection value'
            raise ValueError(msg)
        return self.search_translation(('selection', f'{model_name},{field_name}', '0', _selection_string), lang=lang)

    def constraint(self, model, value):
        return self.search_translation(('constraint', model, '0', value))

    def sql_constraint(self, model, value):
        return self.search_translation(('sql_constraint', model, '0', value))

    def model_translation(self, model_name, field_name, xml_id, origin, lang=None):
        return self.search_translation(('model', f'{model_name},{field_name}', xml_id, origin), lang=lang)

    def model_description(self, model_name, lang=None):
        model = self.env[model_name]
        if not lang:
            # ruff:ignore[private-member-access]
            return model._description
        # ruff:ignore[private-member-access]
        xml_id = f'{model._original_module}.model_{model_name.replace(".", "_")}'
        xml_id = None
        # ruff:ignore[private-member-access]
        return self.model_translation('ir.model', 'name', xml_id, model._description, lang=lang)

    def field_description(self, model_name, field_name, lang=None):
        field = self.env[model_name]._fields[field_name]
        if not lang:
            return field.string
        # ruff:ignore[private-member-access]
        xml_id = f'{field._module}.field_{model_name.replace(".", "_")}_{field_name}'
        return self.model_translation('ir.model.fields', 'field_description', xml_id, field.string, lang=lang)
