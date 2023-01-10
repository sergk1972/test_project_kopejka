import shutil
import sys
from typing import TextIO

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from mainwindow import Ui_MainWindow
from pagination import Pagination
from sqlitefunk import SqliteActions


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.f_name = None
        self.db = None
        self.setupUi(self)
        self.new_file = False
        self.wigget_ajust()
        self.sq = SqliteActions()
        self.pag = Pagination()

    def wigget_ajust(self):
        style = '''
        QTableWidget::item{background-color: white;
        border-style: outset;
        border-width 3px; border-radius: 7px; border-color: green}
        QTableWidget::item:selected {background-color: blue;
        border-width 5px; border-radius: 7px; color: white; border-color: green}
        '''
        self.setStyleSheet(style)
        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 520)
        self.tableWidget.setColumnWidth(2, 820)
        self.actionNew_File.triggered.connect(lambda: self.new_pull_action())
        self.actionOpen_File.triggered.connect(lambda: self.open_pull_action())
        self.actionSave_As.triggered.connect(lambda: self.save_as_pull_action())
        self.submitButton.clicked.connect(self.get_text)  # type: ignore
        self.submitButton.clicked.connect(self.lineEdit_1.clear)  # type: ignore
        self.submitButton.clicked.connect(self.lineEdit_2.clear)  # type: ignore
        self.submitButton.clicked.connect(lambda: self.append_file())
        self.refreshButton.clicked.connect(lambda: self.delete_one())
        self.firstpageButton.clicked.connect(lambda: self.first_page_data())
        self.prevpageButton.clicked.connect(lambda: self.prev_page_data())
        self.directpageButton.clicked.connect(lambda: self.go_to_page_data(self.comboBox.currentIndex()+1))
        self.nextpageButton.clicked.connect(lambda: self.next_page_data())
        self.lastpageButton.clicked.connect(lambda: self.last_page_data())

    def get_text(self):
        if not self.lineEdit_2.text():
            self.lineEdit_2.setText('empty_space')
        if not self.lineEdit_1.text():
            self.lineEdit_1.setText('empty_space')
        if self.new_file:
            self.txt = self.lineEdit_1.text() + " -- " + self.lineEdit_2.text() + " -- "
        else:
            self.txt = '\n' + self.lineEdit_1.text() + " -- " + self.lineEdit_2.text() + " -- "
        self.sq_txt = [self.lineEdit_1.text(), self.lineEdit_2.text()]

    def set_text_to_file(self):
        self.db = self.sq.sql_connection()
        data = self.sq.sql_fetch(self.f_name.split('/').pop().split('.').pop(0))
        self.db.close()
        text = []
        new = True
        for r1, r2 in data:
            if new:
                text.append(r1 + ' -- ' + r2 + ' -- ')
                new = False
            else:
                text.append('\n' + r1 + ' -- ' + r2 + ' -- ')
        input_file: TextIO
        with open(self.f_name, 'w', encoding='utf-8') as input_file:
            input_file.writelines(text)

    def append_file(self):
        input_file: TextIO
        with open(self.f_name, 'a+', encoding='utf-8') as input_file:
            input_file.writelines(self.txt)
        self.new_file = False
        self.db = self.sq.sql_connection()
        self.sq.sql_insert_one(self.f_name.split('/').pop().split('.').pop(0), self.sq_txt[0], self.sq_txt[1])
        self.db.close()
        self.refresh_show()

    def get_from_txt(self):
        with open(self.f_name, 'r', encoding='utf-8') as input_file:
            sentence = []
            for line in input_file:
                sentence.append(line.strip('\n'))
        res = []
        for items in sentence:
            res.append(items.strip(' -- ').split(' -- '))
        return res

    def show_from_sq(self, full_data):
        self.tableWidget.setHorizontalHeaderLabels(["ID", "There are some idiomatic expressions", "Examples"])
        x: int
        y: str
        z: str
        self.tableWidget.setRowCount(0)
        row_pos = self.tableWidget.rowCount()
        for [x, y, z] in full_data:
            x1 = str(x)
            self.tableWidget.insertRow(row_pos)
            self.tableWidget.setItem(row_pos, 0, QtWidgets.QTableWidgetItem(x1))
            self.tableWidget.setItem(row_pos, 1, QtWidgets.QTableWidgetItem(y))
            self.tableWidget.setItem(row_pos, 2, QtWidgets.QTableWidgetItem(z))

    def show_from_txt(self):
        self.tableWidget.setHorizontalHeaderLabels(["There are some idiomatic expressions", "Examples"])
        x: str
        y: str
        self.tableWidget.setRowCount(0)
        row_pos = self.tableWidget.rowCount()
        for [x, y] in self.get_from_txt():
            self.tableWidget.insertRow(row_pos)
            self.tableWidget.setItem(row_pos, 0, QtWidgets.QTableWidgetItem(x))
            self.tableWidget.setItem(row_pos, 1, QtWidgets.QTableWidgetItem(y))

    def delete_one(self):
        self.db = self.sq.sql_connection()
        self.sq.sql_delete_one(self.f_name.split('/').pop().split('.').pop(0), self.tableWidget.currentItem().text())
        self.db.close()
        self.refresh_show()
        self.set_text_to_file()

    def new_pull_action(self):
        try:
            self.f_name: str = QFileDialog.getSaveFileName(self, 'New File', './', 'Text Files (*.txt)')[0]
            self.new_file = True
            self.comboBox.clear()
            self.tableWidget.setRowCount(0)
        except Exception as ex:
            print(ex)

    def open_pull_action(self):
        # noinspection PyTypeChecker
        try:
            self.f_name: str = QFileDialog.getOpenFileName(self, 'Open File', './', 'Text Files (*.txt)')[0]
            # self.show_from_txt()
            f_name = self.f_name.split('/').pop().split('.').pop(0)
            self.db = self.sq.sql_connection()
            self.sq.sql_table_create(f_name)
            data = self.get_from_txt()
            self.pag = Pagination(data)
            self.statusBar().showMessage(f'{self.f_name} | Total pages: {self.pag.total_pages} | Total rows: {len(self.pag.items)}')
            self.comboBox.clear()
            for page in range(1, (self.pag.total_pages + 1)):
                self.comboBox.addItem(f"{page}")
            self.sq.sql_insert(f_name, data)
            start = (self.pag.current_page - 1) * self.pag.page_size
            end = start + self.pag.page_size
            self.sq.get_visible_page(f_name, start, end)
            self.show_from_sq(self.sq.data)
            self.db.close()
        except Exception as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Ошибка открытия файла!')
            error.setText(f'Файл не выбран или не существует!\n{ex}')
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def save_as_pull_action(self):
        file_name = self.f_name
        try:
            self.f_name: str = QFileDialog.getSaveFileName(self, "Save File As", "./", "Text Files (*.txt)")[0]
            shutil.copy(f'{file_name}', f'{self.f_name}')
            self.refresh_show()
        except Exception as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Ошибка открытия файла!')
            error.setText(f'Файл не выбран или не существует!\n{ex}')
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def first_page_data(self):
        self.pag.first_page()
        f_name = self.f_name.split('/').pop().split('.').pop(0)
        self.db = self.sq.sql_connection()
        start = (self.pag.current_page - 1) * self.pag.page_size
        end = start + self.pag.page_size
        visible_data = self.sq.get_visible_page(f_name, start, end)
        self.show_from_sq(visible_data)
        self.db.close()

    def prev_page_data(self):
        self.pag.prev_page()
        f_name = self.f_name.split('/').pop().split('.').pop(0)
        self.db = self.sq.sql_connection()
        start = (self.pag.current_page - 1) * self.pag.page_size
        end = start + self.pag.page_size
        visible_data = self.sq.get_visible_page(f_name, start, end)
        self.show_from_sq(visible_data)
        self.db.close()

    def go_to_page_data(self, page):
        self.pag.go_to_page(page)
        f_name = self.f_name.split('/').pop().split('.').pop(0)
        self.db = self.sq.sql_connection()
        start = (self.pag.current_page - 1) * self.pag.page_size
        end = start + self.pag.page_size
        visible_data = self.sq.get_visible_page(f_name, start, end)
        self.show_from_sq(visible_data)
        self.db.close()

    def next_page_data(self):
        self.pag.next_page()
        f_name = self.f_name.split('/').pop().split('.').pop(0)
        self.db = self.sq.sql_connection()
        start = (self.pag.current_page - 1) * self.pag.page_size
        end = start + self.pag.page_size
        visible_data = self.sq.get_visible_page(f_name, start, end)
        self.show_from_sq(visible_data)
        self.db.close()

    def last_page_data(self):
        self.pag.last_page()
        f_name = self.f_name.split('/').pop().split('.').pop(0)
        self.db = self.sq.sql_connection()
        start = (self.pag.current_page - 1) * self.pag.page_size
        end = start + self.pag.page_size
        visible_data = self.sq.get_visible_page(f_name, start, end)
        self.show_from_sq(visible_data)
        self.db.close()

    def refresh_show(self):
        try:
            data = self.get_from_txt()
            self.pag = Pagination(data)
            self.statusBar().showMessage(
                f'{self.f_name} | Total pages: {self.pag.total_pages} | Total rows: {len(self.pag.items)}')
            self.comboBox.clear()
            for page in range(1, (self.pag.total_pages + 1)):
                self.comboBox.addItem(f"{page}")
            self.last_page_data()
        except Exception as ex:
            print(ex)


def main_application():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    try:
        main_application()
    except Exception as err:
        print(err)
