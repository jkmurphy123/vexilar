from PyQt6 import QtCore, QtGui, QtWidgets

class MessageBubble(QtWidgets.QFrame):
    """
    Simple rounded bubble with role-aware colors and optional typing style.
    """
    def __init__(self, text: str, align_right: bool, role: str = "assistant", is_typing: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("Bubble")

        self._role = role
        self._align_right = align_right
        self._is_typing = is_typing

        # Layout to support left/right alignment
        outer = QtWidgets.QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        spacer_left = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        spacer_right = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        if align_right:
            outer.addItem(spacer_left)

        # Bubble container
        self.inner = QtWidgets.QFrame(self)
        self.inner.setObjectName("Bubble")
        self.inner.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        inner_layout = QtWidgets.QVBoxLayout(self.inner)
        inner_layout.setContentsMargins(14, 10, 14, 10)

        self.label = QtWidgets.QLabel(self.inner)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse |
            QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        font = self.label.font()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setText(("…" if is_typing else text))
        inner_layout.addWidget(self.label)

        # Apply role styles
        pal = self.inner.palette()
        if role == "user":
            bg = QtGui.QColor("#1f2a44")
            fg = QtGui.QColor("#e9f0ff")
        elif role == "system":
            bg = QtGui.QColor("#2a2e35")
            fg = QtGui.QColor("#cbd3e1")
        else:  # assistant
            bg = QtGui.QColor("#1c2630")
            fg = QtGui.QColor("#e8eaf0")

        self._set_colors(self.inner, bg, fg)

        outer.addWidget(self.inner, stretch=0)

        if not align_right:
            outer.addItem(spacer_right)

        # Limit max width so long messages wrap nicely
        self.setMaximumWidth(900)
        self.inner.setMaximumWidth(720)

        # Shadow for a bit of depth
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(24)
        effect.setColor(QtGui.QColor(0, 0, 0, 160))
        effect.setOffset(0, 4)
        self.setGraphicsEffect(effect)

    def _set_colors(self, widget, bg: QtGui.QColor, fg: QtGui.QColor):
        pal = widget.palette()
        pal.setColor(QtGui.QPalette.ColorRole.Window, bg)
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, fg)
        widget.setAutoFillBackground(True)
        widget.setPalette(pal)
        widget.setStyleSheet(f"QFrame#Bubble {{ background-color: {bg.name()}; color: {fg.name()}; }}")
