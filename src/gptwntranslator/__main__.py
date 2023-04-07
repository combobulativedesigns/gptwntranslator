import logging
import os
from gptwntranslator.helpers.logger_helper import CustomLogger, SingletonLogger
from gptwntranslator.interactive import run_interactive

def main():
    logging_file_path = os.path.join(os.getcwd(), "gptwntranslator.log")
    main_logger = SingletonLogger()
    main_logger.initialize(logging_file_path, logging.DEBUG)

    logger = CustomLogger(__name__)

    logger.info("Starting gptwntranslator...")
    logger.info(f"Logging to: {logging_file_path}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Mode set to: interactive")

    run_interactive()

if __name__ == "__main__":
    main()