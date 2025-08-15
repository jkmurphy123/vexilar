from PyQt6 import QtCore, QtGui, QtWidgets
from message_bubble import MessageBubble

class ChatWindow(QtWidgets.QMainWindow):
    """
    Chat-style main window prepared for future LLM integration.
    - Left/right aligned bubbles based on sender
    - Scrollable history
    - Input area with Ctrl+Enter to send
    - F11 toggles fullscreen
    """
    sendRequested = QtCore.pyqtSignal(str)  # emitted when user presses send

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Jetson Orin Nano — LLM UI (Phase 1)")
        self.resize(980, 720)

        self._build_ui()
        self._wire_shortcuts()

        # For Phase 2 you can connect this signal to an LLM handler
        self.sendRequested.connect(self._on_user_send)

    # ---------- UI layout ----------
    def _build_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # Scroll area for chat history
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        root.addWidget(self.scrollArea, stretch=1)

        self.historyContainer = QtWidgets.QWidget()
        self.historyLayout = QtWidgets.QVBoxLayout(self.historyContainer)
        self.historyLayout.setContentsMargins(0, 0, 0, 0)
        self.historyLayout.setSpacing(8)
        self.historyLayout.addStretch(1)
        self.scrollArea.setWidget(self.historyContainer)

        # Input row
        inputRow = QtWidgets.QHBoxLayout()
        inputRow.setSpacing(8)
        root.addLayout(inputRow, stretch=0)

        self.inputEdit = GrowingTextEdit(self)
        self.inputEdit.setPlaceholderText("Type a message…")
        self.inputEdit.setMinimumHeight(44)
        self.inputEdit.setMaximumHeight(140)
        font = self.inputEdit.font()
        font.setPointSize(11)
        self.inputEdit.setFont(font)
        inputRow.addWidget(self.inputEdit, stretch=1)

        self.sendBtn = QtWidgets.QPushButton("Send")
        self.sendBtn.setDefault(True)
        self.sendBtn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.sendBtn.clicked.connect(self._emit_send)
        inputRow.addWidget(self.sendBtn, stretch=0)

        # Status bar
        self.status = self.statusBar()
        self.status.showMessage("Phase 1 — UI only")

        # Initial style (simple, readable)
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #0e0f11; }
            QScrollArea { background: transparent; border: none; }
            QWidget#Bubble {
                border-radius: 14px;
                padding: 10px 12px;
            }
            QTextEdit, QPlainTextEdit {
                background: #16181c;
                color: #e8eaf0;
                border: 1px solid #2a2e35;
                border-radius: 10px;
            }
            QPushButton {
                background: #2962ff;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton:hover { background: #3d73ff; }
            QPushButton:pressed { background: #2254e6; }
        """)

    def _wire_shortcuts(self):
        # Ctrl+Enter to send
        send_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self)
        send_shortcut.activated.connect(self._emit_send)
        send_shortcut2 = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Enter"), self)
        send_shortcut2.activated.connect(self._emit_send)

        # F11 fullscreen toggle
        full_shortcut = QtGui.QShortcut(QtGui.QKeySequence("F11"), self)
        full_shortcut.activated.connect(self._toggle_fullscreen)

    # ---------- Public API ----------
    def add_message(self, role: str, text: str):
        """
        role: 'user' | 'assistant' | 'system'
        """
        align_right = (role == "user")
        bubble = MessageBubble(text=text, align_right=align_right, role=role, parent=self.historyContainer)
        # Insert above the stretch
        self.historyLayout.insertWidget(self.historyLayout.count() - 1, bubble, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        QtCore.QTimer.singleShot(0, self._ensure_visible)

    def set_typing(self, on: bool):
        """Show or hide a 'typing…' placeholder (for Phase 2)."""
        if on and not hasattr(self, "_typing_label"):
            self._typing_label = MessageBubble(text="typing…", align_right=False, role="assistant", is_typing=True)
            self.historyLayout.insertWidget(self.historyLayout.count() - 1, self._typing_label, 0)
            QtCore.QTimer.singleShot(0, self._ensure_visible)
        elif not on and hasattr(self, "_typing_label"):
            self._typing_label.deleteLater()
            del self._typing_label

    # ---------- Internals ----------
    def _emit_send(self):
        text = self.inputEdit.toPlainText().strip()
        if not text:
            return
        self.inputEdit.clear()
        self.add_message("user", text)
        self.sendRequested.emit(text)

    def _on_user_send(self, text: str):
        """
        Phase 1: UI echo. Phase 2: replace with LLM call.
        """
        # (Optional) quick echo so UI feels alive during Phase 1
        self.set_typing(True)
        QtCore.QTimer.singleShot(300, lambda: self._finish_echo(text))

    def _finish_echo(self, text: str):
        self.set_typing(False)
        self.add_message("assistant", f"(echo) You said: {text}")

    def _ensure_visible(self):
        bar = self.scrollArea.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.status.showMessage("Exited fullscreen (F11 to toggle).")
        else:
            self.showFullScreen()
            self.status.showMessage("Fullscreen (F11 to exit).")


class GrowingTextEdit(QtWidgets.QPlainTextEdit):
    """
    Grows up to a max height as the user types, then scrolls.
    """
    textHeightChanged = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document().setDocumentMargin(8)
        self.setTabChangesFocus(True)
        self.document().contentsChanged.connect(self._recalc_height)

    def _recalc_height(self):
        doc = self.document()
        margins = self.contentsMargins()
        h = int(doc.size().height() + margins.top() + margins.bottom()) + 8
        h = max(44, min(h, self.maximumHeight()))
        if self.height() != h:
            self.setFixedHeight(h)
            self.textHeightChanged.emit(h)
