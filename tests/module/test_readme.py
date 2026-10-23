
def test_manifest_defaults(module):
    assert module.readme is None

def test_existing_readme(module_a):
    assert module_a.readme == module_a / 'README.rst'
