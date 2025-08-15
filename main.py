from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import sys

from chat_ui import ChatWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Jetson LLM Chat")

    win = ChatWindow()
    win.show()

    # Optional: show a welcome message after the window is visible
    QTimer.singleShot(150, lambda: win.add_message("system", "Welcome! Phase 1 UI (PySide6) is running."))

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
