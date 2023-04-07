import logging

class SingletonLogger:
    def __init__(self):
        self.logger = logging.getLogger('gptwntranslator')

    def initialize(self, log_file_path, log_level):
        self.logger.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler = logging.FileHandler(log_file_path)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)


class CustomLogger:
    def __init__(self, module_path):
        self.logger = SingletonLogger().logger
        self.module_path = module_path

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(f"{self.module_path}: {msg}", *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(f"{self.module_path}: {msg}", *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(f"{self.module_path}: {msg}", *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(f"{self.module_path}: {msg}", *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(f"{self.module_path}: {msg}", *args, **kwargs)