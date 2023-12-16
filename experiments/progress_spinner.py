from PyQt6.QtWidgets import QApplication, QProgressDialog, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QThread

class WorkerThread(QThread):
    def run(self):
        # Simulate some time-consuming work
        import time
        time.sleep(5)

class BusyWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        button = QPushButton("Do Work", self)
        button.clicked.connect(self.show_busy_dialog)

        layout.addWidget(button)

    def show_busy_dialog(self):
        progressDialog = QProgressDialog(self)
        progressDialog.setLabelText("Working...")
        progressDialog.setRange(0, 0)  # Infinite progress
        progressDialog.show()

        worker_thread = WorkerThread()
        worker_thread.finished.connect(progressDialog.accept)

        worker_thread.start()

if __name__ == "__main__":
    app = QApplication([])

    window = BusyWindow()
    window.show()

    app.exec()
