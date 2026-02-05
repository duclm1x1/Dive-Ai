_# AEH Engine - Recovery Strategies

class RecoveryStrategy:
    def __init__(self, logger):
        self.logger = logger

    def get_recovery_action(self, error, context):
        """Determine the best recovery action for a given error."""
        error_type = type(error).__name__

        if error_type == "ZeroDivisionError":
            return self.handle_zero_division(error, context)
        elif error_type == "FileNotFoundError":
            return self.handle_file_not_found(error, context)
        # Add more error handling strategies here
        else:
            return None

    def handle_zero_division(self, error, context):
        """Handle a ZeroDivisionError."""
        self.logger.log_info("Recovery: Returning a default value for ZeroDivisionError.")
        return {"action": "return_default", "value": float('inf')}

    def handle_file_not_found(self, error, context):
        """Handle a FileNotFoundError."""
        file_path = error.filename
        self.logger.log_info(f"Recovery: Attempting to create the missing file: {file_path}")
        return {"action": "create_file", "path": file_path}
_

        elif error_type == "KeyError":
            return self.handle_key_error(error, context)
        elif error_type == "requests.exceptions.RequestException":
            return self.handle_request_exception(error, context)

    def handle_key_error(self, error, context):
        """Handle a KeyError."""
        missing_key = error.args[0]
        self.logger.log_info(f"Recovery: Attempting to use a default value for missing key: {missing_key}")
        return {"action": "use_default_value", "key": missing_key, "default": None}

    def handle_request_exception(self, error, context):
        """Handle a network request exception."""
        self.logger.log_info("Recovery: Retrying the network request.")
        return {"action": "retry_request"}
