def test_relative_path(module_a):
    assert module_a / 'models/model.py' == module_a.path / 'models/model.py'
