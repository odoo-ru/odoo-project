def test_base_depends(module):
    module.name = 'base'
    assert module.dependencies == set()


def test_empty_depends(module):
    assert module.dependencies == {'base'}


def test_non_empty_depends(module):
    module.manifest.depends = ['b']
    assert module.dependencies == {'b'}
