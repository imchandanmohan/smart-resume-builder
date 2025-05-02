import traceback
import sys

class CustomException(Exception):

    def __init__(self, error_message, error_detail:sys):
        super().__init__(error_message)
        self.error_messgae = self.get_detailed_error_message(
            error_message=error_message,
            error_detail=error_detail
        )

    @staticmethod
    def get_detailed_error_message(error_message, error_detail):
        exc_type, exc_obj, exc_tb = sys.exc_info()  # ✅ This is correct
        if exc_tb is not None:
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
            return f"Issue in {file_name} at line {line_number}: {error_message}"
        else:
            return f"{error_message} (no traceback available)"
        
        
    def __str__(self):

        return self.error_messgae