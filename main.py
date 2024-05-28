from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsPolygonItem, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt5.QtGui import QPolygonF, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
import sys
import math


def create_hexagon(center, size):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        x = center.x() + size * math.cos(angle)
        y = center.y() + size * math.sin(angle)
        points.append(QPointF(x, y))
    return QPolygonF(points)


class HexTile(QGraphicsPolygonItem):
    def __init__(self, center, size, color):
        super().__init__(create_hexagon(center, size))
        self.setBrush(QBrush(color))
        self.setPen(QColor(0, 0, 0))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setBrush(QBrush(QColor(255, 0, 0)))  # 색상을 빨간색으로 변경
        elif event.button() == Qt.RightButton:
            self.setBrush(QBrush(QColor(0, 255, 0)))  # 색상을 초록색으로 변경


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.rows = 5
        self.cols = 5
        self.size = 30

        self.init_ui()
        self.create_hex_grid()

    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        self.row_label = QLabel(f"Rows: {self.rows}")
        self.col_label = QLabel(f"Cols: {self.cols}")

        self.row_slider = QSlider(Qt.Horizontal)
        self.row_slider.setMinimum(1)
        self.row_slider.setMaximum(20)
        self.row_slider.setValue(self.rows)
        self.row_slider.valueChanged.connect(self.update_rows)

        self.col_slider = QSlider(Qt.Horizontal)
        self.col_slider.setMinimum(1)
        self.col_slider.setMaximum(20)
        self.col_slider.setValue(self.cols)
        self.col_slider.valueChanged.connect(self.update_cols)

        control_layout.addWidget(self.row_label)
        control_layout.addWidget(self.row_slider)
        control_layout.addWidget(self.col_label)
        control_layout.addWidget(self.col_slider)

        layout.addLayout(control_layout)
        container.setLayout(layout)
        self.setMenuWidget(container)

        self.setWindowTitle("Hexagon Grid")
        self.setGeometry(100, 100, 800, 600)
        
    def update_rows(self, value):
        self.rows = value
        self.row_label.setText(f"Rows: {self.rows}")
        self.create_hex_grid()

    def update_cols(self, value):
        self.cols = value
        self.col_label.setText(f"Cols: {self.cols}")
        self.create_hex_grid()

    def create_hex_grid(self):
        self.scene.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                x_offset = self.size * 3/2 * col
                y_offset = self.size * math.sqrt(3) * (row + 0.5 * (col % 2))
                hex_color = QColor(100, 200, 100)
                hex_tile = HexTile(QPointF(x_offset, y_offset), self.size, hex_color)
                self.scene.addItem(hex_tile)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

