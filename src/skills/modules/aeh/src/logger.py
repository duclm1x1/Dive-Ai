_# AEH Engine - Logger

import logging

class AEHLogger:
    def __init__(self, log_file, level=logging.INFO):
        self.logger = logging.getLogger("AEHEngine")
        self.logger.setLevel(level)
        
        # Create file handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(fh)

    def log_error(self, error, context):
        self.logger.error(f"Error: {error} | Context: {context}")

    def log_warning(self, message):
        self.logger.warning(message)

    def log_info(self, message):
        self.logger.info(message)
_
