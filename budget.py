import sys

from PySide6.QtWidgets import QWidget, QApplication, QListWidget, QFormLayout, QLineEdit, QHBoxLayout, QRadioButton, \
    QLabel, QCheckBox, QStackedWidget, QVBoxLayout, QGridLayout, QFrame, QComboBox
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPixmap

class stackedExample(QWidget):

    def __init__(self):
        super(stackedExample, self).__init__()

        """
        outerLayout (H)
            leftLayout (V)
            centreLayout (V)
                topLayout (H)
                infoLayout (V)
                    soldeLayout (H)
                budgetLayout (V)
                    saisieLayout (H)
        """

        outerLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        self.centreLayout = QVBoxLayout()
        self.centreLayout2 = QVBoxLayout()
        topLayout = QHBoxLayout()

        self.labelInfo = QLabel()
        pixmap = QPixmap("./images/search.png")
        pixmap.setDevicePixelRatio(10)
        self.labelInfo.setPixmap(pixmap)

        self.labelBudget = QLabel()
        pixmap = QPixmap("./images/budget.png")
        pixmap.setDevicePixelRatio(10)
        self.labelBudget.setPixmap(pixmap)

        leftLayout.addWidget(self.labelInfo)
        leftLayout.addSpacing(20)
        leftLayout.addWidget(self.labelBudget)

        labelPeriode = QLabel("Période")
        comboPeriode = QComboBox()
        labelAnnee = QLabel("Année")
        comboAnnee = QComboBox()
        topLayout.addWidget(labelPeriode)
        topLayout.addWidget(comboPeriode)
        topLayout.addWidget(labelAnnee)
        topLayout.addWidget(comboAnnee)
        self.centreLayout.addLayout(topLayout)
        self.centreLayout2.addLayout(topLayout)

        outerLayout.addLayout(leftLayout)
        outerLayout.addLayout(topLayout)
        # ------------------------ Batir l'affichage principal


        self.stack1 = QWidget()
        self.stack2 = QWidget()

        self.stack1BudgetInfo()
        self.stack2Budget()

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)

        hBox = QHBoxLayout(self)
        hBox.addLayout(outerLayout)
        hBox.addWidget(self.Stack)

        self.Stack.setCurrentIndex(0)
        self.labelBudget.setDisabled(True)
        self.setLayout(hBox)
        self.labelInfo.installEventFilter(self)
        self.labelBudget.installEventFilter(self)

        self.setGeometry(10, 10, 800, 600)
        self.setWindowTitle('StackedWidget demo')

        self.show()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if obj is self.labelInfo or obj is self.labelBudget:
                if obj is self.labelInfo:
                    self.labelBudget.setDisabled(True)
                    self.labelInfo.setDisabled(False)
                    self.Stack.setCurrentIndex(0)
                else:
                    self.labelBudget.setDisabled(False)
                    self.labelInfo.setDisabled(True)
                    self.Stack.setCurrentIndex(1)

        return super().eventFilter(obj, event)

    def stack1BudgetInfo(self):
        infoLayout = QVBoxLayout()
        soldeLayout = QHBoxLayout()

        soldeLayout.addWidget(QLabel("Solde en date du jour"))
        soldeLayout.addWidget(QLabel("$ 200.00"))
        infoLayout.addLayout(soldeLayout)
        self.centreLayout.addLayout(infoLayout)

        self.stack1.setLayout(self.centreLayout)


    def stack2Budget(self):
        budgetLayout = QVBoxLayout()
        saisieLayout = QHBoxLayout()

        saisieLayout.addWidget(QLabel("Dépense maintenant"))
        saisieLayout.addWidget(QLabel("$ 300.00"))
        budgetLayout.addLayout(saisieLayout)
        self.centreLayout2.addLayout(budgetLayout)

        self.stack2.setLayout(self.centreLayout2)

    def display(self, i):
        self.Stack.setCurrentIndex(i)


def main():
    app = QApplication(sys.argv)
    ex = stackedExample()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
