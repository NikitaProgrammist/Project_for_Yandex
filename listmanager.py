import sqlite3
from PyQt5 import QtCore, QtWidgets, QtSql
from dialogs import ProblemDialog
from styles_and_delegations import QComboBox


class ListManager(QtWidgets.QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user + '_list'
        self.connection = sqlite3.connect('task_manager.db')
        self.cursor = self.connection.cursor()
        self.initUI()
        self.filter_func()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.task_table = QtWidgets.QTableView(self)
        self.task_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        low_layout = QtWidgets.QHBoxLayout()
        self.add_task_button = QtWidgets.QPushButton("Добавить задачу")
        self.edit_task_button = QtWidgets.QPushButton("Редактировать задачу")
        self.delete_task_button = QtWidgets.QPushButton("Удалить задачу")
        self.show_all_button = QtWidgets.QPushButton("Все задачи")
        low_layout.addWidget(self.add_task_button)
        low_layout.addWidget(self.edit_task_button)
        low_layout.addWidget(self.delete_task_button)
        low_layout.addWidget(self.show_all_button)
        high_layout = QtWidgets.QHBoxLayout()
        self.choose_priority = QComboBox(self)
        self.choose_priority.addItem("Все")
        self.priority_items = sorted(set([str(_[0]) for _ in self.cursor.execute(f"""SELECT priority 
        FROM {self.user}""").fetchall()]), key=int)
        self.choose_priority.addItems(self.priority_items)
        self.choose_priority.model().itemChanged.connect(self.f)
        self.filter = QtWidgets.QLineEdit(self)
        self.filter_button = QtWidgets.QPushButton("Искать")
        high_layout.addWidget(self.choose_priority)
        high_layout.addWidget(self.filter)
        high_layout.addWidget(self.filter_button)
        main_layout.addLayout(high_layout)
        main_layout.addWidget(self.task_table)
        main_layout.addLayout(low_layout)
        self.query = QtSql.QSqlQuery()
        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable(self.user)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'ИД')
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, 'Название')
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, 'О задаче')
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, 'Приоритет')
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, 'Помеченная')
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, 'Важная')
        self.model.select()
        self.task_table.setModel(self.model)
        self.task_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.task_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()
        self.task_table.hideColumn(0)
        self.task_table.hideColumn(4)
        self.task_table.hideColumn(5)
        self.filter_button.clicked.connect(self.filter_func)
        self.add_task_button.clicked.connect(self.add_task)
        self.edit_task_button.clicked.connect(self.edit_task)
        self.delete_task_button.clicked.connect(self.delete_task)
        self.show_all_button.clicked.connect(self.show_all_tasks)
        self.task_table.clicked.connect(self.cell_changed)
        self.row = -1

    def f(self, item):
        if item == self.choose_priority.model().item(0, 0) and not item.checkState():
            for i in range(1, self.choose_priority.count()):
                self.choose_priority.model().item(i, 0).setCheckState(QtCore.Qt.Unchecked)
            return
        if item == self.choose_priority.model().item(0, 0) and item.checkState():
            for i in range(1, self.choose_priority.count()):
                self.choose_priority.model().item(i, 0).setCheckState(QtCore.Qt.Checked)
            return

    def cell_changed(self, index):
        if index.row() != self.row:
            self.task_table.selectionModel().clearSelection()
            self.task_table.selectRow(index.row())
            self.row = index.row()
        else:
            self.row = -1
            self.task_table.selectionModel().clearSelection()

    def filter_func(self):
        self.model.select()
        priority = []
        for i in range(self.choose_priority.count()):
            item = self.choose_priority.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                priority.append(item.text())
        name = self.filter.text()
        if "Все" not in priority:
            self.query.exec(f"""SELECT * FROM {self.user} WHERE priority in ({', '.join(priority)}) and name like 
            '%{name}%' ORDER BY priority DESC, name ASC""")
        else:
            self.query.exec(f"""SELECT * FROM {self.user} WHERE name like '%{name}%' 
            ORDER BY priority DESC, name ASC""")
        self.model.setQuery(self.query)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()
        self.task_table.hideColumn(0)
        self.task_table.hideColumn(4)
        self.task_table.hideColumn(5)

    def show_all_tasks(self):
        self.model.select()
        self.query.exec(f"""SELECT * FROM {self.user}
        ORDER BY priority DESC, name ASC""")
        self.model.setQuery(self.query)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()

    def add_task(self):
        dialog = ProblemDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = dialog.name_field.text()
            description = dialog.description_field.toPlainText()
            priority = dialog.priority_field.value()
            if str(priority) not in self.priority_items:
                self.choose_priority.addItem(str(priority))
                self.priority_items.append(str(priority))
            marketed = dialog.marketed_field.currentText()
            importance = dialog.importance_field.currentText()
            record = self.model.record()
            record.setValue("name", name)
            record.setValue("description", description)
            record.setValue("priority", priority)
            record.setValue("marketed", marketed)
            record.setValue("importance", importance)
            self.model.insertRecord(-1, record)
        self.filter_func()

    def edit_task(self):
        selected_row = self.task_table.selectionModel().currentIndex().row()
        if selected_row >= 0:
            dialog = ProblemDialog(self)
            record = self.model.record(selected_row)
            id = record.value("id")
            name = record.value("name")
            description = record.value("description")
            priority = record.value("priority")
            marketed = record.value("marketed")
            importance = record.value("importance")
            dialog.name_field.setText(name)
            dialog.description_field.setPlainText(description)
            dialog.priority_field.setValue(priority)
            dialog.marketed_field.setCurrentText(marketed)
            dialog.importance_field.setCurrentText(importance)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                name = dialog.name_field.text()
                description = dialog.description_field.toPlainText()
                priority = dialog.priority_field.value()
                marketed = dialog.marketed_field.currentText()
                importance = dialog.importance_field.currentText()
                self.query.exec(f"""REPLACE INTO {self.user} (id, name, description, priority, marketed, importance) 
                VALUES ({id}, '{name}', '{description}', {priority}, '{marketed}', '{importance}')""")
                self.model.setQuery(self.query)
        self.filter_func()

    def delete_task(self):
        selected_row = self.task_table.selectionModel().currentIndex().row()
        if selected_row >= 0:
            self.model.removeRow(selected_row)
        self.filter_func()


