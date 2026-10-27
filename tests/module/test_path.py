from pathlib import Path


def test_path_like(module):
    assert module.__fspath__() == str(module.path)
    assert Path(module) == module.path


def test_relative_path(module):
    assert module / 'models/model.py' == module.path / 'models/model.py'
