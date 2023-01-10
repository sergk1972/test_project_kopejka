import sqlite3
from sqlite3 import Error
from PyQt5.QtWidgets import QMessageBox


class SqliteActions:

    def __init__(self):
        self.data = None
        self.db = None

    def sql_connection(self):  # db_file  creating and establishing connection
        try:
            self.db = sqlite3.connect('database.db')
            return self.db
        except Error as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Database Error!')
            error.setText(f"ФCan't establish connection!\n{ex}")
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def sql_table_create(self, f_name):  # database table creating
        try:
            cursor_sql = self.db.cursor()
            cursor_sql.execute(f"DROP table if exists {f_name}")
            self.db.commit()
            cursor_sql.execute(f"CREATE TABLE IF NOT EXISTS {f_name} (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                               f"sentence TEXT DEFAULT 'empty_space', sample TEXT DEFAULT 'empty_space') ")
            self.db.commit()
        except Error as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Database Error!')
            error.setText(f"Database already exist!\n{ex}")
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def sql_insert(self, f_name, entities):  # some data adding
        try:
            # items = tuple(enumerate(entities, start=1))
            cursor_sql = self.db.cursor()
            # i: int = 1
            for s1, s2 in entities:
                cursor_sql.execute(f"INSERT INTO {f_name}(sentence, sample) VALUES(?, ?)", (s1, s2))
                # i += 1
                self.db.commit()
        except Error as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Database Error!')
            error.setText(f"Can't insert data!\n{ex}")
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def sql_insert_one(self, f_name, text1, text2):
        try:
            cursor_sql = self.db.cursor()
            cursor_sql.execute(f'INSERT INTO {f_name}(sentence, sample) VALUES(?, ?)', (text1, text2))
            self.db.commit()
        except Error as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Database Error!')
            error.setText(f"Can't insert data!\n{ex}")
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def sql_delete_one(self, f_name, i_d):
        try:
            cursor_sql = self.db.cursor()
            cursor_sql.execute(f'DELETE FROM {f_name} WHERE id = {i_d}')
            self.db.commit()
        except Error as ex:
            error: QMessageBox | QMessageBox = QMessageBox()
            error.setIcon(QMessageBox.Information)  # (QMessageBox_Icon='Warning')
            error.setWindowTitle('Database Error!')
            error.setText(f"Не могу удалить!\n{ex}")
            error.setStandardButtons(QMessageBox.Ok)
            error.exec_()

    def sql_fetch(self, f_name):  # show data
        try:
            cursor_sql = self.db.cursor()
            cursor_sql.execute(f'SELECT sentence, sample FROM {f_name}')
            data = cursor_sql.fetchall()
            return data
        except Error as ex:
            print(ex)

    def get_visible_page(self, f_name, start, end):
        cursor_sql = self.db.cursor()
        try:
            cursor_sql.execute(f'SELECT id, sentence, sample FROM {f_name} WHERE id > {start} AND id <= {end}'
                               f' ORDER BY id DESC')
            self.db.commit()
            self.data: list = cursor_sql.fetchall()
        except Error as ex:
            print(ex)
        return self.data


# if __name__ == "__main__":
#     q = SqliteActions()
#     q.sql_connection()
#     q.sql_table_create('eng_idioms')
#     d = q.sql_fetch('eng_idioms')
#     print(d)
