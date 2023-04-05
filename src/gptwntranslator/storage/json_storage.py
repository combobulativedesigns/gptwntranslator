import json
from gptwntranslator.encoders.json_encoder import JsonEncoder
from gptwntranslator.helpers.design_patterns_helper import singleton
from gptwntranslator.helpers.file_helper import read_file, write_file
from gptwntranslator.helpers.text_helper import make_printable
from gptwntranslator.hooks.object_hook import generic_object_hook

class JsonStorageException(Exception):
    pass

class JsonStorageFormatException(JsonStorageException):
    pass

class JsonStorageFileException(JsonStorageException):
    pass

@singleton
class JsonStorage:

    def __init__(self):
        self._storage_file = ""
        self._data = None

    def initialize(self, storage_file):
        self._storage_file = storage_file
        self._data = None

    def get_data(self):
        if self._data is None:
            self._read()
        return self._data
    
    def set_data(self, data):
        self._data = data
        self._write()

    def _read(self):
        try:
            data_str = read_file(self._storage_file)
        except Exception as e:
            raise JsonStorageFileException(f"Error reading storage file: {e}")
        try:
            self._data = json.loads(data_str, object_hook=generic_object_hook)
        except Exception as e:
            raise JsonStorageFormatException(f"Error parsing storage file: {e}")
        
    def _write(self):
        try:
            novel_printable = make_printable(json.dumps(self._data, ensure_ascii=False, cls=JsonEncoder))
        except Exception as e:
            raise JsonStorageFormatException(f"Error converting data to JSON: {e}")
        try:
            write_file(self._storage_file, novel_printable)
        except Exception as e:
            raise JsonStorageFileException(f"Error writing storage file: {e}")