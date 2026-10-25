
def test_manifest_defaults(module):
    assert module.readme_path is None


def test_existing_readme(module_a):
    assert module_a.readme_path == module_a / 'README.rst'
