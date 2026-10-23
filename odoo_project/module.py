import ast
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path

from attrs import define


class CacheModuleMeta(type):
    def __init__(cls, what, bases, dict):
        super().__init__(what, bases, dict)
        cls._modules_cache = {}

    def __call__(cls, path, *args, cache_module=True, **kwargs):
        path = Path(path).resolve()

        if cache_module and path in cls._modules_cache:
            return cls._modules_cache[path]

        instance = super().__call__(path, *args, **kwargs)
        if cache_module:
            cls._modules_cache[path] = instance
        return instance


README_FILE_NAMES = ['README.rst', 'README.md', 'README.txt', 'README']
STATIC_DESCRIPTION_ICON = 'static/description/icon.png'


# Use attrs.define to enable cached_property with slots.
# https://discuss.python.org/t/extensible-cached-property/105188
# https://github.com/python-attrs/attrs/pull/1200
@define(slots=True)
class OdooModule(metaclass=CacheModuleMeta):
    path: Path
    name: str

    # Odoo 20.0: _DEFAULT_MANIFEST at odoo/modules/module.py:60:1
    default_info = {
        'name': None,
        'version': '1.0',
        'summary': None,
        'description': None,
        'license': 'LGPL-3',
        'category': 'Uncategorized',
        'sequence': 100,
        'icon': None,

        'author': None,
        'contributors': None,
        'maintainer': None,
        'website': None,

        'installable': True,
        'application': False,
        'auto_install': False,
        'depends': (),
        'external_dependencies': None,

        'web': False,
        'to_buy': None,

        'data': (),
        'demo': (),
        'assets': None,

        'pre_init_hook': None,
        'post_init_hook': None,
        'uninstall_hook': None,
        'post_load': None,
    }

    def __init__(self, path: str | Path):
        path = Path(path)
        if not is_module(path):
            raise ValueError(path)

        self.path = path
        self.name = path.name

    def __repr__(self):
        return f'OdooModule({self.name!r})'

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return self.path.__hash__()

    def __truediv__(self, path):
        return self.path / path

    @cached_property
    def manifest(self):
        with (self.path / '__manifest__.py').open() as manifest_file:
            return ast.literal_eval(manifest_file.read())

    @cached_property
    def readme(self) -> Path | None:
        for readme_file_name in README_FILE_NAMES:
            readme_file_path = self / readme_file_name
            if readme_file_path.is_file():
                return readme_file_path
        return None

    @cached_property
    def icon(self) -> str:
        if 'icon' in self.manifest:
            return self.manifest['icon']

        if (self / STATIC_DESCRIPTION_ICON).is_file():
            return f'/{self.name}/{STATIC_DESCRIPTION_ICON}'

        return '/base/' + STATIC_DESCRIPTION_ICON

    @cached_property
    def depends(self) -> frozenset[str]:
        depends = self.manifest.get('depends', ())
        if not depends and self.name != 'base':
            return frozenset(('base',))
        return frozenset(depends)

    @cached_property
    def is_auto_install(self) -> bool:
        """
        Manifest `auto_install` can be True, False or list of depends.
        Convert it to bool.
        Special case: Install always if auto_install is []
        """
        auto_install = self['auto_install']
        return isinstance(auto_install, Iterable) or bool(auto_install)

    @cached_property
    def auto_install_depends(self):
        auto_install = self.manifest.get('auto_install')
        if auto_install is True:
            return frozenset(self.depends)
        if isinstance(auto_install, Iterable):
            return frozenset(auto_install)
        return frozenset()

    def installable(self, serie):
        adopted_version = adapt_version(self['version'], serie)
        return self['installable'] and adopted_version.startswith(serie + '.')

    def __getitem__(self, item):
        if item in self.manifest:
            return self.manifest[item]

        if item in self.default_info:
            return self.default_info[item]

        raise AttributeError


SERIE_LENGTH = 2
FULL_VERSION_MIN_LENGTH = 4


def adapt_version(version, serie):
    """
    Adapt module version by prefix Odoo major version.
    Odoo 20: adapt_version at odoo/modules/module.py:589:1
    """
    version_parts = version.split('.')
    if len(version_parts) < FULL_VERSION_MIN_LENGTH and '.'.join(version_parts[:SERIE_LENGTH]) != serie:
        return f'{serie}.{version}'
    return version


def is_module(path: Path):
    return (path / '__manifest__.py').is_file()
