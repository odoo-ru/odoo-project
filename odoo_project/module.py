import ast
from collections import ChainMap
from collections.abc import Iterable
from functools import cached_property, lru_cache
from pathlib import Path


class PathCacheMeta(type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._cache = {}

    def __call__(cls, path, *args, **kwargs):
        path = Path(path).resolve()

        if path in cls._cache:
            return cls._cache[path]

        instance = super().__call__(path, *args, **kwargs)
        cls._cache[path] = instance
        return instance


class slot_cached_property:
    """
    Декоратор functools.cached_property не работает на классах без __dict__.
    Его нельзя использовать для класса со слотами без __dict__,
    Класс slot_cached_property кэширует свойство в __slots__.
    При этом места расходуется в 3 раза меньше, но доступ к кэшу
    работает в 1.5 раза медленнее cached_property.

    В этом обсуждении есть ещё и такой вариант:
    https://discuss.python.org/t/extensible-cached-property/105188/17

    Для работы требует наличия в классах слота с именем '_<имя_функции>'.
    """
    def __init__(self, func):
        self.func = func
        self.slot_name = None

    def __set_name__(self, owner, name):
        # Автоматически генерируем имя ожидаемого слота при загрузке класса
        self.slot_name = f'_{name}'

    def __get__(self, instance, owner):
        # Если обращаются к свойству через класс (например, MyClass.heavy_data)
        if instance is None:
            return self

        # Проверяем, инициализирован ли слот.
        # Если он пустой, Python выбросит исключение AttributeError.
        try:
            value = getattr(instance, self.slot_name)
        except AttributeError:
            # Вычисляем оригинальную функцию и сохраняем результат в слот
            value = self.func(instance)
            setattr(instance, self.slot_name, value)

        return value


README_FILE_NAMES = ['README.rst', 'README.md', 'README.txt', 'README']
STATIC_DESCRIPTION_ICON = 'static/description/icon.png'

class OdooModuleBase:
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
        # return self is other

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
        elif isinstance(auto_install, Iterable):
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

        return None
        raise AttributeError(f'Unknown attribute: {item!r}')


class OdooModule(OdooModuleBase, metaclass=PathCacheMeta):
    pass


class OdooModule_OFF:
    def data_file_path(self):
        yield from self.manifest.get('data', [])


    def _file_translations(self, po_file_name):
        from odoo.tools.translate import PoFileReader

        result = {}
        for subdir in ['i18n_extra', 'i18n']:
            po_file_path = self / subdir / po_file_name
            if not po_file_path.exists():
                continue
            with po_file_path.open('rb') as f:
                for translation in PoFileReader(f):
                    trns = (
                        translation['type'],
                        translation['name'],
                        translation['res_id'],
                        translation['src'],
                    )
                    result[trns] = translation['value']

        return result

    @lru_cache
    def translations(self, locale_identifier):
        from babel.core import Locale

        locale = Locale.parse(locale_identifier)

        base_trans = self._file_translations(f'{locale.language}.po')
        if not locale.territory or locale.territory.lower() == locale.language:
            return base_trans

        # if locale.territory and locale.territory.lower() != locale.language:
        spec_trans = self._file_translations(f'{locale_identifier}.po')
        return ChainMap(spec_trans, base_trans)


def adapt_version(version, serie):
    """
    Adapt module version by prefix Odoo major version.
    Odoo 20: adapt_version at odoo/modules/module.py:589:1
    """
    version_parts = version.split('.')
    # if len(version_parts) <= 3 and not version.startswith(serie + '.'):
    if len(version_parts) <= 3 and not version.startswith(serie):
        return f'{serie}.{version}'
    return version


def is_module(path: Path):
    return (path / '__manifest__.py').is_file()
