import ast
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path

from attr import Factory
from attrs import define


class CacheModuleMeta(type):
    def __init__(cls, what, bases, dict):
        super().__init__(what, bases, dict)
        cls._modules_cache = {}

    def __call__(cls, path, *args, cache_module=True, **kwargs):
        if isinstance(path, str):
            path = Path(path)

        path = path.resolve()

        if cache_module and path in cls._modules_cache:
            return cls._modules_cache[path]

        instance = super().__call__(path, *args, **kwargs)
        if cache_module:
            cls._modules_cache[path] = instance
        return instance


README_FILE_NAMES = ['README.rst', 'README.md', 'README.txt', 'README']
STATIC_DESCRIPTION_ICON = 'static/description/icon.png'


@define(slots=True)
class Manifest:
    name: str
    version: str = '1.0'
    summary: str | None = None
    description: str | None = None
    website: str | None = None
    license: str = 'LGPL-3'
    category: str = 'Uncategorized'
    sequence: int = 100
    icon: str | None = None

    author: str | None = None
    contributors: str | None = None
    maintainer: str | None = None

    installable: bool = True
    application: bool = False
    depends: list[str] = Factory(list)
    auto_install: bool | list[str] = False
    external_dependencies: dict | None = Factory(dict)

    data: list[str] = Factory(list)
    demo: list[str] = Factory(list)
    assets: dict[str: list[str]] = Factory(dict)

    pre_init_hook: str | None = None
    post_init_hook: str | None = None
    uninstall_hook: str | None = None
    post_load: str | None = None

    # Additional from core
    iap_paid_service: bool = False
    # l10n_* modules
    countries: list[str] = Factory(list)
    # theme_* + hr
    images: list[str] = Factory(list)
    # theme_* + website
    configurator_snippets: dict[str, list[str]] = Factory(dict)
    # theme_*
    configurator_snippets_addons: dict[str, dict] = Factory(dict)
    theme_customizations: dict[str, dict] = Factory(dict)
    # l10n_cr modules. Incorrect field
    url: str | None = None
    # some hr, some pos and other modules
    other_files: list[str] = Factory(list)
    # account
    kpi_providers: list[str] = Factory(list)
    # web, api_doc, auth_signup
    bootstrap: bool = False
    # website
    new_page_templates: dict[str, dict] = Factory(dict)

    @classmethod
    def from_file(cls, path: Path):
        with path.open() as manifest_file:
            # TODO keep file content
            manifest_dict = ast.literal_eval(manifest_file.read())
            return cls(**manifest_dict)


# Use attrs.define to enable cached_property with slots.
# https://discuss.python.org/t/extensible-cached-property/105188
# https://github.com/python-attrs/attrs/pull/1200
@define(
    slots=True,
    init=False,
    repr=False,
    eq=False,
)
class OdooModule(metaclass=CacheModuleMeta):
    path: Path
    name: str

    def __init__(self, path: Path):
        if not is_module(path):
            raise ValueError(path)

        self.path = path
        self.name = path.name

    def __repr__(self):
        return f'OdooModule({str(self.path)!r})'

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return self.path.__hash__()

    def __truediv__(self, path: Path | str) -> Path:
        return self.path / path

    @cached_property
    def manifest(self):
        return Manifest.from_file(self / '__manifest__.py')

    @cached_property
    def readme_path(self) -> Path | None:
        for readme_file_name in README_FILE_NAMES:
            readme_file_path = self / readme_file_name
            if readme_file_path.is_file():
                return readme_file_path
        return None

    @cached_property
    def icon_path(self) -> str:
        if self.manifest.icon:
            return self.manifest.icon

        if (self / STATIC_DESCRIPTION_ICON).is_file():
            return f'/{self.name}/{STATIC_DESCRIPTION_ICON}'

        return '/base/' + STATIC_DESCRIPTION_ICON

    @cached_property
    def depends(self) -> frozenset[str]:
        if not self.manifest.depends and self.name != 'base':
            return frozenset({'base'})
        return frozenset(self.manifest.depends)

    @cached_property
    def is_auto_install(self) -> bool:
        """
        Manifest `auto_install` can be True, False or list of depends.
        Convert it to bool.
        Special case: Install always if auto_install is []
        """
        return bool(self.manifest.auto_install) or isinstance(self.manifest.auto_install, Iterable)

    @cached_property
    def auto_install_depends(self):
        if self.manifest.auto_install is True:
            return self.depends
        if isinstance(self.manifest.auto_install, Iterable):
            return frozenset(self.manifest.auto_install)
        return frozenset()

    def installable(self, serie):
        adopted_version = adapt_version(self['version'], serie)
        return self['installable'] and adopted_version.startswith(serie + '.')


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
