from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys

from chat_ui import ChatWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Jetson LLM Chat (PyQt5)")

    win = ChatWindow()
    win.show()

    QTimer.singleShot(150, lambda: win.add_message("system", "Welcome! Phase 1 UI (PyQt5) is running."))

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
