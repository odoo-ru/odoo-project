
def test_name(module_a):
    assert module_a.name == 'module_a'
    assert module_a['name'] == 'Module A'
    assert module_a.manifest['name'] == 'Module A'


# def test_
