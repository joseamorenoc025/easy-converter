import time

class ConversionProgress:
    """
    Gestiona el estado y los callbacks del progreso de conversión.
    """
    def __init__(self, on_update=None, on_complete=None, on_error=None):
        self.on_update = on_update      # Callback: (percent, message)
        self.on_complete = on_complete  # Callback: (result_path)
        self.on_error = on_error        # Callback: (error_obj)
        
        self.start_time = 0
        self.current_percent = 0
        self.current_message = ""

    def start(self, message="Iniciando..."):
        self.start_time = time.time()
        self.update(0, message)

    def update(self, percent, message=None):
        self.current_percent = percent
        if message:
            self.current_message = message
        
        if self.on_update:
            self.on_update(self.current_percent, self.current_message)

    def complete(self, result_path):
        if self.on_complete:
            self.on_complete(result_path)

    def error(self, error_obj):
        if self.on_error:
            self.on_error(error_obj)

    def get_elapsed_time(self):
        return time.time() - self.start_time
