import sys
import threading
import time
import multiprocessing
from PyQt6.QtWidgets import QApplication

# Adjust path to ensure imports work both in dev and compiled mode
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.backend.main import start_backend
from src.frontend.floating_ball import FloatingBall
from src.frontend.task_window import TaskWindow

def run_backend():
    # Disable signal handling in uvicorn when running in a thread
    # to avoid conflict with PyQt or main thread signals
    # However, uvicorn.run doesn't have a simple flag for that in the convenience function
    # but running it in a thread usually works if we don't need graceful shutdown via signals.
    start_backend(port=8000)

def main():
    # 1. Multiprocessing support for Nuitka/Windows
    multiprocessing.freeze_support()

    # 2. Start Backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Give backend a moment to start (optional, but helps avoid initial connection error)
    time.sleep(1)

    # 3. Start PyQt Application
    app = QApplication(sys.argv)
    
    # Prevent the app from quitting when the last window is closed
    # because we want the floating ball to persist even if task window is closed
    app.setQuitOnLastWindowClosed(False)

    # 4. Initialize Windows
    task_window = TaskWindow()
    ball = FloatingBall()

    # 5. Connect Ball Click to Task Window
    def show_tasks():
        task_window.show()
        task_window.activateWindow() # Bring to front
        task_window.refresh_tasks()  # Refresh data

    ball.clicked_callback = show_tasks
    ball.show()

    # 6. Run Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
