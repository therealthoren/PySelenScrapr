
class ValidationError (Exception):
    validation_error_message = None

    def __init__(self, validation_error_message):
        super().__init__(validation_error_message)
        self.validation_error_message = validation_error_message

    def __str__(self):
        return self.validation_error_message