import sys

from PySide6.QtWidgets import QWidget, QApplication, QListWidget, QFormLayout, QLineEdit, QHBoxLayout, QRadioButton, \
    QLabel, QCheckBox, QStackedWidget, QVBoxLayout, QGridLayout, QFrame, QComboBox
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPixmap
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import librairieSQL
from librairieSQL import Sql

g_connexionSql = Sql()

class stackedExample(QWidget):
    def __init__(self):
        super(stackedExample, self).__init__()

        """
        Stack (H)
            leftLayout (V)
            topLayout (H)
            centreLayout (V)
                infoLayout (V)
                    soldeLayout (H)
                budgetLayout (V)
                    saisieLayout (H)
        """

        leftLayout = QVBoxLayout()
        self.centreLayout = QVBoxLayout()
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
        # ------------------------ Batir l'affichage principal

        self.stack1 = QWidget()
        self.stack2 = QWidget()

        self.stack1BudgetInfo()
        self.stack2Budget()

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)

        hBox = QHBoxLayout(self)
        hBox.addLayout(leftLayout)
        self.centreLayout.addWidget(self.Stack)
        hBox.addLayout(self.centreLayout)

        self.setLayout(hBox)
        self.labelInfo.installEventFilter(self)
        self.labelBudget.installEventFilter(self)
        self.Stack.setCurrentIndex(0)
        self.labelBudget.setDisabled(True)

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
        self.stack1.setLayout(infoLayout)

    def stack2Budget(self):
        budgetLayout = QVBoxLayout()
        saisieLayout = QHBoxLayout()

        saisieLayout.addWidget(QLabel("Dépense maintenant"))
        saisieLayout.addWidget(QLabel("$ 300.00"))
        budgetLayout.addLayout(saisieLayout)
        self.stack2.setLayout(budgetLayout)

    def display(self, i):
        self.Stack.setCurrentIndex(i)


"""
C'est la classe de base du budget. Toutes les transactions possibles sont dans cette classe.
Les informations de chaque transaction sont dans cette classe.
"""
class Budget:
    def __init__(self):
        super().__init__()
        self.budget_Definition = []
        self.budget_Periode = []

        self.anneeBudget = 2023
        self.noPeriodeBudget = 2
        self.codeUtilisateur = "Dany"
        self.versionBudget = 0

        """
        codeUtilisateur : utilisateur pour qui est fait le budget
        nomTypeBudget : nom de la tx budget à payer
        noSectionBudget : section du budget où cette tx ests affichée
        dateFinPrevue : quand ce montant ne sera plus à payer
        jourPaiement : jour d'une date
        montantPrevu : integer
        infoCachee : 0 ou 1
        factureCommune : 0 ou 1
        montantTotalPrevu : Montant total du budget prévu
        """

    def lirePeriodeBudget(self):
        requete = "SELECT " \
                  "    noPeriode, " \
                  "    nomPeriode, " \
                  "    dateDebutPeriode, " \
                  "    dateFinPeriode, " \
                  "    jourDebutPeriode, " \
                  "    jourFinPeriode " \
                  "FROM " \
                  "    periode " \
                  "WHERE " \
                  f"    anneeBudget = '{self.anneeBudget}' " \
                  f"ORDER BY " \
                  f"   anneeBudget, " \
                  f"   noPeriode"

        if g_connexionSql.ouvrirRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                nouvelleLigne = {"noPeriode"       : ligneSQL.value("noPeriode"),
                                 "nomPeriode"      : ligneSQL.value("nomPeriode"),
                                 "dateDebutPeriode": ligneSQL.value("dateDebutPeriode"),
                                 "dateFinPeriode"  : ligneSQL.value("dateFinPeriode"),
                                 "jourDebutPeriode": ligneSQL.value("jourDebutPeriode"),
                                 "jourFinPeriode"  : ligneSQL.value("jourFinPeriode"),
                                 }
                self.budget_Periode.append(nouvelleLigne)

                ligneSQL = g_connexionSql.lireEnr()


    def lireDefinitionBudget(self):
        montantTotalPrevu = 0
        requete = "SELECT " \
                  "    codeUtilisateur, " \
                  "    ligneBudget, " \
                  "    nomTypeBudget, " \
                  "    noSectionBudget, " \
                  "    dateFinPrevue, " \
                  "    jourPaiement, " \
                  "    montantPrevu, " \
                  "    infoCachee, " \
                  "    factureCommune " \
                  "FROM " \
                  "    type_budget " \
                  "WHERE " \
                  f"    codeUtilisateur = '{self.codeUtilisateur}' " \
                  f"ORDER BY " \
                  f"   codeUtilisateur, " \
                  f"   ligneBudget"

        if g_connexionSql.ouvrirRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                nouvelleLigne = {"codeUtilisateur": ligneSQL.value("codeUtilisateur"),
                                 "ligneBudget"    : ligneSQL.value("ligneBudget"),
                                 "nomTypeBudget"  : ligneSQL.value("nomTypeBudget"),
                                 "noSectionBudget": ligneSQL.value("noSectionBudget"),
                                 "dateFinPrevue"  : ligneSQL.value("dateFinPrevue"),
                                 "jourPaiement"   : ligneSQL.value("jourPaiement"),
                                 "montantPrevu"   : ligneSQL.value("montantPrevu"),
                                 "infoCachee"     : ligneSQL.value("infoCachee"),
                                 "factureCommune" : ligneSQL.value("factureCommune"),
                                 }
                self.budget_Definition.append(nouvelleLigne)

                ligneSQL = g_connexionSql.lireEnr()
        else:
            print("fonctionne pas")

    def jourDansPeriode(self, jour_tx):

        # if self.jourDansPeriode(ligneSQL.value("jourPaiement")):
        #     if ligneSQL.value("noSectionBudget") == 0:  # Entrée d'argent
        #         montantTotalPrevu += ligneSQL.value("montantPrevu")
        #     else:
        #         montantTotalPrevu -= ligneSQL.value("montantPrevu")

        # 2021228 - 20230112
        for infoPeriode in self.budget_Periode:
            if infoPeriode["noPeriode"] == self.noPeriodeBudget:
                if str(infoPeriode["dateDebutPeriode"])[4:6] == str(infoPeriode["dateFinPeriode"])[4:6]:
                    #  Vérification du mois
                    if infoPeriode["jourDebutPeriode"] <= jour_tx <= infoPeriode["jourFinPeriode"]:
                        return True
                else:
                    if jour_tx <= infoPeriode["jourDebutPeriode"] and jour_tx <= infoPeriode["jourFinPeriode"]:
                        return True

        return False

    def faireEcranBudget(self):
        print("Faire écran budget)")

def main():
    b = Budget()

    nomBD = "/Users/danydesrosiers/Library/Mobile " \
            "Documents/com~apple~CloudDocs/Budget/budget.sqlite3"
    if g_connexionSql.ouvrirBD(nomBD):
        b.lirePeriodeBudget()
        b.lireDefinitionBudget()
        valide = b.jourDansPeriode(11)
        print(valide)

        # b.faireEcranBudget()

        app = QApplication(sys.argv)
        ex = stackedExample()

        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == '__main__':
    main()
