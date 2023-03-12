import sys

from PySide6.QtWidgets import QWidget, QApplication, QListWidget, QFormLayout, QLineEdit, QHBoxLayout, QRadioButton, \
    QLabel, QCheckBox, QStackedWidget, QVBoxLayout, QGridLayout, QFrame, QComboBox, QGroupBox, QScrollArea
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import librairieSQL
from librairieSQL import Sql

g_connexionSql = Sql()


# TODO: Sauvegarder tout le temps, après le changement d'une donnée dans l'écran
# TODO: Pour le moment pas de rollback

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
            centreLayout (G)
                infoLayout (V)
                    ligneBudget (H)
                    soldeLayout (H)
                budgetLayout (V)
                    saisieLayout (H)
        """

        self.b = donnees_budget

        self.leftLayout = QVBoxLayout()
        self.centreLayout = QVBoxLayout()
        self.budgetLayout = QVBoxLayout()
        self.labelInfo = QLabel()
        self.labelBudget = QLabel()

        self.montantRevenuPrevu = 0
        self.montantDepensePrevue = 0
        self.montantRevenuReel = 0
        self.montantDepenseReelle = 0
        self.montantFactureCommune = 0
        self.montantsBudgetLayout = QGridLayout()

        # Début de - Initialiser le stack d'affichage du budget -------------
        scrollArea = QScrollArea()
        scrollWidget = QWidget()

        # -------------- > Affichage de l'écran Budget
        self.calculerTotauxPrevusReels()
        self.afficherTotauxPrevus()
        self.afficherTotauxReels()
        self.chargerPeriode()
        self.afficherBudgetPeriode()
        # <--------------- Affichage de l'écran Budget

        self.budgetLayout = self.chargerBudget()
        scrollWidget.setLayout(self.budgetLayout)
        scrollArea.setWidget(scrollWidget)
        self.centreLayout.addWidget(scrollArea)

        self.afficherBudget()

        self.show()

    def afficherBudgetPeriode(self):
        totalGroupBox = QGroupBox('Budget pour la période')
        totalGroupBox.setLayout(self.montantsBudgetLayout)
        self.centreLayout.addWidget(totalGroupBox)

    def calculerTotauxPrevusReels(self):
        for ligne in self.b.budget_Prevu:
            if ligne['factureCommune'] == 1:
                self.montantFactureCommune += ligne['montantPrevu']
            if ligne['noSectionBudget'] == 0:
                self.montantRevenuPrevu += ligne['montantPrevu']
            else:
                self.montantDepensePrevue += ligne['montantPrevu']

        for ligne in self.b.budget_Reel:
            if ligne['noSectionBudget'] == 0:
                self.montantRevenuReel += ligne['montantReel']
            else:
                self.montantDepenseReelle += ligne['montantReel']

        self.montantFactureCommune = self.montantFactureCommune // 2
        self.montantRevenuPrevu += self.montantFactureCommune

    def chargerPeriode(self):
        topLayout = QHBoxLayout()
        soldeLayout = QHBoxLayout()
        # self.montantsBudgetLayout = QGridLayout()

        # TODO: Faire le chargement du combo Période

        labelPeriode = QLabel("Période")
        comboPeriode = QComboBox()
        for per in self.b.budget_Periode:
            comboPeriode.addItem(per['nomPeriode'])

        labelAnnee = QLabel("Année")
        comboAnnee = QComboBox()
        for annee in self.b.budget_Annee:
            comboAnnee.addItem(str(annee))

        topLayout.addWidget(labelPeriode)
        topLayout.addWidget(comboPeriode)
        topLayout.addWidget(QLabel())
        topLayout.addWidget(QLabel())
        topLayout.addWidget(QLabel())
        topLayout.addWidget(labelAnnee)
        topLayout.addWidget(comboAnnee)
        topLayout.addWidget(QLabel(''), Qt.AlignmentFlag.AlignRight)

        soldeLayout.addWidget(QLabel("Solde en date du jour"))
        soldeLayout.addWidget(QLabel("$ 200.00"))
        topLayout.addLayout(soldeLayout)

        topGroupBox = QGroupBox()
        topGroupBox.setLayout(topLayout)
        self.centreLayout.addWidget(topGroupBox)

    def afficherBudget(self):
        hBox = QHBoxLayout(self)
        hBox.addLayout(self.leftLayout)
        hBox.addLayout(self.centreLayout)
        self.setLayout(hBox)

        self.setGeometry(600, 10, 600, 1000)
        self.setWindowTitle('Budget Brien/Desrosiers')

    def afficherTotauxPrevus(self):
        # TODO: Les montants de cette section sont déjà cumulés en mémoire. C'est facile de tout cumuler maintenant.
        self.montantsBudgetLayout.addWidget(QLabel('Total prévu des revenus'), 0, 0)
        self.montantsBudgetLayout.addWidget(QLabel(str(self.montantRevenuPrevu)), 0, 1)
        self.montantsBudgetLayout.addWidget(QLabel('Total prévu des dépenses'), 1, 0)
        self.montantsBudgetLayout.addWidget(QLabel(str(self.montantDepensePrevue)), 1, 1)

        montantRevenuOuDette = self.montantRevenuPrevu - self.montantDepensePrevue
        if montantRevenuOuDette >= 0:
            revenuOuDette = 'Total prévu des économies'
        else:
            revenuOuDette = 'Total prévu des pertes'
        self.montantsBudgetLayout.addWidget(QLabel(revenuOuDette), 2, 0)
        self.montantsBudgetLayout.addWidget(QLabel(str(montantRevenuOuDette)), 2, 1)
        self.montantsBudgetLayout.addWidget(QLabel(''), 0, 2)

    def afficherTotauxReels(self):
        self.montantsBudgetLayout.addWidget(QLabel('Total réel des revenus'), 0, 3)
        self.montantsBudgetLayout.addWidget(QLabel(str(self.montantRevenuReel)), 0, 4)
        self.montantsBudgetLayout.addWidget(QLabel('Total réel des dépenses'), 1, 3)
        self.montantsBudgetLayout.addWidget(QLabel(str(self.montantDepenseReelle)), 1, 4)

        montantRevenuOuDette = self.montantRevenuReel - self.montantDepenseReelle
        if montantRevenuOuDette >= 0:
            revenuOuDette = 'Total réel des économies'
        else:
            revenuOuDette = 'Total réel des pertes'
        self.montantsBudgetLayout.addWidget(QLabel(revenuOuDette), 2, 3)
        self.montantsBudgetLayout.addWidget(QLabel(str(montantRevenuOuDette)), 2, 4)

    def chargerBudget(self):
        infoLayout = QGridLayout()

        noColonne = 0
        noLigne = 0
        oldNoSection = -1
        for noSection in range(0, 5):
            for ligne in self.b.budget_Prevu:
                for reel in self.b.budget_Reel:
                    if reel['ligneBudget'] == ligne['ligneBudget']:
                        montantReel = reel['montantReel']
                        break

                if ligne['noSectionBudget'] == noSection:
                    nomSection = ''
                    for section in self.b.budget_nomSection:
                        # Le but ici est de seulement trouver le titre de la section
                        if section['noSectionBudget'] == noSection:
                            nomSection = section['nomSection']
                            break

                    # TODO: Modifier la taille
                    if noLigne == 0:
                        infoLayout.addWidget(QLabel('Transactions'), noLigne, 1 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                        infoLayout.addWidget(QLabel('Montant prévu'), noLigne, 2 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                        infoLayout.addWidget(QLabel('Montant réel'), noLigne, 3 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                        noLigne += 1

                    if oldNoSection != noSection:
                        if oldNoSection != -1 and noLigne > 1:
                            infoLayout.addWidget(QLabel(''))
                            noLigne += 1
                        oldNoSection = noSection
                        infoLayout.addWidget(QLabel(nomSection), noLigne, 0 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                        noLigne += 1

                    infoLayout.addWidget(QLabel(str(ligne['nomTypeBudget'])), noLigne, 1 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                    montantPrevu = ligne['montantPrevu']
                    if self.b.codeUtilisateur == 'Dany':
                        if ligne['ligneBudget'] == 3:  # Factures communes - De Diane
                            montantPrevu = self.montantFactureCommune
                    infoLayout.addWidget(QLabel(str(montantPrevu)), noLigne, 2 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                    # TODO: Remplacer montantPrevu par montantReel
                    infoLayout.addWidget(QLineEdit(str(montantReel)), noLigne, 3 + noColonne, alignment=Qt.AlignmentFlag.AlignTop)
                    noLigne += 1

        infoLayout.setVerticalSpacing(5)
        return infoLayout

    def stack2Budget(self):
        budgetLayout = QVBoxLayout()
        saisieLayout = QHBoxLayout()

        saisieLayout.addWidget(QLabel("Dépense maintenant"))
        saisieLayout.addWidget(QLabel("$ 300.00"))
        budgetLayout.addLayout(saisieLayout)
        self.stack2.setLayout(budgetLayout)


"""
C'est la classe de base du budget. Toutes les transactions possibles sont dans cette classe.
Les informations de chaque transaction sont dans cette classe.
"""
class Budget:
    def __init__(self):
        super().__init__()
        self.budget_Prevu = []
        self.budget_Reel = []
        self.budget_Periode = []
        self.budget_Annee = []
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
        requete = "SELECT anneeBudget " \
                  "FROM " \
                  "    annee"
        if g_connexionSql.executerRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                nouvelleLigne = ligneSQL.value("anneeBudget")
                self.budget_Annee.append(nouvelleLigne)
                ligneSQL = g_connexionSql.lireEnr()

        requete = "SELECT noPeriode, nomPeriode, dateDebutPeriode, dateFinPeriode, jourDebutPeriode, jourFinPeriode " \
                  "FROM " \
                  "    periode " \
                  "WHERE " \
                  f"    anneeBudget = '{self.anneeBudget}' " \
                  f"ORDER BY " \
                  f"   anneeBudget, " \
                  f"   noPeriode"

        if g_connexionSql.executerRequete(requete):
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

    def lireSectionBudget(self):
        requete = "SELECT * " \
                  "FROM " \
                  "    sectionBudget"

        if g_connexionSql.executerRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                nouvelleSection = {'noSectionBudget': ligneSQL.value('noSectionBudget'), 'nomSection': ligneSQL.value('nomSection')}
                self.budget_nomSection.append(nouvelleSection)

                ligneSQL = g_connexionSql.lireEnr()

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

    def lireBudget(self):
        self.lireBudgetPrevu()
        self.cumulerTotalParSectionBudget()
        self.lireBudgetReel()

    def lireBudgetPrevu(self):
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

        if g_connexionSql.executerRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
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
                    self.budget_Prevu.append(nouvelleLigne)
                ligneSQL = g_connexionSql.lireEnr()
        else:
            print("Budget prévu - Fonctionne pas")

    def lireBudgetReel(self):
        isBudgetExist = False
        requete = f"SELECT budget.ligneBudget, type_budget.nomTypeBudget, budget.montantReel, budget.noPeriode, type_budget.noSectionBudget " \
                  f"FROM " \
                  f"    budget " \
                  f"JOIN type_budget ON " \
                  f"    type_budget.codeUtilisateur = '{self.codeUtilisateur}' AND " \
                  f"    type_budget.ligneBudget = budget.ligneBudget " \
                  f"WHERE " \
                  f"    budget.anneeBudget = '{self.anneeBudget}' AND " \
                  f"    budget.codeUtilisateur = '{self.codeUtilisateur}' AND " \
                  f"    budget.noPeriode = {self.noPeriodeBudget} " \
                  f"ORDER BY " \
                  f"   budget.ligneBudget"
        if g_connexionSql.executerRequete(requete):
            ligneSQL = g_connexionSql.lireEnr()
            while ligneSQL:
                isBudgetExist = True
                nouvelleLigne = {"ligneBudget"    : ligneSQL.value("budget.ligneBudget"),
                                 "nomTypeBudget"  : ligneSQL.value("type_budget.nomTypeBudget"),
                                 "montantReel"    : ligneSQL.value("budget.montantReel"),
                                 "noPeriode"      : ligneSQL.value("budget.noPeriode"),
                                 "noSectionBudget": ligneSQL.value("type_budget.noSectionBudget")
                                 }
                self.budget_Reel.append(nouvelleLigne)

                ligneSQL = g_connexionSql.lireEnr()
        else:
            print("Budget réel - Fonctionne pas")

        if not isBudgetExist:
            requete = "INSERT INTO " \
                      "    budget " \
                      "        (ligneBudget, " \
                      "         anneeBudget, " \
                      "         codeUtilisateur, " \
                      "         montantReel, " \
                      "         noPeriode) " \
                      f"SELECT " \
                      f"    ligneBudget, " \
                      f"    {self.anneeBudget}, " \
                      f"    '{self.codeUtilisateur}', " \
                      f"    0, " \
                      f"    {self.noPeriodeBudget} " \
                      "FROM " \
                      "     type_budget " \
                      f"WHERE " \
                      f"    codeUtilisateur = '{self.codeUtilisateur}' " \
                      f"ORDER BY " \
                      f"    ligneBudget"
            if g_connexionSql.executerRequete(requete):
                self.lireBudgetReel()

    def cumulerTotalParSectionBudget(self):
        noSectionBudget = 0
        montantTotalSection = 0

        for tx in self.budget_Prevu:
            if noSectionBudget != tx['noSectionBudget']:
                if self.jourDansPeriode(int(tx["jourPaiement"])) or tx["jourPaiement"] == 0:
                    section = {'noSectionBudget': noSectionBudget, 'montantTotalPrevu': montantTotalSection, 'factureCommune': tx['factureCommune']}
                    montantTotalSection = tx['montantPrevu']
                    self.totalParSection.append(section)
                    noSectionBudget = tx['noSectionBudget']
            else:
                if self.jourDansPeriode(int(tx["jourPaiement"])) or tx["jourPaiement"] == 0:
                    montantTotalSection += tx["montantPrevu"]
                    if tx["noSectionBudget"] == 0:
                        self.totalPrevuPeriode += tx["montantPrevu"]
                    else:
                        self.totalPrevuPeriode -= tx["montantPrevu"]


def main():
    b = Budget()

    nomBD = "/Users/danydesrosiers/Library/Mobile " \
            "Documents/com~apple~CloudDocs/Budget/budget.sqlite3"
    if g_connexionSql.ouvrirBD(nomBD):

        qp = QPalette()
        # qp.setColor(QPalette.Window, Qt.darkBlue)

        app = QApplication(sys.argv)

        b.lirePeriodeBudget()
        b.lireSectionBudget()
        b.lireBudget()

        app.setPalette(qp)
        app.setStyle('Fusion')
        ex = AfficherBudget(b)

        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == '__main__':
    main()
