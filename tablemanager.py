import sqlite3
import calendar
import datetime
from PyQt5 import QtCore, QtWidgets, QtSql
from db import path
from dialogs import TaskDialog
from styles_and_delegations import QCalendarWidget, TableViewDelegate


class TableManager(QtWidgets.QWidget):
    def __init__(self, user: str) -> None:
        super().__init__()
        self.user = user + '_table'

        self.connection = sqlite3.connect(path())
        self.cursor = self.connection.cursor()

        self.initUI()
        self.select_row_table = (-1, self.tableviews[0])

    def initUI(self) -> None:
        main_layout = QtWidgets.QHBoxLayout(self)

        left_sidebar_layout = QtWidgets.QVBoxLayout()

        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.clicked.connect(self.calendar_day)

        left_sidebar_layout.addWidget(QtWidgets.QLabel("Календарь"))
        left_sidebar_layout.addWidget(self.calendar_widget)
        main_layout.addLayout(left_sidebar_layout)

        right_sidebar_layout = QtWidgets.QVBoxLayout()

        self.task_tableview = QtWidgets.QTableView(self)
        self.task_tableview.clicked.connect(self.cell_changed)

        self.add_task_button = QtWidgets.QPushButton("Добавить задачу")
        self.add_task_button.clicked.connect(self.add_task)

        self.edit_task_button = QtWidgets.QPushButton("Редактировать задачу")
        self.edit_task_button.clicked.connect(self.edit_task)

        self.delete_task_button = QtWidgets.QPushButton("Удалить задачу")
        self.delete_task_button.clicked.connect(self.delete_task)

        self.show_all_button = QtWidgets.QPushButton("Все задачи")
        self.show_all_button.clicked.connect(self.show_all_tasks)

        right_sidebar_layout.addWidget(QtWidgets.QLabel("Расписание"))
        right_sidebar_layout.addWidget(self.task_tableview)
        right_sidebar_layout.addWidget(self.add_task_button)
        right_sidebar_layout.addWidget(self.edit_task_button)
        right_sidebar_layout.addWidget(self.delete_task_button)
        right_sidebar_layout.addWidget(self.show_all_button)
        main_layout.addLayout(right_sidebar_layout)

        self.query = QtSql.QSqlQuery()
        self.model = QtSql.QSqlTableModel(self)
        self.model.setTable(self.user)
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'ИД')
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, 'День')
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, 'О задаче')
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, 'Начало')
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, 'Конец')
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, 'Дублирование')
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, 'До какого дня')
        self.model.select()
        self.models = [self.model]

        self.task_tableview.setModel(self.model)
        self.task_tableview.hideColumn(0)
        self.task_tableview.hideColumn(5)
        self.task_tableview.hideColumn(6)
        self.task_tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.task_tableview.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.task_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.task_tableview.resizeColumnsToContents()
        self.task_tableview.resizeRowsToContents()
        self.tableviews = [self.task_tableview]
        self.show_all_tasks()

    def cell_changed(self, index: QtWidgets.QTableWidgetItem) -> None:
        if (index.row(), self.sender()) != self.select_row_table:
            for tableview in self.tableviews:
                tableview.selectionModel().clearSelection()
            self.sender().selectRow(index.row())
            self.select_row_table = (index.row(), self.sender())
        else:
            self.select_row_table = (-1, self.tableviews[0])
            for tableview in self.tableviews:
                tableview.selectionModel().clearSelection()

    def calendar_day(self) -> None:
        self.show_day_tasks(self.calendar_widget.selectedDate(), self.task_tableview)

    def show_day_tasks(self, calendar_date: QtCore.QDate, tableview: QtWidgets.QTableView) -> None:
        self.models[self.tableviews.index(tableview)].select()
        query = f"""SELECT * FROM {self.user} WHERE 
                calendar_date = '{calendar_date.toString("yyyy-MM-dd")}'
                ORDER BY dateline ASC, deadline ASC"""
        self.query.exec(query)
        self.models[self.tableviews.index(tableview)].setQuery(self.query)

        delegate = TableViewDelegate()
        for i in range(tableview.model().rowCount()):
            tableview.setItemDelegateForRow(i, delegate)

        tableview.resizeColumnsToContents()
        tableview.resizeRowsToContents()
        if self.__class__.__name__ == "WeekTable":
            resolution = QtWidgets.QDesktopWidget().screenGeometry().width()
            for i in self.tableviews:
                i.setColumnWidth(2, resolution // 15)

        self.select_row_table = (-1, self.tableviews[0])

    def show_all_tasks(self) -> None:
        self.model.select()
        self.query.exec(f"""SELECT * FROM {self.user} WHERE calendar_date > 
        '{datetime.date.today().strftime('%Y-%m-%d')}' or (calendar_date='{datetime.date.today().strftime('%Y-%m-%d')}' 
        and dateline > '{datetime.datetime.today().time().strftime("%H:%M")}') 
        ORDER BY calendar_date ASC, dateline ASC, deadline ASC""")
        self.model.setQuery(self.query)

        delegate = TableViewDelegate()
        for i in range(self.task_tableview.model().rowCount()):
            self.task_tableview.setItemDelegateForRow(i, delegate)
        self.task_tableview.resizeColumnsToContents()
        self.task_tableview.resizeRowsToContents()
        self.select_row_table = (-1, self.tableviews[0])

    def add_task(self) -> None:
        calendar_date = self.calendar_widget.selectedDate()
        dialog = TaskDialog(calendar_date, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.accept(dialog, calendar_date.toPyDate(), self.model)
        self.show_day_tasks(calendar_date, self.task_tableview)

    def edit_task(self) -> None:
        selected_row, table = self.select_row_table
        model = self.models[self.tableviews.index(table)]
        if selected_row < 0:
            return

        record = model.record(selected_row)
        calendar_date = QtCore.QDate.fromString(record.value("calendar_date"), "yyyy-MM-dd")
        name = record.value("name")
        dateline = QtCore.QTime.fromString(record.value("dateline"), "hh:mm")
        deadline = QtCore.QTime.fromString(record.value("deadline"), "hh:mm")
        priority = record.value("priority")
        time = QtCore.QDate.fromString(record.value("time"), "yyyy-MM-dd")

        dialog = TaskDialog(calendar_date, self)
        dialog.name_field.setPlainText(name)
        dialog.date_field.setTime(dateline)
        dialog.deadline_field.setTime(deadline)
        dialog.priority_field.setCurrentIndex(priority)
        dialog.time_field.setDate(time)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.delete(calendar_date.toPyDate(), name, dateline, deadline, priority, time.toPyDate())
            self.accept(dialog, calendar_date.toPyDate(), model)
            self.show_day_tasks(calendar_date, table)

    def delete_task(self) -> None:
        selected_row, table = self.select_row_table
        model = self.models[self.tableviews.index(table)]
        if selected_row < 0:
            return

        delBox = QtWidgets.QMessageBox()
        delBox.setIcon(QtWidgets.QMessageBox.Question)
        delBox.setText(f"""Удалить всю серию задач или только это?
            YES - Всю серию задач
            NO - Только эту задачу
            Cancel - Не удалять задачу""")
        delBox.setWindowTitle("Удалить задачи (-у)")
        delBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        valid = delBox.exec_()

        if valid == QtWidgets.QMessageBox.Yes:
            record = model.record(selected_row)
            self.delete(QtCore.QDate.fromString(record.value("calendar_date"), "yyyy-MM-dd").toPyDate(),
                        record.value("name"), QtCore.QTime.fromString(record.value("dateline"), "hh:mm"),
                        QtCore.QTime.fromString(record.value("deadline"), "hh:mm"), record.value("priority"),
                        QtCore.QDate.fromString(record.value("time"), "yyyy-MM-dd").toPyDate())
            self.show_day_tasks(QtCore.QDate.fromString(record.value("calendar_date"), "yyyy-MM-dd"), table)

        elif valid == QtWidgets.QMessageBox.No:
            calendar_date = QtCore.QDate.fromString(model.record(selected_row).value("calendar_date"), "yyyy-MM-dd")
            model.removeRow(selected_row)
            self.show_day_tasks(calendar_date, table)
            return

    def accept(self, dialog: QtWidgets.QDialog, calendar_date: datetime.date, model: QtSql.QSqlTableModel) -> None:
        name = dialog.name_field.toPlainText()
        dateline = dialog.date_field.time().toPyTime()
        deadline = dialog.deadline_field.time().toPyTime()
        priority = dialog.priority_field.currentIndex()
        time = dialog.time_field.date().toPyDate()

        while (calendar_date.year, calendar_date.month, calendar_date.day) <= (time.year, time.month, time.day):
            record = model.record()
            record.setValue("calendar_date", QtCore.QDate(calendar_date).toString("yyyy-MM-dd"))
            record.setValue("name", name)
            record.setValue("dateline", QtCore.QTime(dateline).toString("hh:mm"))
            record.setValue("deadline", QtCore.QTime(deadline).toString("hh:mm"))
            record.setValue("priority", priority)
            record.setValue("time", QtCore.QDate(time).toString("yyyy-MM-dd"))
            model.insertRecord(-1, record)

            if priority == 0:
                break
            elif priority == 1:
                calendar_date += datetime.timedelta(1)
            elif priority == 2:
                calendar_date += datetime.timedelta(7)
            elif priority == 3:
                calendar_date += datetime.timedelta(calendar.monthrange(calendar_date.year, calendar_date.month)[1])
            elif priority == 4:
                calendar_date = datetime.datetime(calendar_date.year + 1, calendar_date.month, calendar_date.day)
        model.select()

    def delete(self, calendar_date: datetime.date, name: str, dateline: datetime.time, deadline: datetime.time,
               priority: int, time: datetime.date) -> None:

        while (calendar_date.year, calendar_date.month, calendar_date.day) <= (time.year, time.month, time.day):
            self.cursor.execute(f"""DELETE FROM {self.user} WHERE 
                            calendar_date = '{QtCore.QDate(calendar_date).toString("yyyy-MM-dd")}' and 
                            name = '{name}' and dateline = '{QtCore.QTime(dateline).toString("hh:mm")}' and 
                            deadline = '{QtCore.QTime(deadline).toString("hh:mm")}' and priority = '{priority}' and 
                            time = '{QtCore.QDate(time).toString("yyyy-MM-dd")}'""")
            self.connection.commit()

            if priority == 0:
                break
            elif priority == 1:
                calendar_date += datetime.timedelta(1)
            elif priority == 2:
                calendar_date += datetime.timedelta(7)
            elif priority == 3:
                calendar_date += datetime.timedelta(calendar.monthrange(calendar_date.year, calendar_date.month)[1])
            elif priority == 4:
                calendar_date = datetime.datetime(calendar_date.year + 1, calendar_date.month, calendar_date.day)


class WeekTable(TableManager):
    def initUI(self) -> None:
        self.week = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.week.dateChanged.connect(self.week_changed)
        self.week.setCalendarPopup(True)
        self.weekdates = self.get_week_dates(QtCore.QDate.currentDate())

        self.edit_task_button = QtWidgets.QPushButton("Редактировать задачу")
        self.edit_task_button.clicked.connect(self.edit_task)

        self.delete_task_button = QtWidgets.QPushButton("Удалить задачу")
        self.delete_task_button.clicked.connect(self.delete_task)

        monday_layout = QtWidgets.QVBoxLayout()
        self.monday_tableview = QtWidgets.QTableView(self)
        self.monday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        monday_layout.addWidget(QtWidgets.QLabel("Понедельник"))
        monday_layout.addWidget(self.monday_tableview)

        tuesday_layout = QtWidgets.QVBoxLayout()
        self.tuesday_tableview = QtWidgets.QTableView(self)
        self.tuesday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        tuesday_layout.addWidget(QtWidgets.QLabel("Вторник"))
        tuesday_layout.addWidget(self.tuesday_tableview)

        wednesday_layout = QtWidgets.QVBoxLayout()
        self.wednesday_tableview = QtWidgets.QTableView(self)
        self.wednesday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        wednesday_layout.addWidget(QtWidgets.QLabel("Среда"))
        wednesday_layout.addWidget(self.wednesday_tableview)

        thursday_layout = QtWidgets.QVBoxLayout()
        self.thursday_tableview = QtWidgets.QTableView(self)
        self.thursday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        thursday_layout.addWidget(QtWidgets.QLabel("Четверг"))
        thursday_layout.addWidget(self.thursday_tableview)

        friday_layout = QtWidgets.QVBoxLayout()
        self.friday_tableview = QtWidgets.QTableView(self)
        self.friday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        friday_layout.addWidget(QtWidgets.QLabel("Пятница"))
        friday_layout.addWidget(self.friday_tableview)

        saturday_layout = QtWidgets.QVBoxLayout()
        self.saturday_tableview = QtWidgets.QTableView(self)
        self.saturday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        saturday_layout.addWidget(QtWidgets.QLabel("Суббота"))
        saturday_layout.addWidget(self.saturday_tableview)

        sunday_layout = QtWidgets.QVBoxLayout()
        self.sunday_tableview = QtWidgets.QTableView(self)
        self.sunday_tableview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        sunday_layout.addWidget(QtWidgets.QLabel("Воскресенье"))
        sunday_layout.addWidget(self.sunday_tableview)

        self.tableviews = [self.monday_tableview, self.tuesday_tableview, self.wednesday_tableview,
                           self.thursday_tableview, self.friday_tableview, self.saturday_tableview,
                           self.sunday_tableview]
        for tableview in self.tableviews:
            tableview.clicked.connect(self.cell_changed)

        self.query = QtSql.QSqlQuery()
        self.monday_model = QtSql.QSqlTableModel(self)
        self.tuesday_model = QtSql.QSqlTableModel(self)
        self.wednesday_model = QtSql.QSqlTableModel(self)
        self.thursday_model = QtSql.QSqlTableModel(self)
        self.friday_model = QtSql.QSqlTableModel(self)
        self.saturday_model = QtSql.QSqlTableModel(self)
        self.sunday_model = QtSql.QSqlTableModel(self)
        self.models = [self.monday_model, self.tuesday_model, self.wednesday_model, self.thursday_model,
                       self.friday_model, self.saturday_model, self.sunday_model]
        self.do_table_model()

        high_layout = QtWidgets.QHBoxLayout()
        high_layout.addWidget(self.week)
        high_layout.addWidget(self.edit_task_button)
        high_layout.addWidget(self.delete_task_button)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addLayout(monday_layout)
        h_layout.addLayout(tuesday_layout)
        h_layout.addLayout(wednesday_layout)
        h_layout.addLayout(thursday_layout)
        h_layout.addLayout(friday_layout)
        h_layout.addLayout(saturday_layout)
        h_layout.addLayout(sunday_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(high_layout)
        main_layout.addLayout(h_layout)

    def do_table_model(self) -> None:
        for tableview, model in zip(self.tableviews, self.models):
            model.setTable(self.user)
            model.setHeaderData(0, QtCore.Qt.Horizontal, 'ИД')
            model.setHeaderData(1, QtCore.Qt.Horizontal, 'День')
            model.setHeaderData(2, QtCore.Qt.Horizontal, 'О задаче')
            model.setHeaderData(3, QtCore.Qt.Horizontal, 'Начало')
            model.setHeaderData(4, QtCore.Qt.Horizontal, 'Конец')
            model.setHeaderData(5, QtCore.Qt.Horizontal, 'Дублирование')
            model.setHeaderData(6, QtCore.Qt.Horizontal, 'До какого дня')
            model.select()
            tableview.setModel(model)
            tableview.hideColumn(0)
            tableview.hideColumn(1)
            tableview.hideColumn(5)
            tableview.hideColumn(6)
            tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            tableview.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.exec_query()

    def week_changed(self) -> None:
        self.weekdates = self.get_week_dates(self.week.date())
        self.exec_query()

    def exec_query(self) -> None:
        for i in zip(self.weekdates, self.tableviews):
            self.show_day_tasks(*i)

    @staticmethod
    def get_week_dates(date: QtCore.QDate) -> list:
        week_dates = []
        start_of_week = date.addDays(-date.dayOfWeek() + 1)
        for i in range(7):
            current_date = start_of_week.addDays(i)
            week_dates.append(current_date)
        return week_dates
