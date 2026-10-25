def test_auto_install_is_false(module):
    assert module.manifest.auto_install is False
    assert module.is_auto_install is False
    assert module.auto_install_depends == frozenset()


def test_auto_install_is_true(module):
    module.manifest.auto_install = True
    module.manifest.depends = ['a']
    assert module.is_auto_install is True
    assert module.auto_install_depends == {'a'}


def test_auto_install_is_empty(module):
    module.manifest.auto_install = []
    assert module.is_auto_install is True
    assert module.auto_install_depends == frozenset()


def test_auto_install_is_not_empty(module):
    module.manifest.auto_install = ['b']
    assert module.is_auto_install is True
    assert module.auto_install_depends == {'b'}
