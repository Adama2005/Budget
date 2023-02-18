import sys
import unicodedata as ud

from random import randint
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Slot, QPoint, QRect, QSize, QSettings, QObject, QSortFilterProxyModel
from PySide6.QtGui import QPen, QPainter, QFont, QColor, QDoubleValidator
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice, QBarSeries, QLineSeries, QBarSet, \
    QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, \
    QLabel, QComboBox, QHBoxLayout, QFormLayout, QGridLayout, QLineEdit, QMessageBox, QFileDialog, QTableView, \
    QItemDelegate, QAbstractItemView, QCheckBox
from PySide6 import QtGui, QtCore




class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fenetre_principale = self

        self.title = "Budget"
        self.setWindowTitle(self.title, )

        # self.budget_widget = Budget_Widget(self, self.connecteurSQL, self.fenetre_principale)
        # self.setCentralWidget(self.budget_widget)
        self.show()


def Window():
    app = QApplication(sys.argv)
    MyApp()
    sys.exit(app.exec())


if __name__ == '__main__':
    Window()
