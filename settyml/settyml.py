import os
import re

import yaml


class SettingsNotFoundError(BaseException):
    pass


class NoValueSetToDefaultError(BaseException):
    pass


class Reader(dict):

    env_var_matcher = re.compile(r'\$\{([^}^{]+)\}')

    def __init__(self, yaml_settings: str):
        self.settings = Reader.load_settings_yaml(yaml_settings)
        super().__init__(self.settings)

    @staticmethod
    def load_settings_yaml(yaml_settings: str):
        try:
            with open(yaml_settings, 'r') as settings_stream:
                settings_dict = yaml.safe_load(settings_stream)
            return Reader._filter_for_settings(settings_dict)
        except FileNotFoundError as file_err:
            settings_dict = yaml.safe_load(yaml_settings)
            if isinstance(settings_dict, dict):
                return Reader._filter_for_settings(settings_dict)
            else:
                raise FileNotFoundError(file_err)

    @staticmethod
    def _filter_for_settings(_dict):
        try:
            settings = _dict['Settings']
            return Reader.read(settings)
        except KeyError:
            raise SettingsNotFoundError('Settings should be a defined '
                                        'section in provided YAML')

    @staticmethod
    def read(_dict, parent_keys=None, result_dict=None, level=0):
        if result_dict is None:
            result_dict = _dict.copy()
        if parent_keys is None:
            parent_keys = []
        for k, v in _dict.items():
            if isinstance(v, dict):
                if set(v.keys()) == {'value', 'default'}:
                    all_keys = parent_keys + [k]
                    new_value = os.path.expandvars(v['value'])
                    default = os.path.expandvars(v['default'])
                    new_value = Reader._fill_with_defaults(new_value,
                                                           default)
                    Reader._nested_set(result_dict, all_keys, new_value)
                else:
                    all_keys = parent_keys + [k]
                    new_level = level + 1
                    Reader.read(v, parent_keys=all_keys,
                                result_dict=result_dict, level=new_level)
            elif k not in {'value', 'default'}:
                all_keys = parent_keys + [k]
                new_value = Reader._expandvars_with_none(v)
                Reader._nested_set(result_dict, all_keys, new_value)
            elif k == 'value':
                new_value = Reader._expandvars_with_none(v)
                Reader._nested_set(result_dict, parent_keys, new_value)
            elif k == 'default':
                raise NoValueSetToDefaultError(f'Key in settings with parent '
                                               f'keys {parent_keys} has '
                                               f'default key without value '
                                               f'key.')
        return result_dict if level == 0 else None

    @staticmethod
    def _nested_set(dic, keys, value):
        for key in keys[:-1]:
            dic = dic[key]
        dic[keys[-1]] = value

    @staticmethod
    def _fill_with_defaults(new_value, default):
        matches = Reader.env_var_matcher.findall(new_value)
        if len(matches) > 0:
            new_value = default
        return new_value

    @staticmethod
    def _expandvars_with_none(value):
        new_value = os.path.expandvars(value)
        matches = Reader.env_var_matcher.findall(new_value)
        if len(matches) > 0:
            new_value = None
        return new_value
