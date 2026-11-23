
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


class JarvisHUD(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS MARK V")
        self.setFixedSize(640, 640)

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

    # ---------------------------------
    # ANIMATION
    # ---------------------------------
    def animate(self):
        self.frame += self.speed

    # Smooth audio reaction
        self.display_audio_level += (
        self.audio_level - self.display_audio_level
        ) * 0.28

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
    # MAIN PAINT EVENT
    # ---------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        try:
            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True
            )

            painter.translate(
                self.width() / 2,
                self.height() / 2
            )

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
