import datetime
import sqlite3
from PyQt5 import QtWidgets, QtCore
from db import path


class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Регистрация")

        self.connection = sqlite3.connect(path())
        self.cursor = self.connection.cursor()

        self.label_username = QtWidgets.QLabel("Имя пользователя:")
        self.lineEdit_username = QtWidgets.QLineEdit()

        self.label_password = QtWidgets.QLabel("Пароль:")
        self.lineEdit_password = QtWidgets.QLineEdit()
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.button_register = QtWidgets.QPushButton("Зарегистрироваться")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label_username)
        self.layout.addWidget(self.lineEdit_username)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.lineEdit_password)
        self.layout.addWidget(self.button_register)
        self.setLayout(self.layout)

        self.button_register.clicked.connect(self.register)

    def register(self) -> None:
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        if username and password:
            self.cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            existing_user = self.cursor.fetchone()
            if existing_user:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")
            else:
                self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                self.connection.commit()
                QtWidgets.QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
                self.accept()
                try:
                    self.cursor.execute(f'''CREATE TABLE {username}_table
                                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      calendar_date DATE NOT NULL,
                                      name TEXT NOT NULL,
                                      dateline TIME NOT NULL,
                                      deadline TIME NOT NULL,
                                      priority INTEGER NOT NULL,
                                      time DATE NOT NULL)''')
                    self.cursor.execute(f'''CREATE TABLE {username}_list
                                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      name TEXT NOT NULL,
                                      description TEXT NOT NULL,
                                      priority INTEGER NOT NULL,
                                      marketed TEXT NOT NULL,
                                      importance TEXT NOT NULL)''')
                    self.connection.commit()
                except sqlite3.OperationalError:
                    pass
                self.connection.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Аутентификация")

        self.connection = sqlite3.connect(path())
        self.cursor = self.connection.cursor()

        self.label_username = QtWidgets.QLabel("Имя пользователя:")
        self.lineEdit_username = QtWidgets.QLineEdit()

        self.label_password = QtWidgets.QLabel("Пароль:")
        self.lineEdit_password = QtWidgets.QLineEdit()
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.button_login = QtWidgets.QPushButton("Войти")
        self.button_register = QtWidgets.QPushButton("Регистрация")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label_username)
        self.layout.addWidget(self.lineEdit_username)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.lineEdit_password)
        self.layout.addWidget(self.button_login)
        self.layout.addWidget(self.button_register)
        self.setLayout(self.layout)

        self.button_login.clicked.connect(self.login)
        self.button_register.clicked.connect(self.show_register_dialog)

    def show_register_dialog(self) -> None:
        dialog = RegisterDialog(self)
        dialog.exec()

    def login(self) -> None:
        self.username = self.lineEdit_username.text()
        self.password = self.lineEdit_password.text()
        if self.username and self.password:
            self.cursor.execute("SELECT username, password FROM users WHERE username=?", (self.username,))
            user = self.cursor.fetchone()
            if user and user[1] == self.password:
                self.accept()
                return
        QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")


class TaskDialog(QtWidgets.QDialog):
    def __init__(self, calendar_date: QtCore.QDate, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self.calendar_date = calendar_date
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Добавление/изменение задачи")

        self.name_label = QtWidgets.QLabel("Название:")
        self.name_field = QtWidgets.QPlainTextEdit()

        self.date_label = QtWidgets.QLabel("Начало:")
        self.date_field = QtWidgets.QTimeEdit(QtCore.QTime.currentTime())

        self.deadline_label = QtWidgets.QLabel("Окончание:")
        self.deadline_field = QtWidgets.QTimeEdit(QtCore.QTime.currentTime())

        self.priority_label = QtWidgets.QLabel("Повторяется:")
        self.priority_field = QtWidgets.QComboBox()
        self.priority_field.addItems(['Никогда', 'Каждый день', 'Каждую неделю', 'Каждый месяц', 'Каждый год'])

        self.time_label = QtWidgets.QLabel("Повторять до:")
        self.time_field = QtWidgets.QDateEdit(QtCore.QDate(self.calendar_date.toPyDate() + datetime.timedelta(1)))
        self.time_field.setCalendarPopup(True)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.name_label, self.name_field)
        layout.addRow(self.date_label, self.date_field)
        layout.addRow(self.deadline_label, self.deadline_field)
        layout.addRow(self.priority_label, self.priority_field)
        layout.addRow(self.time_label, self.time_field)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def accept(self) -> None:
        if self.time_field.date() <= self.calendar_date:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Дата до которой надо повторять событие должна "
                                                          "быть больше выбранной на календаре.")
            return
        super().accept()


class ProblemDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Добавление/изменение задачи")

        self.name_label = QtWidgets.QLabel("Название:")
        self.name_field = QtWidgets.QLineEdit()

        self.description_label = QtWidgets.QLabel("Описание:")
        self.description_field = QtWidgets.QPlainTextEdit()

        self.priority_label = QtWidgets.QLabel("Приоритет:")
        self.priority_field = QtWidgets.QSpinBox()

        self.marketed_label = QtWidgets.QLabel("Помеченная:")
        self.marketed_field = QtWidgets.QComboBox()
        self.marketed_field.addItems(['Да', 'Нет'])
        if self.parent.__class__.__name__ == 'MarkedTasks':
            self.marketed_field.setEnabled(False)

        self.importance_label = QtWidgets.QLabel("Важная:")
        self.importance_field = QtWidgets.QComboBox()
        self.importance_field.addItems(['Да', 'Нет'])
        if self.parent.__class__.__name__ == 'ImportantTasks':
            self.importance_field.setEnabled(False)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.name_label, self.name_field)
        layout.addRow(self.description_label, self.description_field)
        layout.addRow(self.priority_label, self.priority_field)
        layout.addRow(self.marketed_label, self.marketed_field)
        layout.addRow(self.importance_label, self.importance_field)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
