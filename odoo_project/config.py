from dataclasses import dataclass, field

import tomlkit


@dataclass(order=True)
class Config:
    project_module_dirs: list[str] = field(default_factory=list)
    third_party_module_dirs: list[str] = field(default_factory=list)
    include_modules: list[str] = field(default_factory=list)
    exclude_modules: list[str] = field(default_factory=list)


def read_config(path):
    with path.open() as config_file:
        config = tomlkit.load(config_file)

    return Config(**config.unwrap())
