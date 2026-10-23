
def test_absent_depends(module):
    assert module.depends == {'base'}


def test_base_depends(module):
    module.name = 'base'
    assert module.depends == set()


def test_existing_depends(module_a):
    assert module_a.depends == {'module_b'}
