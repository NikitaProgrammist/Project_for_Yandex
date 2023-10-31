from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont


class DateDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        return ':'.join(value.split('-')[::-1])


class QCalendarWidget(QtWidgets.QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #FFFFFF; color: #FF0000;")
        font = QFont("Roboto", 10)
        self.setFont(font)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setGridVisible(True)
