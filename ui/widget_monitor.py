from typing import Callable, Type
from PySide6.QtCore import (
    QObject,
    SignalInstance,
)
from PySide6.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QRadioButton,
    QDoubleSpinBox,
    QSpinBox,
    QWidget,
)

class WidgetMonitor(QObject):
    """Monitors widgets for user interaction and triggers callback."""

    def __init__(self, widgets: list[Type[QWidget]], callback: Callable):
        super().__init__()
        self.callback = callback
        self.connections: list[tuple[QWidget, SignalInstance]] = []
        self._callback_active: bool = False

        widget: QWidget
        for widget in widgets:
            signal_instance: SignalInstance = None

            if isinstance(widget, QLineEdit):
                signal_instance = widget.textEdited
            elif isinstance(widget, (QTextEdit, QPlainTextEdit)):
                signal_instance = widget.textChanged
            elif isinstance(widget, (QCheckBox, QRadioButton)):
                signal_instance = widget.toggled
            elif isinstance(widget, QComboBox):
                signal_instance = widget.currentIndexChanged
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                signal_instance = widget.valueChanged

            if signal_instance is not None:
                signal_instance.connect(self._on_interaction)
                self.connections.append((widget, signal_instance))


    def _on_interaction(self):
        """Internal handler that calls callback only once and disconnects all signals."""
        # sender = self.sender()
        # if sender:
        #     print(f"[WidgetMonitor] Interaction detected on: {sender.objectName() or type(sender).__name__}")


        if self._callback_active:
            self._callback_active = False
            self.callback()
            self._disconnect_all()


    def _disconnect_all(self):
        """Disconnect all monitored signals to stop receiving events."""
        for _, signal_instance in self.connections:
            try:
                signal_instance.disconnect(self._on_interaction)
            except RuntimeError:
                pass


    def _reconnect_all(self):
        """Reconnect all monitored signals."""
        for _, signal_instance in self.connections:
            try:
                signal_instance.connect(self._on_interaction)
            except RuntimeError:
                pass


    def reset(self):
        """Re-enable callback and reconnect signals."""
        self._callback_active = True
        self._reconnect_all()
