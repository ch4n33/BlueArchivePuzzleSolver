from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsPolygonItem, QWidget, \
    QVBoxLayout, QHBoxLayout, QSlider, \
    QLabel, QComboBox
from PyQt5.QtGui import QPolygonF, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
import sys
import math

from enum import Enum


def create_hexagon(center, size):
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        x = center.x() + size * math.cos(angle)
        y = center.y() + size * math.sin(angle)
        points.append(QPointF(x, y))
    return QPolygonF(points)


class TileState(Enum):
    # 타일 종류 : 빈 칸, 타일, 스위치 타일, 빈 타일, 토글 타일, 크랙 타일, 양방향 이동 타일, 단방향 이동 타일, 단방향 도착 타일
    EMPTY       = 0
    TILE        = 1
    SWITCH      = 2
    EMPTY_TILE  = 3
    TOGGLE      = 4
    CRACK       = 5
    BI_DIR      = 6
    UNI_DIR     = 7
    UNI_DIR_END = 8
    START       = 9


class Tile():
    def __init__(self, tileState):
        self.tileState = tileState
        self.enemy = None
    
    def setEnemy(self, enemy):
        self.enemy = enemy
    
    def setTileState(self, state):
        self.tileState = state


tileColor = (
    QColor(255, 255, 255),  # EMPTY
    QColor(220, 220, 255),  # TILE
    QColor(255, 200, 255),  # SWITCH
    QColor(190, 190, 220),  # EMPTY_TILE
    QColor(255, 255, 220),  # TOGGLE
    QColor(220, 220, 140),  # CRACK
    QColor(200, 200, 255),  # BI_DIR
    QColor(220, 200, 255),  # UNI_DIR
    QColor(220, 100, 255),  # UNI_DIR_END
    QColor(255, 255, 180)   # START
)
editState = TileState.EMPTY
editEnemy = None
stateMatrix = [[Tile(TileState.EMPTY) for _ in range(32)] for _ in range(32)]


class HexTile(QGraphicsPolygonItem):
    def __init__(self, center, size, x,y):
        super().__init__(create_hexagon(center, size))
        self.setBrush(QBrush(tileColor[stateMatrix[x][y].tileState.value]))
        self.x, self.y = x,y
        self.setPen(QColor(0, 0, 0))     

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print (f'editState: {editState.name}')
            self.setTileState(editState)  # 타일 상태를 타일로 변경
        elif event.button() == Qt.RightButton:
            self.setEnemy(editEnemy)  # 적을 배치

    def setTileState(self, state):
        stateMatrix[self.x][self.y].setTileState(state)
        self.setBrush(QBrush(tileColor[state.value]))
    
    def setEnemy(self, enemy):
        stateMatrix[self.x][self.y].setEnemy(enemy)
        # draw enemy here
    

class Enemy():
    def __init__(self, defense, move, difficulty):
        '''
        defense : 'light' | 'heavy' | 'special' | 'structure' | 'present'
        move : 'stationary' | 'near' | 'pursue'
        difficulty : 0 | 1 | 2 | 3 | 'boss'
        '''
        if defense not in ['light', 'heavy', 'special', 'structure', 'present']:
            raise ValueError(f"defense must be one of 'light', 'heavy', 'special', 'structure', 'present'")
        if defense is 'present' and move is not 'stationary' and difficulty is not 0:
            raise ValueError(f"present enemy must be stationary and its difficulty must be 0")
        if move not in ['stationary', 'near', 'pursue']:
            raise ValueError(f"move must be one of 'stationary', 'near', 'pursue'")
        if difficulty not in [0,1,2,3,'boss']:
            raise ValueError(f"difficulty must be one of 0,1,2,3,'boss'")
        
        self.defense = defense
        self.move = move
        self.difficulty = difficulty


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
        
        self.edit_selector = QComboBox()
        self.edit_selector.addItem("Empty")
        self.edit_selector.addItem("Tile")
        self.edit_selector.addItem("Switch")
        self.edit_selector.addItem("Empty Tile")
        self.edit_selector.addItem("Toggle")
        self.edit_selector.addItem("Crack")
        self.edit_selector.addItem("Bi-Dir")
        self.edit_selector.addItem("Uni-Dir")
        self.edit_selector.addItem("Uni-Dir End")
        self.edit_selector.currentIndexChanged.connect(self.edit_state_changed)
        
        self.edit_defense_selector = QComboBox()
        self.edit_defense_selector.addItem("Light")
        self.edit_defense_selector.addItem("Heavy")
        self.edit_defense_selector.addItem("Special")
        self.edit_defense_selector.addItem("Structure")
        self.edit_defense_selector.addItem("Present")
        self.edit_defense_selector.currentIndexChanged.connect(self.edit_defense_changed)
        
        self.edit_move_selector = QComboBox()
        self.edit_move_selector.addItem("Stationary")
        self.edit_move_selector.addItem("Near")
        self.edit_move_selector.addItem("Pursue")
        self.edit_move_selector.currentIndexChanged.connect(self.edit_move_changed) 
        
        self.edit_difficulty_selector = QComboBox()
        self.edit_difficulty_selector.addItem("0")
        self.edit_difficulty_selector.addItem("1")
        self.edit_difficulty_selector.addItem("2")
        self.edit_difficulty_selector.addItem("3")
        self.edit_difficulty_selector.addItem("Boss")
        self.edit_difficulty_selector.currentIndexChanged.connect(self.edit_difficulty_changed)       

        control_layout.addWidget(self.row_label)
        control_layout.addWidget(self.row_slider)
        control_layout.addWidget(self.col_label)
        control_layout.addWidget(self.col_slider)
        control_layout.addWidget(self.edit_defense_selector)
        control_layout.addWidget(self.edit_move_selector)
        control_layout.addWidget(self.edit_difficulty_selector)
        control_layout.addWidget(self.edit_selector)

        layout.addLayout(control_layout)
        container.setLayout(layout)
        self.setMenuWidget(container)

        self.setWindowTitle("Title here")
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
                hex_tile = HexTile(QPointF(x_offset, y_offset), self.size, row, col)
                self.scene.addItem(hex_tile)
    
    def edit_state_changed(self, index):
        global editState
        editState = TileState(index)
        print(editState)
        
    def edit_defense_changed(self, index):
        pass
    
    def edit_move_changed(self, index):
        pass
    
    def edit_difficulty_changed(self, index):
        pass
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

