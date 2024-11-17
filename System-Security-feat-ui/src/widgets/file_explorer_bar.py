from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame 
from widgets.file_area import FileArea  
from widgets.sidebar import Sidebar  

class FileExplorerBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)

        self.sidebar = Sidebar(self)
        self.layout.addWidget(self.sidebar)

        self.add_horizontal_separator()

        self.file_area = FileArea(self)
        self.layout.addWidget(self.file_area)

        self.setLayout(self.layout)

    def add_horizontal_separator(self):
        line_separator = QFrame(self)
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        line_separator.setStyleSheet("color: black;")
        self.layout.addWidget(line_separator)
