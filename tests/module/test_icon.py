
def test_absent_icon(module):
    assert 'icon' not in module.manifest
    assert module.icon == '/base/static/description/icon.png'


def test_filled_icon(module):
    module.manifest['icon'] = 'custom-path'
    assert module.icon == 'custom-path'


def test_existing_file_icon(module_a):
    assert 'icon' not in module_a.manifest
    assert module_a.icon == f'/{module_a.name}/static/description/icon.png'
