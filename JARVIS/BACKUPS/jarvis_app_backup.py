import sys

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication

from jarvis_ui import JarvisHUD


class JarvisWorker(QObject):
    state_changed = Signal(str)
    hud_visible = Signal(bool)
    finished = Signal()

    def run(self):
        
        try:
            import main

            main.state_callback = self.state_changed.emit
            

            while not QThread.currentThread().isInterruptionRequested():
                self.state_changed.emit("STANDBY")
                self.hud_visible.emit(False)

                main.wait_for_wake_word()

                self.hud_visible.emit(True)
                self.state_changed.emit("LISTENING")

                main.conversation_mode()

        except Exception as error:
            print("JARVIS worker error:", error)

        finally:
            self.finished.emit()


class JarvisApp(JarvisHUD):
    def __init__(self):
        super().__init__()
        self.hide()

        self.thread = QThread(self)
        self.worker = JarvisWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.state_changed.connect(self.set_state)
        self.worker.hud_visible.connect(self.setVisible)

        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def closeEvent(self, event):
        # Stop requesting new work; an active audio read
        # may need to finish before the worker exits.
        self.thread.requestInterruption()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = JarvisApp()

    sys.exit(app.exec())
