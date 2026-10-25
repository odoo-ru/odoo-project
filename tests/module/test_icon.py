
def test_absent_icon(module):
    assert module.manifest.icon is None
    assert module.icon_path == '/base/static/description/icon.png'


def test_non_empty_icon(module):
    module.manifest.icon = 'custom-path'
    assert module.icon_path == 'custom-path'


def test_existing_icon_file(module_a):
    assert module_a.manifest.icon is None
    assert module_a.icon_path == f'/{module_a.name}/static/description/icon.png'
