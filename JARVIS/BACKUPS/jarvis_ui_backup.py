
import sys
import math
import random

from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush,
    QFont, QRadialGradient
)
from PySide6.QtWidgets import QApplication, QWidget


class JarvisHUD(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS MARK V")
        self.setFixedSize(640, 640)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.frame = 0
        self.state = "SYSTEM ONLINE"

        random.seed(42)
        self.particles = [
            (
                random.uniform(70, 290),
                random.uniform(0, 360),
                random.uniform(1, 2.5)
            )
            for _ in range(75)
        ]

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(33)

    def animate(self):
        self.frame += 1
        self.update()

    def arc(self, painter, radius, start, span,
            color, width=2, glow=False):

        rect = (-radius, -radius, radius * 2, radius * 2)

        if glow:
            for extra, alpha in [(13, 12), (8, 25), (4, 45)]:
                c = QColor(color)
                c.setAlpha(alpha)
                painter.setPen(QPen(c, width + extra))
                painter.drawArc(
                    *rect,
                    int(start * 16),
                    int(span * 16)
                )

        painter.setPen(QPen(QColor(color), width))
        painter.drawArc(
            *rect,
            int(start * 16),
            int(span * 16)
        )

    def ring(self, painter, radius, rotation,
             segments, color, width, coverage=0.65):

        painter.save()
        painter.rotate(rotation)

        step = 360 / segments
        span = step * coverage

        for i in range(segments):
            start = i * step

            self.arc(
                painter,
                radius,
                start,
                span,
                color,
                width
            )

        painter.restore()

    def ticks(self, painter, radius, count,
              length, color, rotation=0, width=1):

        painter.save()
        painter.rotate(rotation)

        painter.setPen(QPen(QColor(color), width))

        for i in range(count):
            angle = math.radians(i * 360 / count)

            major = i % 5 == 0
            tick_length = length * 1.8 if major else length

            x1 = math.cos(angle) * radius
            y1 = math.sin(angle) * radius

            x2 = math.cos(angle) * (radius - tick_length)
            y2 = math.sin(angle) * (radius - tick_length)

            painter.drawLine(
                QPointF(x1, y1),
                QPointF(x2, y2)
            )

        painter.restore()

    def particles_effect(self, painter):
        for radius, angle, size in self.particles:
            a = math.radians(angle + self.frame * 0.12)

            x = math.cos(a) * radius
            y = math.sin(a) * radius

            alpha = int(
                70 + 70 * (
                    0.5 + 0.5 * math.sin(self.frame * 0.04 + radius)
                )
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 220, 255, alpha))
            painter.drawEllipse(
                QPointF(x, y),
                size,
                size
            )

    def scanner(self, painter):
        painter.save()
        painter.rotate(self.frame * 0.8)

        gradient = QRadialGradient(0, 0, 280)
        gradient.setColorAt(0, QColor(0, 200, 255, 0))
        gradient.setColorAt(0.65, QColor(0, 200, 255, 8))
        gradient.setColorAt(1, QColor(0, 200, 255, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPie(
            -280, -280, 560, 560,
            0, 35 * 16
        )

        painter.restore()

    def center_core(self, painter):
        pulse = 0.5 + 0.5 * math.sin(self.frame * 0.055)

        gradient = QRadialGradient(0, 0, 135)

        gradient.setColorAt(
            0,
            QColor(0, 110, 160, int(65 + pulse * 35))
        )
        gradient.setColorAt(
            0.65,
            QColor(0, 65, 110, 55)
        )
        gradient.setColorAt(
            1,
            QColor(0, 180, 255, 0)
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(-135, -135, 270, 270)

        self.arc(
            painter, 118, 0, 360,
            "#36E7FF", 2, True
        )

        self.arc(
            painter, 106,
            -self.frame * 0.8,
            230,
            "#58DFFF", 3
        )

        self.arc(
            painter, 106,
            180 + self.frame * 0.8,
            100,
            "#087BB9", 3
        )

        painter.setPen(QColor(190, 250, 255))
        font = QFont("Consolas", 24, QFont.Weight.Bold)
        font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing, 2
        )
        painter.setFont(font)

        painter.drawText(
            -145, -32, 290, 65,
            Qt.AlignmentFlag.AlignCenter,
            "J.A.R.V.I.S."
        )

        painter.setPen(QColor(72, 225, 255))
        painter.setFont(QFont("Consolas", 10))

        painter.drawText(
            -145, 30, 290, 30,
            Qt.AlignmentFlag.AlignCenter,
            self.state
        )

        painter.setPen(QColor(65, 170, 200, 170))
        painter.setFont(QFont("Consolas", 7))

        painter.drawText(
            -145, 61, 290, 20,
            Qt.AlignmentFlag.AlignCenter,
            "ADVANCED INTELLIGENCE SYSTEM"
        )

    def technical_details(self, painter):
        painter.setFont(QFont("Consolas", 7))
        painter.setPen(QColor(75, 195, 225, 160))

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

        painter.setPen(QPen(QColor(0, 180, 220, 55), 1))

        for r in [145, 185, 225, 270]:
            painter.drawEllipse(-r, -r, 2 * r, 2 * r)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.translate(
            self.width() / 2,
            self.height() / 2
        )

        # Subtle dark holographic background
        gradient = QRadialGradient(0, 0, 310)
        gradient.setColorAt(0, QColor(0, 24, 37, 220))
        gradient.setColorAt(0.7, QColor(0, 20, 33, 160))
        gradient.setColorAt(1, QColor(0, 15, 25, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(-310, -310, 620, 620)

        self.scanner(painter)

        # Outer rings
        self.arc(
            painter, 280,
            self.frame * 0.25,
            270,
            "#42E8FF", 4, True
        )

        self.arc(
            painter, 280,
            195 - self.frame * 0.25,
            120,
            "#087CA9", 4
        )

        self.ring(
            painter, 266,
            -self.frame * 0.18,
            72, "#159AB9", 2, 0.52
        )

        self.ticks(
            painter, 250,
            120, 10, "#31D8F5",
            self.frame * 0.08
        )

        # Middle ring
        self.ring(
            painter, 220,
            self.frame * 0.45,
            36, "#21C9F3", 7, 0.76
        )

        self.arc(
            painter, 198,
            -self.frame * 0.5,
            245,
            "#4EEAFF", 5, True
        )

        self.arc(
            painter, 198,
            120 + self.frame * 0.5,
            75,
            "#F4C64E", 3
        )

        self.ticks(
            painter, 184,
            96, 8, "#4CCAE0",
            -self.frame * 0.12
        )

        # Inner technical rings
        self.ring(
            painter, 160,
            -self.frame * 0.7,
            48, "#167EA8", 3, 0.5
        )

        self.ring(
            painter, 143,
            self.frame * 0.9,
            24, "#5DEBFF", 3, 0.72
        )

        self.technical_details(painter)
        self.particles_effect(painter)
        self.center_core(painter)

        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = JarvisHUD()
    window.show()
    window.activateWindow()
    window.setFocus()

    sys.exit(app.exec())
