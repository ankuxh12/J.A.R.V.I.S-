
import sys
import math
import random

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QRadialGradient
)
from PySide6.QtWidgets import QApplication, QWidget
from system_monitor import get_system_stats

class JarvisHUD(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS MARK V")
        self.setFixedSize(1040, 640)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

        self.frame = 0.0
        self.state = "SYSTEM ONLINE"
        self.speed = 1.0
        self.audio_level = 0.0
        self.display_audio_level = 0.0
        self.conversation_speaker = ""
        self.conversation_text = ""
        self.visible_characters = 0
        self.typewriter_tick = 0

        rng = random.Random(42)

        self.particles = [
            (
                rng.uniform(70, 290),
                rng.uniform(0, 360),
                rng.uniform(1, 2.5)
            )
            for _ in range(75)
        ]

        screen = QApplication.primaryScreen()

        if screen:
            geometry = screen.availableGeometry()

            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2
            )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(33)
        # MARK IX: System monitoring
        self.system_stats = {
            "cpu": 0,
            "ram": 0,
            "disk": 0,
            "battery": None,
            "charging": None
        }

        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.refresh_system_stats)
        self.system_timer.start(1000)

        self.refresh_system_stats()
    # ---------------------------------
    # ANIMATION
    # ---------------------------------
    def animate(self):
        self.frame += self.speed

    # Smooth audio reaction
        self.display_audio_level += (
        self.audio_level - self.display_audio_level
        ) * 0.28
        self.typewriter_tick += 1

        if self.typewriter_tick % 2 == 0:
            self.visible_characters = min(
                len(self.conversation_text),
                self.visible_characters + 2
            )
        self.update()
    

    def set_state(self, state):
        self.state = str(state).upper()

        speeds = {
            "STANDBY": 0.5,
            "LISTENING": 1.0,
            "THINKING": 3.0,
            "SPEAKING": 1.8,
            "SYSTEM ONLINE": 1.0
        }

        self.speed = speeds.get(self.state, 1.0)
        self.update()
    def set_audio_level(self, level):
        self.audio_level = max(
        0.0,
        min(1.0, float(level))
        )
    def refresh_system_stats(self):
        try:
            self.system_stats = get_system_stats()
            self.update()
        except Exception as error:
            print("System monitor error:", error)

    
    def set_conversation(self, speaker, text):
        self.conversation_speaker = str(speaker).upper()
        self.conversation_text = str(text)
        self.visible_characters = 0
        self.typewriter_tick = 0
        self.update()

    
    # ---------------------------------
    # DRAW GLOWING ARC
    # ---------------------------------

    def arc(
        self,
        painter,
        radius,
        start,
        span,
        color,
        width=2,
        glow=False
    ):

        rect = QRectF(
            -float(radius),
            -float(radius),
            float(radius * 2),
            float(radius * 2)
        )

        painter.save()

        try:
            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            if glow:
                for extra, alpha in [
                    (13, 12),
                    (8, 25),
                    (4, 45)
                ]:
                    glow_color = QColor(color)
                    glow_color.setAlpha(alpha)

                    painter.setPen(
                        QPen(
                            glow_color,
                            float(width + extra)
                        )
                    )

                    painter.drawArc(
                        rect,
                        int(start * 16),
                        int(span * 16)
                    )

            painter.setPen(
                QPen(
                    QColor(color),
                    float(width)
                )
            )

            painter.drawArc(
                rect,
                int(start * 16),
                int(span * 16)
            )

        finally:
            painter.restore()

    # ---------------------------------
    # SEGMENTED ROTATING RINGS
    # ---------------------------------

    def ring(
        self,
        painter,
        radius,
        rotation,
        segments,
        color,
        width,
        coverage=0.65
    ):

        painter.save()

        try:
            painter.rotate(rotation)

            step = 360.0 / segments
            span = step * coverage

            for i in range(segments):
                self.arc(
                    painter,
                    radius,
                    i * step,
                    span,
                    color,
                    width
                )

        finally:
            painter.restore()

    # ---------------------------------
    # RADAR TICKS
    # ---------------------------------

    def ticks(
        self,
        painter,
        radius,
        count,
        length,
        color,
        rotation=0,
        width=1
    ):

        painter.save()

        try:
            painter.rotate(rotation)

            painter.setPen(
                QPen(QColor(color), float(width))
            )

            for i in range(count):
                angle = math.radians(
                    i * 360.0 / count
                )

                major = i % 5 == 0

                tick_length = (
                    length * 1.8
                    if major
                    else length
                )

                x1 = math.cos(angle) * radius
                y1 = math.sin(angle) * radius

                x2 = math.cos(angle) * (
                    radius - tick_length
                )
                y2 = math.sin(angle) * (
                    radius - tick_length
                )

                painter.drawLine(
                    QPointF(x1, y1),
                    QPointF(x2, y2)
                )

        finally:
            painter.restore()

    # ---------------------------------
    # FLOATING PARTICLES
    # ---------------------------------

    def particles_effect(self, painter):

        painter.save()

        try:
            painter.setPen(
                Qt.PenStyle.NoPen
            )

            for radius, angle, size in self.particles:

                a = math.radians(
                    angle + self.frame * 0.12
                )

                x = math.cos(a) * radius
                y = math.sin(a) * radius

                alpha = int(
                    70 + 70 * (
                        0.5
                        + 0.5 * math.sin(
                            self.frame * 0.04 + radius
                        )
                    )
                )

                painter.setBrush(
                    QColor(0, 220, 255, alpha)
                )

                painter.drawEllipse(
                    QPointF(x, y),
                    size,
                    size
                )

        finally:
            painter.restore()

    # ---------------------------------
    # RADAR SCANNER
    # ---------------------------------

    def scanner(self, painter):

        painter.save()

        try:
            painter.rotate(self.frame * 0.8)

            gradient = QRadialGradient(
                0, 0, 280
            )

            gradient.setColorAt(
                0,
                QColor(0, 200, 255, 0)
            )

            gradient.setColorAt(
                0.65,
                QColor(0, 200, 255, 12)
            )

            gradient.setColorAt(
                1,
                QColor(0, 200, 255, 0)
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QBrush(gradient)
            )

            painter.drawPie(
                QRectF(-280, -280, 560, 560),
                0,
                35 * 16
            )

        finally:
            painter.restore()

    # ---------------------------------
    # CENTER AI CORE
    # ---------------------------------

    def center_core(self, painter):

        pulse = (
            0.5
            + 0.5 * math.sin(
                self.frame * 0.055
            )
        )

        painter.save()

        try:
            gradient = QRadialGradient(
                0, 0, 135
            )

            gradient.setColorAt(
                0,
                QColor(
                    0,
                    110,
                    160,
                    int(65 + pulse * 35)
                )
            )

            gradient.setColorAt(
                0.65,
                QColor(0, 65, 110, 55)
            )

            gradient.setColorAt(
                1,
                QColor(0, 180, 255, 0)
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QBrush(gradient)
            )

            painter.drawEllipse(
                QRectF(-135, -135, 270, 270)
            )

            self.arc(
                painter,
                118,
                0,
                360,
                "#36E7FF",
                2,
                True
            )
            # Voice-reactive inner ring
            level = self.display_audio_level

            reactive_radius = 122 + level * 15
            reactive_width = 2 + level * 6

            self.arc(
                painter,
                reactive_radius,
                0,
                360,
                "#7DF9FF",
                reactive_width,
                True
            )

            self.arc(
                painter,
                106,
                -self.frame * 0.8,
                230,
                "#58DFFF",
                3
            )

            self.arc(
                painter,
                106,
                180 + self.frame * 0.8,
                100,
                "#087BB9",
                3
            )

            # JARVIS title
            painter.setPen(
                QColor(190, 250, 255)
            )

            font = QFont(
                "Consolas",
                24,
                QFont.Weight.Bold
            )

            font.setLetterSpacing(
                QFont.SpacingType.AbsoluteSpacing,
                2
            )

            painter.setFont(font)

            painter.drawText(
                QRectF(-145, -32, 290, 65),
                Qt.AlignmentFlag.AlignCenter,
                "J.A.R.V.I.S."
            )

            # Current state
            painter.setPen(
                QColor(72, 225, 255)
            )

            painter.setFont(
                QFont("Consolas", 10)
            )

            painter.drawText(
                QRectF(-145, 30, 290, 30),
                Qt.AlignmentFlag.AlignCenter,
                self.state
            )

            painter.setPen(
                QColor(65, 170, 200, 170)
            )

            painter.setFont(
                QFont("Consolas", 7)
            )

            painter.drawText(
                QRectF(-145, 61, 290, 20),
                Qt.AlignmentFlag.AlignCenter,
                "ADVANCED INTELLIGENCE SYSTEM"
            )

        finally:
            painter.restore()

    # ---------------------------------
    # TECHNICAL HUD DETAILS
    # ---------------------------------

    def technical_details(self, painter):

        painter.save()

        try:
            painter.setFont(
                QFont("Consolas", 7)
            )

            painter.setPen(
                QColor(75, 195, 225, 160)
            )

            labels = [
                ("SYS // 001", -260, -170),
                ("ARC REACTOR", 155, -170),
                ("NEURAL LINK", -260, 180),
                ("MARK V", 195, 180),
                ("ONLINE", -45, -250),
                ("AI CORE", -35, 260)
            ]

            for text, x, y in labels:
                painter.drawText(x, y, text)

            painter.setPen(
                QPen(
                    QColor(0, 180, 220, 55),
                    1
                )
            )

            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            for radius in [145, 185, 225, 270]:
                painter.drawEllipse(
                    QRectF(
                        -radius,
                        -radius,
                        radius * 2,
                        radius * 2
                    )
                )

        finally:
            painter.restore()

    # ---------------------------------
    # LISTENING: SONAR RADAR MODE
    # ---------------------------------
    def listening_mode(self, painter):
        painter.save()
        try:
            # Clean sonar rings: deliberately different from the default HUD.
            for radius in (150, 205, 265):
                self.arc(painter, radius, 0, 360, "#146D88", 1.5)

            self.ring(painter, 276, -self.frame * 0.18, 48,
                      "#29DFFF", 3, 0.35)
            self.ticks(painter, 252, 72, 8, "#46DFFF",
                       self.frame * 0.10, 1.5)

            # Scanning needle and sweeping sector.
            painter.save()
            painter.rotate(self.frame * 1.5)
            sweep = QColor(0, 225, 255, 35)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(sweep))
            painter.drawPie(QRectF(-235, -235, 470, 470), 0, 40 * 16)
            painter.setPen(QPen(QColor("#6CF5FF"), 2))
            painter.drawLine(QPointF(0, 0), QPointF(235, 0))
            painter.restore()

            # Repeating expanding sonar echoes.
            phase = (self.frame * 1.8) % 105.0
            for offset in (0.0, 35.0, 70.0):
                distance = (phase + offset) % 105.0
                radius = 138 + distance
                opacity = max(0, int(115 * (1.0 - distance / 105.0)))
                echo = QColor(50, 240, 255, opacity)
                painter.setPen(QPen(echo, 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QRectF(-radius, -radius,
                                           radius * 2, radius * 2))

            self.arc(painter, 135, self.frame * 0.6, 150,
                     "#76F9FF", 4, True)
        finally:
            painter.restore()

    # ---------------------------------
    # SPEAKING: VOICE-REACTIVE REACTOR
    # ---------------------------------
    def speaking_mode(self, painter):
        painter.save()
        try:
            level = self.display_audio_level
            beat = 0.5 + 0.5 * math.sin(self.frame * 0.08)

            # Reactor shell, with a strong audio-driven radius and glow.
            self.arc(painter, 273, 0, 360, "#124E82", 2)
            self.ring(painter, 264, self.frame * 0.45, 64,
                      "#6BDBFF", 3.5, 0.45)
            self.ring(painter, 235, -self.frame * 0.7, 32,
                      "#1679CE", 5, 0.72)
            self.arc(painter, 218 + level * 9, 0, 360,
                     "#69EAFF", 3 + level * 5, True)

            # 64 radial energy bars react to actual Piper voice level.
            for i in range(64):
                angle = math.radians(i * 360.0 / 64.0)
                variation = 0.55 + 0.45 * math.sin(
                    i * 1.71 + self.frame * 0.12
                ) ** 2
                bar_length = 9 + (12 + level * 53) * variation
                inner = 157.0
                outer = inner + bar_length
                alpha = int(140 + 115 * min(1.0, level + beat * 0.2))
                painter.setPen(QPen(QColor(105, 235, 255, alpha),
                                    2.0 + level * 2.5))
                painter.drawLine(
                    QPointF(math.cos(angle) * inner,
                            math.sin(angle) * inner),
                    QPointF(math.cos(angle) * outer,
                            math.sin(angle) * outer)
                )

            self.arc(painter, 146 + level * 7, 0, 360,
                     "#9AF6FF", 2 + level * 5, True)
            self.ring(painter, 135, -self.frame * 1.2, 16,
                      "#4ABEFF", 3, 0.50)
        finally:
            painter.restore()

    # ---------------------------------
    # MAIN PAINT EVENT
    # ---------------------------------

    def draw_conversation(self, painter):
        if not self.conversation_text:
            return

        painter.save()

        try:
            # Lower HUD conversation panel
            panel = QRectF(-245, 195, 490, 95)

            painter.setPen(QPen(QColor(40, 205, 245, 160), 1))
            painter.setBrush(QBrush(QColor(0, 12, 26, 225)))
            painter.drawRoundedRect(panel, 12, 12)

            # Speaker label
            painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))

            if self.conversation_speaker == "YOU":
                painter.setPen(QColor("#72F5FF"))
            else:
                painter.setPen(QColor("#63B7FF"))

            painter.drawText(
                QRectF(-228, 203, 450, 20),
                Qt.AlignmentFlag.AlignLeft,
                self.conversation_speaker + " //"
            )

            # Typewriter text
            visible_text = self.conversation_text[
                :self.visible_characters
            ]

            painter.setFont(QFont("Consolas", 9))
            painter.setPen(QColor("#D7F8FF"))

            text_rect = QRectF(-228, 226, 455, 53)

            # Keep recent text visible when the answer is long
            if len(visible_text) > 140:
                visible_text = "..." + visible_text[-137:]

            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.AlignTop
                | Qt.TextFlag.TextWordWrap,
                visible_text
            )

        finally:
            painter.restore()
    
   
    def draw_system_monitor(self, painter):
        painter.save()

        try:
            # Coordinates relative to reactor center (320, 320)
            # Right-side panel begins outside the circular HUD
            panel = QRectF(325, -245, 365, 490)

            painter.setPen(QPen(QColor("#23DFF5"), 1.5))
            painter.setBrush(QBrush(QColor(0, 14, 26, 235)))
            painter.drawRoundedRect(panel, 14, 14)

            # Header
            painter.setPen(QColor("#63F7FF"))
            painter.setFont(
                QFont("Consolas", 15, QFont.Weight.Bold)
            )

            painter.drawText(
                QRectF(350, -220, 320, 35),
                Qt.AlignmentFlag.AlignLeft,
                "JARVIS SYSTEM MONITOR"
            )

            painter.setPen(QPen(QColor("#23DFF5"), 2))
            painter.drawLine(
                QPointF(350, -180),
                QPointF(660, -180)
            )

            stats = self.system_stats

            items = [
                ("CPU USAGE", stats.get("cpu")),
                ("RAM USAGE", stats.get("ram")),
                ("DISK USAGE", stats.get("disk")),
                ("BATTERY", stats.get("battery"))
            ]

            y = -140

            for label, value in items:
                painter.setFont(QFont("Consolas", 10))
                painter.setPen(QColor("#79EFFF"))

                if value is None:
                    display_value = "N/A"
                    percent = 0
                else:
                    display_value = f"{float(value):.0f}%"
                    percent = max(0, min(float(value), 100))

                painter.drawText(
                    QRectF(350, y, 300, 25),
                    Qt.AlignmentFlag.AlignLeft,
                    f"{label}: {display_value}"
                )

                # Progress bar background
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(20, 65, 85, 200))
                painter.drawRoundedRect(
                    QRectF(350, y + 28, 305, 10),
                    4, 4
                )

                # Live progress bar
                painter.setBrush(QColor("#27E5FF"))
                if percent > 0:
                    painter.drawRoundedRect(
                        QRectF(350, y + 28, 305 * percent / 100, 10),
                        4, 4
                    )

                y += 90

            # Footer
            painter.setPen(QColor("#4FAFC5"))
            painter.setFont(QFont("Consolas", 9))

            painter.drawText(
                QRectF(350, 205, 310, 22),
                Qt.AlignmentFlag.AlignLeft,
                "NEURAL SYSTEM // ONLINE"
            )

        finally:
            painter.restore()




    def paintEvent(self, event):

        painter = QPainter(self)

        try:
            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True
            )

            painter.translate(320, 320)

            # Holographic background
            gradient = QRadialGradient(
                0, 0, 310
            )

            gradient.setColorAt(
                0,
                QColor(0, 24, 37, 220)
            )

            gradient.setColorAt(
                0.7,
                QColor(0, 20, 33, 160)
            )

            gradient.setColorAt(
                1,
                QColor(0, 15, 25, 0)
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QBrush(gradient)
            )

            painter.drawEllipse(
                QRectF(-310, -310, 620, 620)
            )

            # Each voice state gets a completely different circle design.
            if self.state == "LISTENING":
                self.listening_mode(painter)
            elif self.state == "SPEAKING":
                self.speaking_mode(painter)
            else:
                # Animated scanner
                self.scanner(painter)

                # Outer glowing arcs
                self.arc(
                    painter,
                    280,
                    self.frame * 0.25,
                    270,
                    "#42E8FF",
                    4,
                    True
                )

                self.arc(
                    painter,
                    280,
                    195 - self.frame * 0.25,
                    120,
                    "#087CA9",
                    4
                )

                # Outer segmented ring
                self.ring(
                    painter,
                    266,
                    -self.frame * 0.18,
                    72,
                    "#159AB9",
                    2,
                    0.52
                )

                # Outer ticks
                self.ticks(
                    painter,
                    250,
                    120,
                    10,
                    "#31D8F5",
                    self.frame * 0.08
                )

                # Middle segmented ring
                self.ring(
                    painter,
                    220,
                    self.frame * 0.45,
                    36,
                    "#21C9F3",
                    7,
                    0.76
                )

                # Middle glowing arcs
                self.arc(
                    painter,
                    198,
                    -self.frame * 0.5,
                    245,
                    "#4EEAFF",
                    5,
                    True
                )

                self.arc(
                    painter,
                    198,
                    120 + self.frame * 0.5,
                    75,
                    "#F4C64E",
                    3
                )

                # Middle ticks
                self.ticks(
                    painter,
                    184,
                    96,
                    8,
                    "#4CCAE0",
                    -self.frame * 0.12
                )

                # Inner rings
                self.ring(
                    painter,
                    160,
                    -self.frame * 0.7,
                    48,
                    "#167EA8",
                    3,
                    0.5
                )

                self.ring(
                    painter,
                    143,
                    self.frame * 0.9,
                    24,
                    "#5DEBFF",
                    3,
                    0.72
                )

            # Details and center
            self.technical_details(painter)
            self.particles_effect(painter)
            self.center_core(painter)
            self.draw_system_monitor(painter)
            self.draw_conversation(painter)

        finally:
            # IMPORTANT:
            # Painter closes only AFTER drawing finishes.
            if painter.isActive():
                painter.end()

    # ---------------------------------
    # KEYBOARD CONTROLS
    # ---------------------------------
    def keyPressEvent(self, event):

    # ESC = Exit
        if event.key() == Qt.Key.Key_Escape:
            self.close()

        # Ctrl + Q = Exit
        elif (
            event.key() == Qt.Key.Key_Q
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.close()

        else:
            super().keyPressEvent(event)


# ---------------------------------
# STANDALONE TEST
# ---------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = JarvisHUD()
    window.show()
    window.activateWindow()
    window.setFocus()

    sys.exit(app.exec())
