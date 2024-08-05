# coding: utf-8 

from PyQt5.QtCore import pyqtSignal, QThread

class EmbeddingWorker(QThread):
    progress_updated = pyqtSignal(dict)
    embedding_completed = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, backend, input_file, output_dir, model, output_name, output_format, batch_size):
        super().__init__()
        self.backend = backend
        self.input_file = input_file
        self.output_dir = output_dir
        self.model = model
        self.output_name = output_name
        self.output_format = output_format
        self.batch_size = batch_size

    def run(self):
        try:
            # Connect signals
            self.backend.progress_updated.connect(self.progress_updated.emit)
            self.backend.embedding_completed.connect(self.embedding_completed.emit)
            self.backend.error_occurred.connect(self.error_occurred.emit)
            
            self.backend.embed_file(self.input_file, self.output_dir, self.model, self.output_name, self.output_format, self.batch_size)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            # Disconnect signals
            try:
                self.backend.progress_updated.disconnect(self.progress_updated.emit)
            except TypeError:
                pass
            try:
                self.backend.embedding_completed.disconnect(self.embedding_completed.emit)
            except TypeError:
                pass
            try:
                self.backend.error_occurred.disconnect(self.error_occurred.emit)
            except TypeError:
                pass