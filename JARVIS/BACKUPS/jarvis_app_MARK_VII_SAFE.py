
import sys
import signal
import traceback

from PySide6.QtCore import QObject, QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication

from jarvis_ui import JarvisHUD


class JarvisWorker(QObject):

    state_changed = Signal(str)
    hud_visible = Signal(bool)
    audio_level_changed = Signal(float)
    finished = Signal()

    def run(self):
        try:
            import main

            thread = QThread.currentThread()

            main.state_callback = self.state_changed.emit
            import speak as speak_module
            speak_module.audio_level_callback = self.audio_level_changed.emit

            while not thread.isInterruptionRequested():

                self.state_changed.emit("STANDBY")
                self.hud_visible.emit(False)

                # Wait for Hey Jarvis, but allow shutdown
                detected = main.wait_for_wake_word(
                    stop_requested=thread.isInterruptionRequested
                )

                if not detected or thread.isInterruptionRequested():
                    break

                self.hud_visible.emit(True)
                self.state_changed.emit("LISTENING")

                # Conversation ends on Goodbye or shutdown
                main.conversation_mode(
                    stop_requested=thread.isInterruptionRequested
                )

                self.hud_visible.emit(False)

        except Exception:
            print("JARVIS worker error:")
            traceback.print_exc()

        finally:
            self.hud_visible.emit(False)
            self.finished.emit()


class JarvisApp(JarvisHUD):
    def closeEvent(self, event):

        if not self.shutting_down:
            self.shutting_down = True

            print("JARVIS shutdown requested...")

            self.thread.requestInterruption()
            self.hide()

        event.ignore()
    def __init__(self):
        super().__init__()

        self.hide()
        self.shutting_down = False

        self.thread = QThread(self)
        self.worker = JarvisWorker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.state_changed.connect(self.set_state)
        self.worker.audio_level_changed.connect(self.set_audio_level)
        self.worker.hud_visible.connect(self.setVisible)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(
            QApplication.instance().quit
        )

        self.thread.start()

    def closeEvent(self, event):

        if not self.shutting_down:
            self.shutting_down = True

            print("JARVIS shutdown requested...")

            self.thread.requestInterruption()
            self.hide()

        # Do not destroy the window while the thread is running.
        # The app quits after the worker finishes.
        event.ignore()



if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Standby mein HUD hidden hota hai.
    # Isliye Qt ko running rehne do.
    app.setQuitOnLastWindowClosed(False)

    window = JarvisApp()

    # Ctrl+C aane par graceful shutdown request
    def shutdown_handler(signum, frame):
        print("\nCtrl+C detected. Shutting down JARVIS...")
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        window.close()

    signal.signal(signal.SIGINT, shutdown_handler)

    # Qt event loop ko periodically Python signals
    # process karne ka mauka deta hai.
    signal_timer = QTimer()
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(100)

    sys.exit(app.exec())

