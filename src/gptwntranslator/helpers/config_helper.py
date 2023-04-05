import yaml

from gptwntranslator.helpers.design_patterns_helper import singleton
from gptwntranslator.helpers.file_helper import read_file

@singleton
class Config:
    def __init__(self):
        self.data = None
        self.vars = dict()

    def load(self, path):
        if self.data is None:
            try:
                text = read_file(path)
                self.data = DotDict.from_dict_string(text)
            except Exception as e:
                raise Exception("Failed to load config file: " + str(e))
        else:
            raise Exception("Config already loaded")
        
    def get_language_name_for_code(self, language_code: str) -> str:
        return [lang[1] for lang in [list(dct.items())[0] for dct in self.data.config.languages] if lang[0] == language_code][0]
    
    def get_language_code_for_name(self, language_name: str) -> str:
        return [lang[0] for lang in [list(dct.items())[0] for dct in self.data.config.languages] if lang[1] == language_name][0]

    def get_spacy_pipeline_for_language_code(self, language_code: str) -> str:
        return [lang[1] for lang in [list(dct.items())[0] for dct in self.data.config.spacy.pipelines] if lang[0] == language_code][0]
    
    def get_spacy_pipeline_for_language_name(self, language_name: str) -> str:
        language_code = self.get_language_code_for_name(language_name)
        return self.get_spacy_pipeline_for_language_code(language_code)
    
    def get_languages(self):
        return [lang[0] for lang in [list(dct.items())[0] for dct in self.data.config.languages]]
    
class DotDict(dict):
    """A dictionary that supports dot notation."""

    def __getattr__(self, item):
        value = self.get(item)
        if isinstance(value, dict):
            return DotDict(value)
        else:
            return value

    def __setattr__(self, key, value):
        self[key] = value

    @classmethod
    def from_dict_string(cls, dict_string):
        return cls(yaml.safe_load(dict_string))
    
    def __str__(self):
        items = []
        for key, value in self.items():
            if isinstance(value, DotDict):
                items.append(f"{key}: {str(value)}")
            else:
                items.append(f"{key}: {value}")
        return "{" + ", ".join(items) + "}"
    
