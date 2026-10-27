import ast
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path

from attr import Factory
from attrs import define


class AutoInstallTypeError(TypeError):
    def __init__(self, value):
        super().__init__(f'Invalid type of manifest auto_install: {type(value)}')


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
class OdooModuleManifest:
    """
    A wrapper around the values of an Odoo module manifest file.

    Designed for convenient access to manifest values
    without computing certain fields as Odoo does.
    It exposes all known manifest fields as class attributes.
    Missing values are automatically populated with defaults, empty lists, empty dicts, or `None`.
    """
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
    assets: dict[str, list[str]] = Factory(dict)

    pre_init_hook: str | None = None
    post_init_hook: str | None = None
    uninstall_hook: str | None = None
    post_load: str | None = None

    # Odoo 20 modules fields
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
    def from_path(cls, path: Path):
        """Read values from directory `__manifest__.py` file."""
        with (path / '__manifest__.py').open() as manifest_file:
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
    """
    Represents an Odoo module directory.

    Designed to work with module files, including the manifest, data, and translations.
    The implementation is independent of the Odoo version, does not import `odoo`,
    and does not rely on Odoo code.
    """
    path: Path
    """Module dir path"""
    name: str
    """Module dir name <small>aka</small> Technical name"""

    def __init__(self, path: Path):
        if not is_module(path):
            raise ValueError(path)

        self.path = path
        self.name = path.name

    def __fspath__(self):
        return str(self.path)

    def __truediv__(self, path: Path | str) -> Path:
        """Returns the path relative to the module directory."""
        return self.path / path

    def __repr__(self):
        return f'OdooModule({str(self.path)!r})'

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)

    @cached_property
    def manifest(self) -> OdooModuleManifest:
        """Returns parsed manifest object"""
        return OdooModuleManifest.from_path(self.path)

    @cached_property
    def readme_path(self) -> Path | None:
        """
        Returns first of existing files or `None`:

        1. README.rst
        2. README.md
        3. README.txt
        4. README
        """
        for readme_file_name in README_FILE_NAMES:
            readme_file_path = self / readme_file_name
            if readme_file_path.is_file():
                return readme_file_path
        return None

    @cached_property
    def icon_path(self) -> str:
        """
        Returns first available option:

        1. Manifest icon value if it is specified.
        2. `/<module>/static/description/icon.png` if file exists.
        3. Fallback to `/base/static/description/icon.png`.
        """
        if self.manifest.icon:
            return self.manifest.icon

        if (self / STATIC_DESCRIPTION_ICON).is_file():
            return f'/{self.name}/{STATIC_DESCRIPTION_ICON}'

        return f'/base/{STATIC_DESCRIPTION_ICON}'

    @cached_property
    def dependencies(self) -> frozenset[str]:
        """
        Returns manifest `depends` wrapped into `frozenset`.
        Adds `base` if it's empty.
        """
        if not self.manifest.depends and self.name != 'base':
            return frozenset({'base'})
        return frozenset(self.manifest.depends)

    @cached_property
    def is_auto_install(self) -> bool:
        """
        Returns True if manifest `auto_install` is True or Iterable.
        """
        if isinstance(self.manifest.auto_install, bool):
            return self.manifest.auto_install
        if isinstance(self.manifest.auto_install, Iterable):
            return True
        raise AutoInstallTypeError(self.manifest.auto_install)

    @cached_property
    def auto_install_depends(self) -> frozenset[str]:
        """
        Return frozenset depends on manifest `auto_install` value.
        If it's True returns `self.dependencies`.
        If it's False returns empty set.
        If it's list returns frozenset of its values.
        """
        if self.manifest.auto_install is False:
            return frozenset()
        if self.manifest.auto_install is True:
            return self.dependencies
        if isinstance(self.manifest.auto_install, Iterable):
            return frozenset(self.manifest.auto_install)
        raise AutoInstallTypeError(self.manifest.auto_install)

    def is_installable(self, serie):
        adopted_version = adapt_version(self.manifest.version, serie)
        return self.manifest.installable and adopted_version.startswith(serie + '.')


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
