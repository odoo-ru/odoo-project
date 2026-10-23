def test_auto(module):
    assert module['auto_install'] is False
    assert module.is_auto_install is False
    assert module.auto_install_depends == set()

# def test_soma(module):
#     assert module.auto_install_depends
