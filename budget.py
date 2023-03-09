import sys

from PySide6.QtWidgets import QWidget, QApplication, QListWidget, QFormLayout, QLineEdit, QHBoxLayout, QRadioButton, \
    QLabel, QCheckBox, QStackedWidget, QVBoxLayout, QGridLayout, QFrame, QComboBox
from PySide6.QtCore import QEvent, Qt, QRect
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import librairieSQL
from librairieSQL import Sql

g_connexionSql = Sql()


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class AfficherBudget(QWidget):
    def __init__(self, donnees_budget):
        super(AfficherBudget, self).__init__()

        """
        Stack (H)
            leftLayout (V)
            topLayout (H)   soldeLayout (H)
            montantsBudgetLayout (G)
            centreLayout (V)
                infoLayout (V)
                    ligneBudget (H)
                    soldeLayout (H)
                budgetLayout (V)
                    saisieLayout (H)
        """

        self.b = donnees_budget

        self.leftLayout = QVBoxLayout()
        self.centreLayout = QVBoxLayout()
        self.labelInfo = QLabel()
        self.labelBudget = QLabel()

        self.initialiserLayoutBudget()

        # Début de - Initialiser le stack d'affichage du budget -------------
        self.stack1 = QWidget()
        self.stack2 = QWidget()

        self.stack1BudgetInfo()
        self.stack2Budget()

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        # Fin de - Initialiser le stack d'affichage du budget -------------

        self.afficherBudget()

        self.show()

    def initialiserLayoutBudget(self):
        topLayout = QHBoxLayout()
        soldeLayout = QHBoxLayout()
        montantsBudgetLayout = QGridLayout()

        pixmap = QPixmap("./images/search.png")
        pixmap.setDevicePixelRatio(10)
        self.labelInfo.setPixmap(pixmap)

        pixmap = QPixmap("./images/budget.png")
        pixmap.setDevicePixelRatio(10)
        self.labelBudget.setPixmap(pixmap)

        self.leftLayout.addWidget(self.labelInfo)
        self.leftLayout.addSpacing(5)
        self.leftLayout.addWidget(self.labelBudget)

        labelPeriode = QLabel("Période")
        # TODO: Faire le chargement du combo Période
        comboPeriode = QComboBox()
        # TODO: Faire le chargement du combo Année
        labelAnnee = QLabel("Année")
        comboAnnee = QComboBox()
        topLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        topLayout.addWidget(labelPeriode)
        topLayout.addWidget(comboPeriode)
        topLayout.addWidget(QLabel(''))
        topLayout.addWidget(QLabel(''))
        topLayout.addWidget(labelAnnee)
        topLayout.addWidget(comboAnnee)
        topLayout.addWidget(QLabel(''), Qt.AlignmentFlag.AlignRight)

        # TODO: Modifier la taille
        soldeLayout.addWidget(QLabel("Solde en date du jour"))
        soldeLayout.addWidget(QLabel("$ 200.00"))
        topLayout.addLayout(soldeLayout)
        self.centreLayout.addLayout(topLayout)

        # TODO: Les montants de cette section sont déjà cumulés en mémoire. C'est facile de tout cumuler maintenant.
        montantsBudgetLayout.addWidget(QLabel(''), 0, 0)
        montantsBudgetLayout.addWidget(QLabel('Total prévu pour la période'), 1, 0)
        montantsBudgetLayout.addWidget(QLabel('$ 2453.24'), 1, 1)
        montantsBudgetLayout.addWidget(QLabel('Total réel pour la période'), 2, 0)
        montantsBudgetLayout.addWidget(QLabel('$ 2233.24'), 2, 1)
        montantsBudgetLayout.addWidget(QLabel('Économie'), 3, 0)
        montantsBudgetLayout.addWidget(QLabel('$ 230.00'), 3, 1)
        for i in range(1, 3):
            montantsBudgetLayout.addWidget(QLabel(''), i, 2)
            montantsBudgetLayout.addWidget(QLabel(''), i, 3)
            montantsBudgetLayout.addWidget(QLabel(''), i, 4)
        montantsBudgetLayout.addWidget(QLabel(''), 8, 0)

        self.centreLayout.addLayout(montantsBudgetLayout)

    def afficherBudget(self):
        hBox = QHBoxLayout(self)
        hBox.addLayout(self.leftLayout)
        self.centreLayout.addWidget(self.Stack)
        hBox.addLayout(self.centreLayout)

        self.setLayout(hBox)
        self.labelInfo.installEventFilter(self)
        self.labelBudget.installEventFilter(self)
        self.Stack.setCurrentIndex(0)
        self.labelBudget.setDisabled(True)

        self.setGeometry(10, 10, 800, 600)
        self.setWindowTitle('Budget Brien/Desrosiers')

    def stack1BudgetInfo(self):
        infoLayout = QGridLayout()
        sectionPrecedente = -1

        noColonne = 0
        noLigne = 5
        noLigneSolde = 0

        changementSection = False
        for ligne in self.b.budget_Definition:
            if ligne['noSectionBudget'] != sectionPrecedente:
                sectionPrecedente = ligne['noSectionBudget']

                nomSection = ''
                for section in self.b.budget_nomSection:
                    # Le but ici est de seulement trouver le titre de la section
                    if ligne['noSectionBudget'] == section['noSectionBudget']:
                        nomSection = section['nomSection']
                        changementSection = True
                        break

            if changementSection:
                if noLigne + 4 >= 25:
                    if noLigne > noLigneSolde:
                        noLigneSolde = noLigne
                    noLigne = 5
                    infoLayout.addWidget(QLabel(), noLigne, 5)
                    infoLayout.addWidget(QLabel(), noLigne, 6)
                    infoLayout.addWidget(QLabel(), noLigne, 7)
                    noColonne = 8

                # TODO: Modifier la taille
                if noLigne == 5:
                    infoLayout.addWidget(QLabel('Transactions'), noLigne, 1 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                    infoLayout.addWidget(QLabel('Montant prévu'), noLigne, 2 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                    infoLayout.addWidget(QLabel('Montant réel'), noLigne, 3 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                    noLigne += 1

                infoLayout.addWidget(QLabel())
                noLigne += 1

                infoLayout.addWidget(QLabel(nomSection), noLigne, 0 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                changementSection = False
                noLigne += 1

            infoLayout.addWidget(QLabel(str(ligne['nomTypeBudget'])), noLigne, 1 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
            infoLayout.addWidget(QLabel(str(ligne['montantPrevu'])), noLigne, 2 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
            # TODO: Remplacer montantPrevu par montantReel
            infoLayout.addWidget(QLineEdit(str(ligne['montantPrevu'])), noLigne, 3 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
            noLigne += 1
        infoLayout.setVerticalSpacing(5)
        self.stack1.setLayout(infoLayout)

    def stack2Budget(self):
        budgetLayout = QVBoxLayout()
        saisieLayout = QHBoxLayout()

        saisieLayout.addWidget(QLabel("Dépense maintenant"))
        saisieLayout.addWidget(QLabel("$ 300.00"))
        budgetLayout.addLayout(saisieLayout)
        self.stack2.setLayout(budgetLayout)

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

    # def display(self, i):
    #     self.Stack.setCurrentIndex(i)


"""
C'est la classe de base du budget. Toutes les transactions possibles sont dans cette classe.
Les informations de chaque transaction sont dans cette classe.
"""
class Budget:
    def __init__(self):
        super().__init__()
        self.budget_Definition = []
        self.budget_Periode = []
        self.budget_nomSection = []
        self.totalPrevuPeriode = 0
        self.totalParSection = []
        self.anneeBudget = 2023
        self.noPeriodeBudget = 2
        self.codeUtilisateur = "Dany"
        self.versionBudget = 0

        """
        codeUtilisateur : utilisateur pour qui est fait le budget
        nomTypeBudget : nom de la tx budget à payer
        noSectionBudget : section du budget où cette tx est affichée
        dateFinPrevue : quand ce montant ne sera plus à payer
        jourPaiement : jour d'une date
        montantPrevu : integer
        infoCachee : 0 ou 1
        factureCommune : 0 ou 1
        montantTotalPrevu : Montant total du budget prévu
        """

    def lirePeriodeBudget(self):
        requete = "SELECT noPeriode, nomPeriode, dateDebutPeriode, dateFinPeriode, jourDebutPeriode, jourFinPeriode " \
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

    def lireNomSectionBudget(self):
        requete = "SELECT * " \
                  "FROM " \
                  "    sectionBudget"

        if g_connexionSql.ouvrirRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                nouvelleSection = {'noSectionBudget': ligneSQL.value('noSectionBudget'), 'nomSection': ligneSQL.value('nomSection')}
                self.budget_nomSection.append(nouvelleSection)

                ligneSQL = g_connexionSql.lireEnr()

    def lireDefinitionBudget(self):
        requete = "SELECT codeUtilisateur, ligneBudget, nomTypeBudget, noSectionBudget, dateFinPrevue, jourPaiement, montantPrevu, infoCachee, factureCommune " \
                  "FROM " \
                  "    type_budget " \
                  "WHERE " \
                  f"    codeUtilisateur = '{self.codeUtilisateur}' AND " \
                  f"    noSectionBudget <= 4 " \
                  f"ORDER BY " \
                  f"   codeUtilisateur, " \
                  f"   noSectionBudget, " \
                  f"   ligneBudget"

        if g_connexionSql.ouvrirRequete(requete):
            noSectionBudget = 0
            montantTotalSection = 0
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                if noSectionBudget != ligneSQL.value("noSectionBudget"):
                    if self.jourDansPeriode(int(ligneSQL.value("jourPaiement"))) or ligneSQL.value("jourPaiement") == 0:
                        section = {"noSectionBudget": noSectionBudget, "montantTotalPrevu": montantTotalSection}
                        montantTotalSection = ligneSQL.value("montantPrevu")
                        self.totalParSection.append(section)
                        noSectionBudget = ligneSQL.value("noSectionBudget")
                else:
                    if self.jourDansPeriode(int(ligneSQL.value("jourPaiement"))) or ligneSQL.value("jourPaiement") == 0:
                        montantTotalSection += ligneSQL.value("montantPrevu")

                nouvelleLigne = {"ligneBudget"    : ligneSQL.value("ligneBudget"),
                                 "nomTypeBudget"  : ligneSQL.value("nomTypeBudget"),
                                 "noSectionBudget": ligneSQL.value("noSectionBudget"),
                                 "dateFinPrevue"  : ligneSQL.value("dateFinPrevue"),
                                 "jourPaiement"   : ligneSQL.value("jourPaiement"),
                                 "montantPrevu"   : ligneSQL.value("montantPrevu"),
                                 "infoCachee"     : ligneSQL.value("infoCachee"),
                                 "factureCommune" : ligneSQL.value("factureCommune"),
                                 }
                if self.jourDansPeriode(int(ligneSQL.value("jourPaiement"))) or ligneSQL.value("jourPaiement") == 0:
                    self.budget_Definition.append(nouvelleLigne)

                    # TODO: Il faut que j'ajoute le dernier montant de la section

                    if ligneSQL.value("noSectionBudget") == 0:
                        self.totalPrevuPeriode += ligneSQL.value("montantPrevu")
                    else:
                        self.totalPrevuPeriode -= ligneSQL.value("montantPrevu")

                ligneSQL = g_connexionSql.lireEnr()
        else:
            print("fonctionne pas")

    def jourDansPeriode(self, jour_tx):
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


def main():
    b = Budget()

    nomBD = "/Users/danydesrosiers/Library/Mobile " \
            "Documents/com~apple~CloudDocs/Budget/budget.sqlite3"
    if g_connexionSql.ouvrirBD(nomBD):
        b.lirePeriodeBudget()
        b.lireNomSectionBudget()
        b.lireDefinitionBudget()

        app = QApplication(sys.argv)
        ex = AfficherBudget(b)

        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == '__main__':
    main()
