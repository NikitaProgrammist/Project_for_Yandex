import datetime
import re
from typing import Any
from PyQt5 import QtWidgets, QtCore, QtGui


class TableViewDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value: str, locale: QtCore.QLocale) -> str:
        pattern = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
        if pattern.match(value):
            return ':'.join(value.split('-')[::-1])
        return value

    def initStyleOption(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        super().initStyleOption(option, index)
        model = index.model()
        table_day = datetime.datetime.strptime(model.data(index.sibling(index.row(), 1)), "%Y-%m-%d").date()
        deadline = datetime.datetime.strptime(model.data(index.sibling(index.row(), 4)), "%H:%M").time()
        dateline = datetime.datetime.strptime(model.data(index.sibling(index.row(), 3)), "%H:%M").time()
        today_date = datetime.date.today()
        today_time = datetime.datetime.today().time()
        if (table_day < today_date or (table_day == today_date and deadline < today_time)) and deadline > dateline:
             option.palette.setColor(option.palette.Text, QtGui.QColor(125, 125, 125))
        else:
            option.palette.setColor(option.palette.Text, QtGui.QColor(0, 0, 0))


class QCalendarWidget(QtWidgets.QCalendarWidget):
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #FFFFFF; color: #FF0000;")
        font = QtGui.QFont("Roboto", 10)
        self.setFont(font)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setGridVisible(True)


class QComboBox(QtWidgets.QComboBox):
    def addItem(self, text: str, userData: Any | None = None) -> None:
        super(QComboBox, self).addItem(text)
        item = self.model().item(self.count()-1, 0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)

    def addItems(self, items: Any) -> None:
        for i in items:
            self.addItem(i)
