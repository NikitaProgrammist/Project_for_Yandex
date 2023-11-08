import sys
from PyQt5 import QtWidgets, QtSql, QtCore
from tablemanager import TableManager, WeekTable
from listmanager import ListManager, MarkedTasks, ImportantTasks
from dialogs import LoginDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        x = self.login()
        if x is None:
            sys.exit(0)
        self.user = x
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('dist/task_manager.db')
        self.db.open()
        self.initUI()

    def initUI(self) -> None:
        self.setGeometry(0, 0, 1000, 750)
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - (self.frameSize().height() // 2))
        self.setWindowTitle("TaskPlanner")

        self.tab_widget = QtWidgets.QTabWidget(self)

        self.maintable = TableManager(self.user)
        self.tab_widget.addTab(self.maintable, "Задачи на день")

        self.weektable = WeekTable(self.user)
        self.tab_widget.addTab(self.weektable, "Задачи на неделю")

        self.list_tasks = ListManager(self.user)
        self.tab_widget.addTab(self.list_tasks, "Список задач")

        self.marked_tasks = MarkedTasks(self.user)
        self.tab_widget.addTab(self.marked_tasks, "Помеченные задачи")

        self.important_tasks = ImportantTasks(self.user)
        self.tab_widget.addTab(self.important_tasks, "Важные задачи")

        self.setCentralWidget(self.tab_widget)

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index: int) -> None:
        if index == 0:
            self.maintable.show_all_tasks()
        if index == 1:
            self.weektable.week_changed()
        if index == 2:
            self.list_tasks.filter_func()
        if index == 3:
            self.marked_tasks.filter_func()
        if index == 4:
            self.important_tasks.filter_func()

    def login(self) -> str:
        dialog = LoginDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return dialog.username


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    sys.excepthook = except_hook
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
