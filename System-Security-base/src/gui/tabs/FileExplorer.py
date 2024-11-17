from PyQt5.QtWidgets import (
    QMenu, 
    QAction, 
    QWidget, 
    QLineEdit,
    QTreeView, 
    QTabWidget, 
    QVBoxLayout, 
    QMessageBox, 
    QActionGroup,
    QFileSystemModel, 
)
from PyQt5.QtCore import QSortFilterProxyModel, QDir, Qt

import os
import sys

class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

class Tab_FileExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout(self)

        self.address_bar = QLineEdit(self)
        self.address_bar.setPlaceholderText("주소 입력")
        self.address_bar.returnPressed.connect(self.navigate_to_address)

        layout.addWidget(self.address_bar)

        self.file_view = QTreeView(self)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        self.proxy_model = SortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.file_view.setSortingEnabled(True)
        self.file_view.setModel(self.proxy_model)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.setRootIndex(self.proxy_model.mapFromSource(self.model.index(QDir.rootPath())))

        self.file_view.doubleClicked.connect(self.open_file_or_folder)

        self.file_view.header().setSectionsClickable(True)
        self.file_view.header().sectionClicked.connect(self.header_clicked)
        self.file_view.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.header().customContextMenuRequested.connect(self.show_header_context_menu)

        self.file_view.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.file_view)

        self.file_view.setColumnWidth(0, 300)  # 이름 (Name)
        self.file_view.setColumnWidth(1, 100)  # 크기 (Size)
        self.file_view.setColumnWidth(2, 100)  # 유형 (Type)
        self.file_view.setColumnWidth(3, 150)  # 수정한 날짜 (Date Modified)

        self.model.setReadOnly(False)
        self.model.setFilter(QDir.AllEntries | QDir.Hidden | QDir.System)

        self.history = []
        self.current_index = -1

        self.current_sort_column = 0
        self.current_sort_order = Qt.AscendingOrder

        self.visible_columns = [0, 1, 2, 3]  # 기본적으로 보이는 컬럼

        # DLL 로드
        '''
        self.file_operations_dll = ctypes.CDLL("../../build/file_operations.dll")
        self.compress_dll = ctypes.CDLL("../../build/compress.dll")
        self.virus_scan_dll = ctypes.CDLL("../../build/virus_scan.dll")
        self.header_check_dll = ctypes.CDLL("../../build/header_check.dll")
        self.lock_dll = ctypes.CDLL("../../build/lock.dll")
        self.hide_dll = ctypes.CDLL("../../build/hide.dll")
        self.properties_dll = ctypes.CDLL("../../build/properties.dll")
        '''

    def navigate_to(self, path):
        source_index = self.model.index(path)
        proxy_index = self.proxy_model.mapFromSource(source_index)
        self.file_view.setRootIndex(proxy_index)
        self.address_bar.setText(path)
        self.add_to_history(path)
        self.update_tab_name(path)

    def navigate_to_address(self):
        path = self.address_bar.text()
        if os.path.exists(path):
            self.navigate_to(path)
        else:
            QMessageBox.warning(self, "주소를 찾을 수 없습니다.", "입력하신 주소를 다시 확인해주세요.")

    def open_file_or_folder(self, index):
        source_index = self.proxy_model.mapToSource(index)
        path = self.model.filePath(source_index)
        if os.path.isdir(path):
            self.navigate_to(path)
        else:
            self.file_operations_dll.open_file(path.encode('utf-8'))

    def add_to_history(self, path):
        if self.current_index == -1 or path != self.history[self.current_index]:
            self.current_index += 1
            self.history = self.history[:self.current_index]
            self.history.append(path)

    def header_clicked(self, logical_index):
        if self.current_sort_column == logical_index:
            if self.current_sort_order == Qt.AscendingOrder:
                self.current_sort_order = Qt.DescendingOrder
            else:
                self.current_sort_order = Qt.AscendingOrder
        else:
            self.current_sort_column = logical_index
            self.current_sort_order = Qt.AscendingOrder

        self.file_view.sortByColumn(self.current_sort_column, self.current_sort_order)

    def show_header_context_menu(self, pos):
        menu = QMenu(self)
        header = self.file_view.header()

        column_group = QActionGroup(self)
        column_group.setExclusive(False)

        columns = [
            ("이름", 0),
            ("크기", 1),
            ("유형", 2),
            ("수정한 날짜", 3),
        ]

        for text, column in columns:
            action = QAction(text, self)
            action.setCheckable(True)
            action.setChecked(column in self.visible_columns)
            action.setData(column)

            if column == 0:  # '이름' 컬럼은 항상 체크되어 있고 비활성화
                action.setEnabled(False)
            else:
                action.triggered.connect(self.toggle_column)
            column_group.addAction(action)
            menu.addAction(action)

        menu.exec_(self.file_view.header().mapToGlobal(pos))

    def toggle_column(self):
        action = self.sender()
        if action:
            column = action.data()
            if action.isChecked():
                if column not in self.visible_columns:
                    self.visible_columns.append(column)
                    self.file_view.setColumnHidden(column, False)
            else:
                if column in self.visible_columns:
                    self.visible_columns.remove(column)
                    self.file_view.setColumnHidden(column, True)

    def update_tab_name(self, path):
        tab_widget = self.parent().parent()
        if isinstance(tab_widget, QTabWidget):
            index = tab_widget.indexOf(self)
            tab_widget.setTabText(index, os.path.basename(path) or "루트")

    def show_context_menu(self, pos):
        index = self.file_view.indexAt(pos)
        menu = QMenu(self)

        new_folder_action = menu.addAction("새 폴더 만들기")
        new_file_action = menu.addAction("새 파일 만들기")
        menu.addSeparator()

        if index.isValid():
            source_index = self.proxy_model.mapToSource(index)
            file_path = self.model.filePath(source_index)

            delete_action = menu.addAction("삭제")
            rename_action = menu.addAction("이름변경")
            open_action = menu.addAction("열기")
            menu.addSeparator()
            
            compress_action = menu.addAction("압축")
            virus_scan_action = menu.addAction("바이러스 검사")
            header_check_action = menu.addAction("헤더검사")
            lock_action = menu.addAction("잠금")
            hide_action = menu.addAction("숨기기")
            properties_action = menu.addAction("속성")

        action = menu.exec_(self.file_view.viewport().mapToGlobal(pos))

        if action == new_folder_action:
            self.create_new_folder(self.model.filePath(self.file_view.rootIndex()))
        elif action == new_file_action:
            self.create_new_file(self.model.filePath(self.file_view.rootIndex()))
        elif index.isValid():
            if action == delete_action:
                self.file_operations_dll.delete_file(file_path.encode('utf-8'))
            elif action == rename_action:
                self.file_operations_dll.rename_file(file_path.encode('utf-8'))
            elif action == open_action:
                self.file_operations_dll.open_file(file_path.encode('utf-8'))
            elif action == compress_action:
                self.compress_dll.compress_file(file_path.encode('utf-8'))
            elif action == virus_scan_action:
                self.virus_scan_dll.scan_file(file_path.encode('utf-8'))
            elif action == header_check_action:
                self.header_check_dll.check_header(file_path.encode('utf-8'))
            elif action == lock_action:
                self.lock_dll.lock_file(file_path.encode('utf-8'))
            elif action == hide_action:
                self.hide_dll.hide_file(file_path.encode('utf-8'))
            elif action == properties_action:
                self.properties_dll.show_properties(file_path.encode('utf-8'))

    def create_new_folder(self, parent_path):
        self.file_operations_dll.create_new_folder(parent_path.encode('utf-8'))

    def create_new_file(self, parent_path):
        self.file_operations_dll.create_new_file(parent_path.encode('utf-8'))