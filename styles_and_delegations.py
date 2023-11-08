from typing import Any

from PyQt5 import QtWidgets, QtCore, QtGui


class DateDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value: str, locale: QtCore.QLocale) -> str:
        return ':'.join(value.split('-')[::-1])


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