class MarkedTasks(ListManager):
    def filter_func(self):
        self.model.select()
        priority = []
        for i in range(self.choose_priority.count()):
            item = self.choose_priority.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                priority.append(item.text())
        name = self.filter.text()
        if "Все" not in priority:
            self.query.exec(f"""SELECT * FROM {self.user} WHERE marketed = 'Да' and 
            priority in ({', '.join(priority)}) and name like '%{name}%'
            ORDER BY priority DESC, name ASC""")
        else:
            self.query.exec(f"""SELECT * FROM {self.user} WHERE marketed = 'Да' and name like '%{name}%'
            ORDER BY priority DESC, name ASC""")
        self.model.setQuery(self.query)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()
        self.task_table.hideColumn(0)
        self.task_table.hideColumn(4)
        self.task_table.hideColumn(5)

    def show_all_tasks(self):
        self.model.select()
        self.query.exec(f"""SELECT * FROM {self.user} WHERE marketed = 'Да'
        ORDER BY priority DESC, name ASC""")
        self.model.setQuery(self.query)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()


class ImportantTasks(ListManager):
    def filter_func(self):
        self.model.select()
        priority = []
        for i in range(self.choose_priority.count()):
            item = self.choose_priority.model().item(i)
            if item.checkState() == QtCore.Qt.Checked:
                priority.append(item.text())
        name = self.filter.text()
        if "Все" not in priority:
            self.query.exec(f"""SELECT * FROM {self.user} WHERE importance = 'Да' and 
            priority in ({', '.join(priority)}) and name like '%{name}%'
            ORDER BY priority DESC, name ASC""")
        else:
            self.query.exec(f"""SELECT * FROM {self.user} WHERE importance = 'Да' and name like '%{name}%'
            ORDER BY priority DESC, name ASC""")
        self.model.setQuery(self.query)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()
        self.task_table.hideColumn(0)
        self.task_table.hideColumn(4)
        self.task_table.hideColumn(5)

    def show_all_tasks(self):
        self.model.select()
        self.query.exec(f"""SELECT * FROM {self.user} WHERE importance = 'Да'
        ORDER BY priority DESC, name ASC""")
        self.model.setQuery(self.query)
        self.task_table.resizeColumnsToContents()
        self.task_table.resizeRowsToContents()
