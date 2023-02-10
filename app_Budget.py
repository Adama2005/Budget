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

# import PySide6
import pandas
import math

g_LabelSection = {}
g_CheckBox_ListeSaisieManuelle = {}
g_LabelLigneBudget = {}
g_InformationsMontantSaisi = {}
g_LineEdit = {}

g_AnneeBudget = 2023
g_UtilisateurBudget = "Dany"
g_NoPeriodeBudget = 1
g_DateDebutPeriode = ''
g_DateFinPeriode = ''

g_SQLQuery = []
g_nbQueryOuverte = -1

class LineEdit(QLineEdit):
    def mouseDoubleClickEvent(self, event):
        informationsMontantSaisi = self.objectName().split(",")
        ChoisirChargementTxOuAfficherTx(informationsMontantSaisi)


class ChoisirChargementTxOuAfficherTx(QMainWindow):
    def __init__(self, informations_montant_saisi):
        super().__init__()

        self.Tx = self
        self.windowTx = AfficherTransactionsCellule(informations_montant_saisi)

        self.windowTx.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.windowTx.show()


def chercher_ligneBudget_DansTableTransactions(nom_tx, date_tx, est_depense, liste_dates_periodes):
    global g_nbQueryOuverte, g_SQLQuery

    noPeriode = -1
    txExisteDeja = False

    for info_periode in liste_dates_periodes:
        if info_periode[1] <= date_tx <= info_periode[2]:
            noPeriode = info_periode[0]
            break

    nomRecherche = nom_tx
    index = nom_tx.find('#')
    if index >= 0:
        nomRecherche = nom_tx[:index-1]

    requete = f"SELECT " \
              f"    ligneBudget, " \
              f"    noPeriode, " \
              f"    dateTx " \
              f"FROM " \
              f"    transactions " \
              f"WHERE " \
              f"    anneeBudget = {g_AnneeBudget} AND " \
              f"    nomTx like '{nomRecherche}%' AND " \
              f"    codeUtilisateur = '{g_UtilisateurBudget}' AND " \
              f"    ligneBudget <> 20 " \
              f"ORDER " \
              f"    BY dateTx DESC"

    if est_depense:
        ligneBudget = 20   # Dépenses personnelles
    else:
        ligneBudget = 1    # Paie GRICS

    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            if g_SQLQuery[g_nbQueryOuverte].value('noPeriode') == int(g_NoPeriodeBudget):
                txExisteDeja = True
                noPeriode = g_SQLQuery[g_nbQueryOuverte].value('noPeriode')
                ligneBudget = g_SQLQuery[g_nbQueryOuverte].value('ligneBudget')

    return txExisteDeja, ligneBudget, noPeriode


def ajouterTx_DansTableTransactions(ligne_budget, no_periode, nom_tx, date_tx, depense_tx, revenu_tx):
    global g_nbQueryOuverte, g_SQLQuery

    requete = "INSERT INTO " \
              "    transactions " \
              "    (ligneBudget, " \
              "     anneeBudget, " \
              "     codeUtilisateur, " \
              "     nomTx, " \
              "     noPeriode, " \
              "     dateTx, " \
              "     depenseTx, " \
              "     revenuTx) " \
              "VALUES " \
             f"    ({ligne_budget}, " \
             f"    {g_AnneeBudget}, " \
             f"   '{g_UtilisateurBudget}', " \
             f"   '{nom_tx}', " \
             f"    {no_periode}, " \
             f"   '{date_tx}', " \
             f"    {depense_tx}, " \
             f"    {revenu_tx}) " \
             "ON CONFLICT " \
             "    (ligneBudget, " \
             "     anneeBudget, " \
             "     codeUtilisateur, " \
             "     nomTx, " \
             "     noPeriode, " \
             "     dateTx, " \
             "     depenseTx, " \
             "     revenuTx) " \
             "DO NOTHING"

    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if not g_SQLQuery[g_nbQueryOuverte].exec(requete):
        print("Insertion impossible dans la table 'transactions'")


def calculerMontant(ligne_budget, maj_ligne_budget=False):
    global g_CheckBox_ListeSaisieManuelle, g_NoPeriodeBudget, g_LineEdit, g_nbQueryOuverte, g_SQLQuery

    montantTxFormat = ""
    montantDepenseTx = 0
    montantRevenuTx = 0

    requete = f"SELECT " \
              f"    SUM(depenseTx) as total_depenseTx, " \
              f"    SUM(revenuTx) as total_revenuTx " \
              f"FROM " \
              f"    transactions " \
              f"WHERE " \
              f"    codeUtilisateur = '{g_UtilisateurBudget}' AND " \
              f"    anneeBudget = {g_AnneeBudget} AND " \
              f"    ligneBudget = {ligne_budget} AND " \
              f"    noPeriode = {g_NoPeriodeBudget} " \
              f"ORDER BY " \
              f"    dateTx DESC"
    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            montantDepenseTx = g_SQLQuery[g_nbQueryOuverte].value('total_depenseTx')
            montantRevenuTx = g_SQLQuery[g_nbQueryOuverte].value('total_revenuTx')

        montantTx = montantDepenseTx
        if montantRevenuTx > montantDepenseTx:
            montantTx = montantRevenuTx

        montantTxFormat = '0.00'
        if montantTx != '':
            montantInt = "{montantSansFormat:.2f}"
            montantTxFormat = montantInt.format(montantSansFormat=(montantTx / 100))

    if maj_ligne_budget:
        g_LineEdit[ligne_budget].setText(montantTxFormat)
    return montantTxFormat


def ouvrirBaseDonnees(fenetre_principale):
    # Create the connection
    connecteur = QSqlDatabase.addDatabase("QSQLITE")
    connecteur.setDatabaseName("/Users/danydesrosiers/Library/Mobile "
                               "Documents/com~apple~CloudDocs/Budget/budget.sqlite3")

    # Try to open the connection and handle possible errors
    if not connecteur.open():
        QMessageBox.critical(
                             fenetre_principale,
                             "Budget - Erreur!",
                             "Database Erreur: %s" % connecteur.lastError().databaseText(),
                             )
        sys.exit(1)
    return connecteur


def lirePeriodes():
    global g_nbQueryOuverte, g_SQLQuery

    listePeriodes = []
    periodes = []
    listeDatesParPeriode = []

    requete = "SELECT " \
              "    noPeriode, " \
              "    nomPeriode, " \
              "    dateDebutPeriode, " \
              "    dateFinPeriode " \
              "FROM " \
              "    periode " \
              "WHERE " \
             f"    anneeBudget = {g_AnneeBudget}"

    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            listePeriodes.append(g_SQLQuery[g_nbQueryOuverte].value('nomPeriode'))
            periodes.append(g_SQLQuery[g_nbQueryOuverte].value('noPeriode'))
            infoPeriode = [g_SQLQuery[g_nbQueryOuverte].value('noPeriode'),
                           str(g_SQLQuery[g_nbQueryOuverte].value('dateDebutPeriode')),
                           str(g_SQLQuery[g_nbQueryOuverte].value('dateFinPeriode'))]
            listeDatesParPeriode.append(infoPeriode)

    return listePeriodes, periodes, listeDatesParPeriode


def lireTousLesUtilisateurs():
    global g_AnneeBudget, g_UtilisateurBudget, g_NoPeriodeBudget, g_nbQueryOuverte, g_SQLQuery

    dernierCodeUtilisateur = 0
    requete = f"SELECT " \
              f"    dernierCodeUtilisateur " \
              f"FROM " \
              f"    donneesApplicatives"

    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            g_UtilisateurBudget = g_SQLQuery[g_nbQueryOuverte].value(dernierCodeUtilisateur)

    if not g_UtilisateurBudget:
        g_UtilisateurBudget = 'Dany'

    listeUtilisateur = []

    requete = "SELECT " \
              "    codeUtilisateur, " \
              "    anneeUtilisateur, " \
              "    noPeriodeUtilisateur " \
              "FROM " \
              "    utilisateur " \
              "ORDER BY " \
              "codeUtilisateur"

    utilisateurTrouve = False
    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            utilisateurTrouve = True
            listeUtilisateur.append(g_SQLQuery[g_nbQueryOuverte].value('codeUtilisateur'))

            if g_SQLQuery[g_nbQueryOuverte].value('codeUtilisateur') == g_UtilisateurBudget:
                g_AnneeBudget = g_SQLQuery[g_nbQueryOuverte].value('anneeUtilisateur')
                g_NoPeriodeBudget = g_SQLQuery[g_nbQueryOuverte].value('noPeriodeUtilisateur')

    if not utilisateurTrouve:
        # Aller lire dans la table utilisateur à la place
        listeUtilisateur.append('Dany')
        listeUtilisateur.append('Diane')
        g_AnneeBudget = 2023
        g_NoPeriodeBudget = 1

    return listeUtilisateur


def lireAnneesBudget():
    global g_nbQueryOuverte, g_SQLQuery

    listeAnnees = []


    requete = "SELECT DISTINCT " \
              "    anneeBudget " \
              "FROM " \
              "    periode " \
              "ORDER BY " \
              "    anneeBudget, " \
              "    noPeriode" \

    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            listeAnnees.append(str(g_SQLQuery[g_nbQueryOuverte].value('anneeBudget')))

    return listeAnnees


def lireSectionBudget():
    global g_nbQueryOuverte, g_SQLQuery

    listeSection = []

    requete = "SELECT " \
              "    nomSection " \
              "FROM " \
              "    sectionBudget"
    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            listeSection.append(g_SQLQuery[g_nbQueryOuverte].value('nomSection'))

    return listeSection


def lireVersionBudget():
    global g_nbQueryOuverte, g_SQLQuery

    versionBudget = []

    requete = "SELECT DISTINCT " \
              "    version " \
              "FROM " \
              "    type_budget " \
              "WHERE " \
             f"    codeUtilisateur = '{g_UtilisateurBudget}'"
    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if g_SQLQuery[g_nbQueryOuverte].exec(requete):
        while g_SQLQuery[g_nbQueryOuverte].next():
            versionBudget.append(str(g_SQLQuery[g_nbQueryOuverte].value('version')))

    return versionBudget


def ecrireDonneesApplicatives(fenetre_principale):
    global g_nbQueryOuverte, g_SQLQuery

    requete = f"UPDATE " \
              f"    donneesApplicatives " \
              f"SET " \
              f"    dernierCodeUtilisateur = '{g_UtilisateurBudget}'"
    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if not g_SQLQuery[g_nbQueryOuverte].exec(requete):
        QMessageBox.critical(fenetre_principale,
                             "Budget - Données applicatives",
                             "Budget - Sauvegarde du dernier utilisateur"
                             "\n\nErreur lors de la sauvegarde. "
                             f"\n\nErreur : {g_SQLQuery[g_nbQueryOuverte].lastError().text()}"
                             f"\n\nRequête : \n{requete}"
                             )

    requete = f"UPDATE " \
              f"    utilisateur " \
              f"SET " \
              f"    anneeUtilisateur = '{g_AnneeBudget}', " \
              f"    noPeriodeUtilisateur = '{g_NoPeriodeBudget}' " \
              f"    WHERE codeUtilisateur = '{g_UtilisateurBudget}'"
    g_nbQueryOuverte += 1
    g_SQLQuery.append(g_nbQueryOuverte)
    g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    if not g_SQLQuery[g_nbQueryOuverte].exec(requete):
        QMessageBox.critical(fenetre_principale,
                             "Budget - Données applicatives",
                             "Budget - Sauvegarde des Données applicatives"
                             "\n\nErreur lors de la sauvegarde. "
                             f"\n\nErreur : {g_SQLQuery[g_nbQueryOuverte].lastError().text()}"
                             f"\n\nRequête : \n{requete}"
                             )
        sys.exit(2)


def trouverSiPaiementDuDansPeriode(calculer_montant_du, jour_du_paiement, jour_debut_periode,
                                   jour_fin_periode):
    paiementDu = False
    if jour_du_paiement > 0:
        # Vérifier si le paiement doit se faire entre la date de début et de fin de la période
        if jour_debut_periode <= jour_du_paiement <= jour_fin_periode:
            paiementDu = True
        else:
            if jour_debut_periode >= jour_fin_periode:
                if jour_du_paiement <= jour_fin_periode or jour_du_paiement >= jour_debut_periode:
                    paiementDu = True
    else:
        # Si le jour du paiement est 0, c'Est parce que c'est un montant à payer qui n'est pas dans les factures
        # communes, c'est pour ça
        if not calculer_montant_du:
            paiementDu = True

    return paiementDu


"""
Module sauverMontantFacturesCommunes: 

Cette fonction permet d'ajouter la part du montant des factures que Diane doit donner à Dany, pour 
qu'il puisse faire le paiement des factures.
"""
def sauverMontantFacturesCommunes(montant_pour_diane):
    global g_nbQueryOuverte, g_SQLQuery

    if g_UtilisateurBudget == "Dany":
        requete = f"UPDATE " \
                  f"    type_budget " \
                  f"SET " \
                  f"    montantPrevu = {montant_pour_diane} " \
                  f"WHERE " \
                  f"    ligneBudget = 50 AND " \
                  f"    codeUtilisateur = 'Diane' AND " \
                  f"    noSectionBudget = 3"
        g_nbQueryOuverte += 1
        g_SQLQuery.append(g_nbQueryOuverte)
        g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
        g_SQLQuery[g_nbQueryOuverte].prepare(requete)
        if not g_SQLQuery[g_nbQueryOuverte].exec(requete):
            print("Erreur sauverMontantFacturesCommunes")


"""
Fonction cumulerTotauxParSection: 

Cette fonction permet de cumuler les totaux prévus et réels pour chaque section du budget. Ce qui va permettre 
de détecter les sections où il y a trop de dépenses. 
"""
def cumulerTotauxParSection():
    global g_LabelSection

    montantTotalParSection = []

    for ligneTotal in g_LabelLigneBudget:
        informationsLigne = []
        if g_LineEdit[ligneTotal]:
            informationsLigne = g_LineEdit[ligneTotal].objectName().split(",")

        sectionTotal = informationsLigne[0]
        calculerMontant(ligneTotal)

        paiementDu = (informationsLigne[2] == 'True')
        montantPrevuParSection = 0
        montantReelParSection = 0
        if paiementDu:
            montantPrevuParSection = int(float(informationsLigne[5]) * 10 * 10)
            montantReelParSection = int(float(informationsLigne[6]) * 10 * 10)

        sectionPrevueTrouvee = False
        for totalParSection in montantTotalParSection:
            if totalParSection['section'] == sectionTotal:
                sectionPrevueTrouvee = True
                totalParSection['montantTotalPrevu'] += montantPrevuParSection
                totalParSection['montantTotalReel'] += montantReelParSection

        if not sectionPrevueTrouvee:
            nouvelleSection = {'section': sectionTotal,
                               'montantTotalPrevu': int(montantPrevuParSection),
                               'montantTotalReel': int(montantReelParSection)}
            montantTotalParSection.append(nouvelleSection)

    for montant in montantTotalParSection:
        montantInt = "{montantSansFormat:.2f}"
        montantPrevuEnDollars = montantInt.format(montantSansFormat=(montant['montantTotalPrevu'] / 100))
        montantReelEnDollars = montantInt.format(montantSansFormat=(montant['montantTotalReel'] / 100))

        titreSection = f"{montant['section']}    ${montantReelEnDollars} / " \
                       f"${montantPrevuEnDollars}"
        g_LabelSection[montant['section']].setText(titreSection)


def quitterBudget(fenetre_principale):
    quitter = QMessageBox.question(fenetre_principale,
                                   "QUITTER",
                                   "Êtes-vous certain de vouloir quitter?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                   )
    return quitter


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fenetre_principale = self
        self.connecteurSQL = QSqlDatabase

        self.title = "Budget"
        self.setWindowTitle(self.title, )

        self.readSettings()

        connexion = ouvrirBaseDonnees(self.fenetre_principale)
        self.connecteurSQL = connexion

        self.budget_widget = Budget_Widget(self, self.connecteurSQL, self.fenetre_principale)
        self.setCentralWidget(self.budget_widget)
        self.show()

    def readSettings(self):
        settings = QSettings("Budget", "Position fenêtre Budget")
        pos = settings.value("pos", QPoint(0, 0))
        size = settings.value("size", QSize(700, 300))

        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QSettings("Budget", "Position fenêtre Budget")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    def closeEvent(self, event):
        # self.labelMessage.setText("")
        self.quitterAppBudgetAvecEvent(event, self.connecteurSQL, self.fenetre_principale)

    @staticmethod
    def quitterAppBudgetAvecEvent(event, connecteur_sql, fenetre_principale):
        quitter = quitterBudget(fenetre_principale)
        if quitter == QMessageBox.StandardButton.Yes:
            event.accept()
            fenetre_principale.writeSettings()
            ecrireDonneesApplicatives(fenetre_principale)
            connecteur_sql.close()
            sys.exit()
        else:
            event.ignore()


# def EffacerMontantReelBudget():
#     global g_nbQueryOuverte, g_SQLQuery
#
#     requete = f"UPDATE " \
#               f"    budget " \
#               f"SET " \
#               f"    montantReel = 0 " \
#               f"WHERE " \
#               f"    anneeBudget = {g_AnneeBudget} AND " \
#               f"    codeUtilisateur = '{g_UtilisateurBudget}' AND " \
#               f"    saisieManuellement = 0"
#     g_nbQueryOuverte += 1
#     g_SQLQuery.append(g_nbQueryOuverte)
#     g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
#     g_SQLQuery[g_nbQueryOuverte].prepare(requete)
#     if not g_SQLQuery[g_nbQueryOuverte].exec(requete):
#         print("Problème avec la remise à zéro du 'montantReel' de la 'table budget'")


def chargerTransactionsFichier(liste_dates_periodes):
    import os.path
    from os import path

    fichierUtilisateur = f"tx{g_UtilisateurBudget}.xlsx"
    fichierValide = False

    # EffacerMontantReelBudget()
    # MAJ_montantReel_dans_BD()

    if path.exists(fichierUtilisateur):
        fichierValide = True
        data = pandas.read_excel(fichierUtilisateur)
        df = pandas.DataFrame(data, columns=['dateTx', 'nomTx', 'depenseTx', 'revenuTx', 'nomTypeBudget'])
        for i in df.index:
            estDepense = False
            nomTx = df['nomTx'][i].replace("'", "''")
            dateTx = df['dateTx'][i]
            dateTxString = str(dateTx).replace('-', '')[0:8]
            depenseTx = df['depenseTx'][i]
            revenuTx = df['revenuTx'][i]

            if dateTxString[0:4] == g_AnneeBudget:
                if isinstance(depenseTx, str):
                    depenseTx = df['depenseTx'][i]
                    depenseTx = ud.normalize('NFKD', depenseTx).replace(' ', '').replace(',', '.')
                    depenseTx = depenseTx.replace('\u2212', '-')
                    depenseTx = int(float(depenseTx) * 10 * 10)
                    estDepense = True
                else:
                    if math.isnan(df['depenseTx'][i]):
                        depenseTx = int(float(0) * 10 * 10)
                    else:
                        # depenseTX est de type Float
                        depenseTx = int(depenseTx * 10 * 10)
                        estDepense = True

                # revenuTx = df['revenuTx'][i]
                if isinstance(revenuTx, str):
                    revenuTx = ud.normalize('NFKD', revenuTx).replace(' ', '').replace(',', '.')
                    revenuTx = int(float(revenuTx) * 10 * 10)
                else:
                    if math.isnan(df['revenuTx'][i]):
                        revenuTx = int(float(0) * 10 * 10)
                    else:
                        # revenuTX est de type Float
                        revenuTx = int(revenuTx * 10 * 10)

                # Chercher dans la table de correspondance
                infosLigneBudget = chercher_ligneBudget_DansTableTransactions(nomTx, dateTxString, estDepense,
                                                                              liste_dates_periodes)
                if not infosLigneBudget[0]:
                    ajouterTx_DansTableTransactions(infosLigneBudget[1], infosLigneBudget[2], nomTx, dateTx,
                                                    depenseTx, revenuTx)
    return fichierValide


"""
Class Budget_Widget: 

Cette fonction crée le layout nécessaire pour encadrer les données qui seront affichées 
pour permettre de faire un budget pour un utilisateur, une année et une période de l'année.
"""


class Budget_Widget(QWidget):
    def __init__(self, parent, connecteur_sql, fenetre_principale):
        super().__init__(parent)
        self.fenetre_principale = fenetre_principale
        self.connecteurSQL = connecteur_sql

        self.chart_view = None
        self.chart = None
        self.slice = None

        self.series = None
        self.w = None

        self.listePeriodes = []
        self.listeDatesPeriodes = []

        self.Ind_NomPeriode = 0
        self.Ind_NoPeriode = 1

        self.pos_Prevu = 0
        self.pos_JourDebut = 1
        self.pos_JourFin = 2
        self.pos_JourPaiement = 3
        self.pos_LigneBudget = 4
        self.pos_MontantTotalFacturesCommunes = 5
        self.pos_InfoCachee = 6

        self.afficherLignesCacheesBudget = False

        self.listeAnnees = []
        self.quelBouton = None

        self.layoutPrincipal = QVBoxLayout()
        self.layoutPrincipalButton = QVBoxLayout()

        self.layoutTop = QHBoxLayout()
        self.layoutTopGauche = QFormLayout()
        self.layoutTopCentre = QFormLayout()
        self.layoutTopDroit = QFormLayout()
        self.layoutBudget = QHBoxLayout()
        self.gridBudget = QGridLayout()

        self.layoutSommaire = QHBoxLayout()
        self.gridSommaire = QGridLayout()

        # Peut-être ajout pour le graphique dans Sommaire

        self.boutonStat = QPushButton("Statistiques")
        self.labelMessage = QLabel('')
        self.boutonCache = QPushButton("C")
        self.boutonSauvegarder = QPushButton("Sauvegarder")
        self.boutonQuitter = QPushButton("Quitter")
        self.sectionsBudget = []

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabBudget = QWidget()
        self.tabSommaire = QWidget()
        self.tabs.TabPosition(1)

        # Ajouter les utilisateurs dans l'interface, provenant de la BD
        self.comboUtilisateurs = QComboBox()
        self.listeUtilisateurs = lireTousLesUtilisateurs()
        self.comboUtilisateurs.addItems(self.listeUtilisateurs)
        self.comboUtilisateurs.setCurrentIndex(self.listeUtilisateurs.index(g_UtilisateurBudget))
        self.comboUtilisateurs.activated.connect(self.onActivated_Utilisateur)

        # Ajouter les années dans l'interface, provenant de la BD
        self.comboAnnees = QComboBox()
        self.listeAnnees = lireAnneesBudget()
        self.comboAnnees.addItems(self.listeAnnees)
        self.comboAnnees.setCurrentIndex(self.listeAnnees.index(str(g_AnneeBudget)))
        self.comboAnnees.activated.connect(self.onActivated_Annee)

        # Ajouter les utilisateurs dans l'interface, provenant de la BD
        self.comboPeriodes = QComboBox()
        self.listePeriodes = lirePeriodes()
        self.listeDatesPeriodes = self.listePeriodes[2]
        self.comboPeriodes.addItems(self.listePeriodes[self.Ind_NomPeriode])
        self.comboPeriodes.setCurrentIndex(self.listePeriodes[self.Ind_NoPeriode].index(int(g_NoPeriodeBudget)))
        self.comboPeriodes.activated.connect(self.onActivated_Periode)

        self.tabs.resize(self.width(), self.height())
        self.creationLayoutBudget()
        self.afficherBudget()

    def afficherBudget(self):
        global g_CheckBox_ListeSaisieManuelle, g_LineEdit, g_LabelLigneBudget

        noSection = 0
        noLigne = 0
        ligne = 0
        noColonne = 0
        noVersion = 0
        montantTotalFacturesCommunes = 0
        g_LabelLigneBudget = {}

        self.effacerTousLesSousLayout()
        fichierTransactionsValide = chargerTransactionsFichier(self.listeDatesPeriodes)

        versionBudget = 0
        version_Budget = lireVersionBudget()
        if version_Budget:
            versionBudget = version_Budget[noVersion]

            informations_Budget = self.lireBudget(3, versionBudget)
            if informations_Budget:
                montantFacturesCommunes = informations_Budget[self.pos_MontantTotalFacturesCommunes]
                if montantFacturesCommunes > 0:
                    montantInt = "{montantSansFormat:.2f}"
                    montantEnDollars = montantInt.format(montantSansFormat=(montantFacturesCommunes / 100) / 2)
                    montantTotalFacturesCommunes = montantEnDollars
                    sauverMontantFacturesCommunes(montantFacturesCommunes / 2)

        for section in self.sectionsBudget:
            if section != 'Sommaire':
                informations_Budget = self.lireBudget(noSection, versionBudget)
                if informations_Budget:
                    listeMontantsPrevus = informations_Budget[self.pos_Prevu]
                    # listeMontantsReels = informations_Budget[self.pos_Reel]
                    listeJourDebutPeriode = informations_Budget[self.pos_JourDebut]
                    listeJourFinPeriode = informations_Budget[self.pos_JourFin]
                    listeJoursPaiements = informations_Budget[self.pos_JourPaiement]
                    listeLignesBudget = informations_Budget[self.pos_LigneBudget]
                    listeInfoCachee = informations_Budget[self.pos_InfoCachee]

                    g_LabelSection[section] = QLabel(f"{section}")

                    if noLigne >= 15 and noColonne == 0:
                        ligne = 0
                        noColonne = 5

                    if ligne == 0:
                        self.gridBudget.addWidget(g_LabelSection[section], ligne, 0 + noColonne,
                                                  alignment=Qt.AlignmentFlag.AlignTop)
                    else:
                        self.gridBudget.addWidget(g_LabelSection[section], ligne, 0 + noColonne)
                    self.gridBudget.addWidget(QLabel("Banque"), ligne, 1 + noColonne)

                    ligne += 1

                    for nomTx in listeMontantsPrevus:
                        g_LabelLigneBudget[listeLignesBudget[nomTx]] = QLabel(f"{' ':>20}{nomTx}")
                        toolTip = f"Ligne du budget : {listeLignesBudget[nomTx]}"
                        if listeJoursPaiements[nomTx] != '0':
                            toolTip += f"\nJour du paiement : {listeJoursPaiements[nomTx]}"

                        g_LabelLigneBudget[listeLignesBudget[nomTx]].setToolTip(toolTip)


                        paiementDu = True
                        if listeJoursPaiements[nomTx] > '0':
                            paiementDu = trouverSiPaiementDuDansPeriode(True,
                                                                        int(listeJoursPaiements[nomTx]),
                                                                        int(listeJourDebutPeriode[nomTx]),
                                                                        int(listeJourFinPeriode[nomTx]))
                        if not paiementDu:
                            g_LabelLigneBudget[listeLignesBudget[nomTx]].setStyleSheet("color: grey")
                        toolTip = ""

                        if listeLignesBudget[nomTx] == "3":  # Factures communes
                            montantPrevu = str(montantTotalFacturesCommunes)
                        else:
                            montantPrevu = listeMontantsPrevus[nomTx]

                        montantTransactions = calculerMontant(listeLignesBudget[nomTx])
                        g_LineEdit[listeLignesBudget[nomTx]] = LineEdit(objectName=f"{section},"
                                                                                     f"{listeLignesBudget[nomTx]},"
                                                                                     f"{paiementDu},"
                                                                                     f"{nomTx},"
                                                                                     f"{listeInfoCachee[nomTx]},"
                                                                                     f"{montantPrevu},"
                                                                                     f"{montantTransactions}")
                        g_LineEdit[listeLignesBudget[nomTx]].setText(montantTransactions)
                        g_LineEdit[listeLignesBudget[nomTx]].setToolTip(f"Montant prévu au budget : "
                                                                        f"{str(montantPrevu)}")

                        if paiementDu:
                            if int(float(montantTransactions) * 10 * 10) > int(float(montantPrevu) * 10 * 10):
                                g_LineEdit[listeLignesBudget[nomTx]].setStyleSheet("color:violet")
                            else:
                                g_LineEdit[listeLignesBudget[nomTx]].setStyleSheet("color: green")
                        else:
                            g_LineEdit[listeLignesBudget[nomTx]].setStyleSheet("color: grey")

                        if listeInfoCachee[nomTx] == '1':
                            g_LabelLigneBudget[listeLignesBudget[nomTx]].setVisible(False)
                            g_LineEdit[listeLignesBudget[nomTx]].setVisible(False)
                        self.installEventFilter(self)
                        g_LineEdit[listeLignesBudget[nomTx]].setMaxLength(7)
                        g_LineEdit[listeLignesBudget[nomTx]].setReadOnly(True)

                        self.gridBudget.addWidget(g_LabelLigneBudget[listeLignesBudget[nomTx]], ligne, 0 + noColonne)
                        self.gridBudget.addWidget(g_LineEdit[listeLignesBudget[nomTx]], ligne, 1 + noColonne,
                                                  alignment=Qt.AlignmentFlag.AlignLeft)
                        g_LineEdit[listeLignesBudget[nomTx]].setFixedWidth(75)

                        noLigne += 1
                        ligne += 1

                    self.gridBudget.addWidget(QLabel(), ligne, 0 + noColonne)
                    noLigne += 1
                    ligne += 1
                else:
                    break

            noSection += 1

        if noSection > 0:
            if fichierTransactionsValide:
                cumulerTotauxParSection()

            gridDany = QVBoxLayout()
            gridDany.addWidget(QLabel('Dany'), 0, Qt.AlignmentFlag.AlignTop)
            gridDany.addWidget(QLabel('1'))
            gridDany.addWidget(QLabel('2'))
            gridDany.addWidget(QLabel('3'))
            gridDany.addWidget(QLabel('4'))
            gridDany.addWidget(QLabel('5'))
            gridDany.addWidget(QLabel('6'))


            self.layoutBudget.addLayout(self.gridBudget)
            self.layoutBudget.addLayout(gridDany)
            self.tabBudget.setLayout(self.layoutBudget)

            self.tabs.TabPosition(1)
            self.layoutPrincipal.addWidget(self.tabs)

            # Pour être certain que les boutons Sauvegarder et Quitter s'affiche à droite de la fenêtre
            layoutBouton = QGridLayout()
            layoutBouton.addWidget(self.boutonStat, 0, 0)
            layoutBouton.addWidget(QLabel(), 0, 1)
            layoutBouton.addWidget(QLabel(), 0, 2)
            layoutBouton.addWidget(self.labelMessage, 0, 3)
            layoutBouton.addWidget(self.boutonCache, 0, 4)
            # layoutBouton.addWidget(self.boutonSauvegarder, 0, 5)
            layoutBouton.addWidget(self.boutonQuitter, 0, 5)

            self.layoutPrincipalButton.addLayout(layoutBouton)
            self.layoutPrincipal.addLayout(self.layoutPrincipalButton)
            self.setLayout(self.layoutPrincipal)
        else:
            QMessageBox.information(self.fenetre_principale,
                                    "",
                                    f"L'utilisateur {self.utilisateur} n'a aucune donnée pour faire un budget",
                                    )


    """
    Module lireBudget: 

    Cette fonction lit le budget de l'utilisateur pour l'année et la période sélectionnées. Ce budget lu pourra 
    être affiché par la suite.
    """
    def lireBudget(self, no_section, version_budget):
        global g_nbQueryOuverte, g_SQLQuery

        listeMontantsPrevus = {}
        listeMontantsReels = {}
        listeJoursPaiements = {}
        listeJourDebutPeriode = {}
        listeJourFinPeriode = {}
        listeLignesBudget = {}
        listeInfoCachee = {}

        montantTotalFacturesCommunes = 0

        requete = "SELECT " \
                  "    type_budget.nomTypeBudget, " \
                  "    type_budget.montantPrevu, " \
                  "    periode.jourDebutPeriode, " \
                  "    periode.jourFinPeriode, " \
                  "    type_budget.jourPaiement, " \
                  "    type_budget.ligneBudget, " \
                  "    type_budget.factureCommune, " \
                  "    type_budget.infoCachee " \
                  "FROM " \
                  "    type_budget " \
                  "JOIN budget ON" \
                  f"   budget.codeUtilisateur = type_budget.codeUtilisateur AND " \
                  f"   budget.anneeBudget = {g_AnneeBudget} AND " \
                  f"   budget.ligneBudget = type_budget.ligneBudget AND " \
                  f"   budget.noPeriode = {g_NoPeriodeBudget} " \
                  f"JOIN periode ON " \
                  f"   periode.anneeBudget = budget.anneeBudget AND " \
                  f"   periode.NoPeriode = budget.noPeriode " \
                  f"WHERE " \
                  f"   type_budget.codeUtilisateur = '{g_UtilisateurBudget}' AND " \
                  f"   type_budget.noSectionBudget = {no_section} AND " \
                  f"   type_budget.version = {version_budget} " \
                  f"ORDER BY " \
                  f"   type_budget.codeUtilisateur, " \
                  f"   type_budget.ligneBudget"

        budget_Trouve = False

        g_nbQueryOuverte += 1
        g_SQLQuery.append(g_nbQueryOuverte)
        g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
        g_SQLQuery[g_nbQueryOuverte].prepare(requete)
        if g_SQLQuery[g_nbQueryOuverte].exec(requete):
            while g_SQLQuery[g_nbQueryOuverte].next():
                budget_Trouve = True

                montantInt = "{montantSansFormat:.2f}"
                montantEnDollars = montantInt.format(montantSansFormat=g_SQLQuery[g_nbQueryOuverte]
                                                     .value('type_budget.montantPrevu')
                                                     / 100)
                listeMontantsPrevus[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = montantEnDollars

                # # Formater le montant réel de la BD qui est en Integer et lui ajouter les cents
                # montantInt = "{montantSansFormat:.2f}"
                # montantEnDollars = montantInt.format(montantSansFormat=g_SQLQuery[g_nbQueryOuverte]
                #                                      .value('budget.montantReel') / 100)
                # listeMontantsReels[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = montantEnDollars

                listeJourDebutPeriode[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = \
                    str(g_SQLQuery[g_nbQueryOuverte].value('periode.jourDebutPeriode'))
                listeJourFinPeriode[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = \
                    str(g_SQLQuery[g_nbQueryOuverte].value('periode.jourFinPeriode'))
                listeJoursPaiements[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = \
                    str(g_SQLQuery[g_nbQueryOuverte].value('type_budget.jourPaiement'))
                listeLignesBudget[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = \
                    str(g_SQLQuery[g_nbQueryOuverte].value('type_budget.ligneBudget'))
                if g_SQLQuery[g_nbQueryOuverte].value('type_budget.factureCommune') == 1:
                    if trouverSiPaiementDuDansPeriode(False,
                                                      int(g_SQLQuery[g_nbQueryOuverte].
                                                                  value('type_budget.jourPaiement')),
                                                      int(g_SQLQuery[g_nbQueryOuverte].
                                                                  value('periode.jourDebutPeriode')),
                                                      int(g_SQLQuery[g_nbQueryOuverte].
                                                                  value('periode.jourDebutPeriode'))
                                                      ):
                        montantTotalFacturesCommunes += g_SQLQuery[g_nbQueryOuverte].value('type_budget.montantPrevu')
                listeInfoCachee[g_SQLQuery[g_nbQueryOuverte].value('type_budget.nomTypeBudget')] = \
                    str(g_SQLQuery[g_nbQueryOuverte].value('type_budget.infoCachee'))

        if not budget_Trouve:
            # Créer le budget selon le type de budget de l'utilisateur sélectionné, l'année sélectionnée et la période
            # sélectionnée.

            requete_Insert = "INSERT INTO " \
                             "    budget " \
                             "        (ligneBudget, " \
                             "         anneeBudget, " \
                             "         codeUtilisateur, " \
                             "         montantReel, " \
                             "         noPeriode) " \
                             f"SELECT " \
                             f"    ligneBudget, " \
                             f"    {g_AnneeBudget}, " \
                             f"    '{g_UtilisateurBudget}', 0," \
                             f"    {g_NoPeriodeBudget} " \
                             "FROM " \
                             "     type_budget " \
                             f"WHERE " \
                             f"    codeUtilisateur = '{g_UtilisateurBudget}' AND " \
                             f"    noSectionBudget = {no_section} " \
                             f"ORDER BY " \
                             f"    ligneBudget"
            g_nbQueryOuverte += 1
            g_SQLQuery.append(g_nbQueryOuverte)
            g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
            g_SQLQuery[g_nbQueryOuverte].prepare(requete)
            if g_SQLQuery[g_nbQueryOuverte].exec(requete_Insert):
                informations_Budget = self.lireBudget(no_section, version_budget)
                if informations_Budget:
                    listeMontantsPrevus = informations_Budget[self.pos_Prevu]
                    # listeMontantsReels = informations_Budget[self.pos_Reel]
                    listeJourDebutPeriode = informations_Budget[self.pos_JourDebut]
                    listeJourFinPeriode = informations_Budget[self.pos_JourFin]
                    listeJoursPaiements = informations_Budget[self.pos_JourPaiement]
                    listeLignesBudget = informations_Budget[self.pos_LigneBudget]
                    montantTotalFacturesCommunes = informations_Budget[self.pos_MontantTotalFacturesCommunes]
                    listeInfoCachee = informations_Budget[self.pos_InfoCachee]

        # return listeMontantsPrevus, listeMontantsReels, listeJourDebutPeriode, listeJourFinPeriode, \
        #     listeJoursPaiements, listeLignesBudget, montantTotalFacturesCommunes, listeInfoCachee
        return listeMontantsPrevus, listeJourDebutPeriode, listeJourFinPeriode, \
            listeJoursPaiements, listeLignesBudget, montantTotalFacturesCommunes, listeInfoCachee

    # def sauverMontant(self):
    #     global g_nbQueryOuverte, g_SQLQuery
    #
    #     erreur = False
    #     for edit in self.layoutBudget.parentWidget().findChildren(QLineEdit):
    #         montantReel = edit.text()
    #         if montantReel == '':
    #             montantReel = '0'
    #
    #         sectionLigne = edit.objectName().split(",")
    #
    #         montantReelAvantSaisie = '0'
    #         if sectionLigne[6] != '':
    #             montantReelAvantSaisie = sectionLigne[6]
    #
    #         requete = f"UPDATE " \
    #                   f"    budget " \
    #                   f"SET " \
    #                   f"    montantReel = {int(float(montantReel) * 10 * 10)}, " \
    #                   f"    saisieManuellement = IIF({montantReel}!={montantReelAvantSaisie}, 1, 0) " \
    #                   f"WHERE " \
    #                   f"    codeUtilisateur = '{g_UtilisateurBudget}' AND " \
    #                   f"    anneeBudget = {g_AnneeBudget} AND " \
    #                   f"    ligneBudget = {sectionLigne[1]} AND " \
    #                   f"    noPeriode = {g_NoPeriodeBudget}"
    #         g_nbQueryOuverte += 1
    #         g_SQLQuery.append(g_nbQueryOuverte)
    #         g_SQLQuery[g_nbQueryOuverte] = QSqlQuery()
    #         g_SQLQuery[g_nbQueryOuverte].prepare(requete)
    #         if not g_SQLQuery[g_nbQueryOuverte].exec(requete):
    #             QMessageBox.critical(self.fenetre_principale,
    #                                  "Budget - Sauvegarde",
    #                                  "Budget - Sauvegarde\n\nBudget - Erreur lors de la sauvegarde!"
    #                                  f"\n\nErreur : {g_SQLQuery[g_nbQueryOuverte].lastError().text()}"
    #                                  f"\n\nRequête : \n{requete}")
    #             sys.exit(1)
    #     if not erreur:
    #         self.labelMessage.setStyleSheet("color: green")
    #         self.labelMessage.setText(f"La dernière sauvegarde du budget de {g_UtilisateurBudget} s'est bien "
    #                                   f"effectuée")

    def creationLayoutBudget(self):
        # Add tabs
        self.sectionsBudget = lireSectionBudget()
        if self.sectionsBudget[0]:
            self.tabs.addTab(self.tabBudget, "Saisir le budget")
        if self.sectionsBudget[1]:
            self.tabs.addTab(self.tabSommaire, "Sommaire")
        self.tabs.TabPosition(1)

        # Budget de qui et pour quelle période
        self.layoutTopGauche.addRow("Budget de", self.comboUtilisateurs)
        self.layoutTopCentre.addRow("Année", self.comboAnnees)
        self.layoutTopDroit.addRow("Période", self.comboPeriodes)
        self.layoutTop.addLayout(self.layoutTopGauche)
        self.layoutTop.addLayout(self.layoutTopCentre)
        self.layoutTop.addLayout(self.layoutTopDroit)
        self.layoutPrincipal.addLayout(self.layoutTop)
        self.boutonStat.clicked.connect(AfficherStat)
        self.boutonCache.clicked.connect(self.AfficherLignesCachees)
        # self.boutonSauvegarder.clicked.connect(self.sauvegarderBudget)
        self.boutonQuitter.clicked.connect(self.quitterAppBudget)
        self.boutonQuitter.setDefault(True)

    def effacerTousLesSousLayout(self):
        global g_LineEdit

        g_LineEdit = {}

        self.afficherLignesCacheesBudget = False

        self.layoutBudget.deleteLater()
        self.layoutSommaire.deleteLater()
        self.layoutPrincipalButton.deleteLater()
        self.gridBudget.deleteLater()
        self.gridSommaire.deleteLater()
        self.tabBudget.deleteLater()
        self.tabSommaire.deleteLater()
        self.tabs.deleteLater()

        self.layoutBudget = QHBoxLayout()
        self.layoutSommaire = QHBoxLayout()
        self.layoutPrincipalButton = QVBoxLayout()
        self.gridBudget = QGridLayout()
        self.gridSommaire = QGridLayout()
        self.tabs = QTabWidget()
        self.tabBudget = QWidget()
        self.tabSommaire = QWidget()

        self.sectionsBudget = lireSectionBudget()
        if self.sectionsBudget[0]:
            self.tabs.addTab(self.tabBudget, "Budget")
        if self.sectionsBudget[1]:
            self.tabs.addTab(self.tabSommaire, "Sommaire")
        self.tabs.TabPosition(1)

    def onActivated_Utilisateur(self, idx):
        global g_UtilisateurBudget

        g_UtilisateurBudget = self.listeUtilisateurs[idx]
        self.afficherBudget()

    def onActivated_Annee(self, idx):
        global g_AnneeBudget

        g_AnneeBudget = self.listeAnnees[idx]
        self.listePeriodes = lirePeriodes()
        self.comboPeriodes.clear()
        self.comboPeriodes.addItems(self.listePeriodes[self.Ind_NomPeriode])
        self.comboPeriodes.setCurrentIndex(self.listePeriodes[self.Ind_NoPeriode].index(int(g_NoPeriodeBudget)))
        self.comboPeriodes.activated.connect(self.onActivated_Periode)
        self.afficherBudget()

    def onActivated_Periode(self, idx):
        global g_NoPeriodeBudget

        g_NoPeriodeBudget = str(idx + 1)
        self.afficherBudget()

    def AfficherLignesCachees(self):
        self.afficherLignesCacheesBudget = not self.afficherLignesCacheesBudget
        for ligneTotal in g_LineEdit:
            informationsLigne = g_LineEdit[ligneTotal].objectName().split(",")
            if informationsLigne[4] == '1':
                g_LabelLigneBudget[ligneTotal].setVisible(self.afficherLignesCacheesBudget)
                g_LineEdit[ligneTotal].setVisible(self.afficherLignesCacheesBudget)

    def quitterAppBudget(self):
        self.labelMessage.setText("")
        quitter = quitterBudget(self)
        if quitter == QMessageBox.StandardButton.Yes:
            self.fenetre_principale.writeSettings()

            ecrireDonneesApplicatives(self.fenetre_principale)
            self.connecteurSQL.close()
            sys.exit()


class AfficherTransactionsCellule(QMainWindow):
    def __init__(self, informations_montant_saisi):
        super().__init__()

        self.readSettingsFenTx()

        self.setWindowTitle(f"Liste des transactions de : {informations_montant_saisi[3]}")
        self.addAction("Ok")

        self.model = QSqlTableModel(self)
        self.model.setTable("transactions")
        self.model.setFilter(f"ligneBudget = {informations_montant_saisi[1]} AND anneeBudget = {g_AnneeBudget} "
                             f"AND "
                             f"codeUtilisateur = '{g_UtilisateurBudget}' AND noPeriode = {g_NoPeriodeBudget}")
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.setHeaderData(0, Qt.Horizontal, "ligneBudget")
        self.model.setHeaderData(1, Qt.Horizontal, "anneeBudget")
        self.model.setHeaderData(2, Qt.Horizontal, "codeUtilisateur")
        self.model.setHeaderData(3, Qt.Horizontal, "nomTx")
        self.model.setHeaderData(4, Qt.Horizontal, "noPeriode")

        self.model.setHeaderData(5, Qt.Horizontal, "Dany")
        self.model.setHeaderData(6, Qt.Horizontal, "revenuTx")
        self.model.setHeaderData(7, Qt.Horizontal, "dateTx")
        self.model.select()

        self.model.setHeaderData(0, Qt.Horizontal, "Type de transaction")
        self.model.setHeaderData(3, Qt.Horizontal, "Nom de la transaction")
        self.model.setHeaderData(5, Qt.Horizontal, "Dépense")
        self.model.setHeaderData(6, Qt.Horizontal, "Revenu")
        self.model.setHeaderData(7, Qt.Horizontal, "Date de la transaction")
        # Set up the view
        self.view = QTableView()
        self.view.setShowGrid(True)
        self.view.setModel(self.model)

        # Pour trier la vue par ordre descendant de date de transaction
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.model)
        self.view.setModel(proxyModel)
        # self.view.setSortingEnabled(True)
        # self.view.sortByColumn(7, Qt.DescendingOrder)
        self.view.reset()

        self.view.hideColumn(1)
        self.view.hideColumn(2)
        self.view.hideColumn(4)
        self.view.resizeColumnsToContents()
        self.setCentralWidget(self.view)

    def readSettingsFenTx(self):
        settings = QSettings("Budget", "Position fenêtre question transaction")
        pos = settings.value("posFenTx", QPoint(300, 700))
        size = settings.value("sizeFenTx", QSize(300, 700))
        self.resize(size)
        self.move(pos)

    def writeSettingsFenTx(self):
        settings = QSettings("Budget", "Position fenêtre question transaction")
        settings.setValue("posFenTx", self.pos())
        settings.setValue("sizeFenTx", self.size())

    def closeEvent(self, event):
        self.writeSettingsFenTx()

        for montant in g_LineEdit:
            calculerMontant(montant, True)



class Donut_BreakdownChart(QChart):
    def __init__(self, parent=None):
        super().__init__(QChart.ChartTypeCartesian, parent, Qt.WindowFlags())
        self.main_series = QPieSeries()
        self.main_series.setPieSize(0.7)
        self.addSeries(self.main_series)

    def add_breakdown_series(self, breakdown_series, color):
        font = QFont("Arial", 8)

        # add breakdown series as a slice to center pie
        main_slice = Donut_MainSlice(breakdown_series)
        main_slice.set_name(breakdown_series.name())
        main_slice.setValue(breakdown_series.sum())
        self.main_series.append(main_slice)

        # customize the slice
        main_slice.setBrush(color)
        main_slice.setLabelVisible()
        main_slice.setLabelColor(Qt.white)
        main_slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)
        main_slice.setLabelFont(font)

        # position and customize the breakdown series
        breakdown_series.setPieSize(0.8)
        breakdown_series.setHoleSize(0.7)
        breakdown_series.setLabelsVisible()

        for pie_slice in breakdown_series.slices():
            color = QColor(color).lighter(115)
            pie_slice.setBrush(color)
            pie_slice.setLabelFont(font)

        # add the series to the chart
        self.addSeries(breakdown_series)

        # recalculate breakdown donut segments
        self.recalculate_angles()

        # update customize legend markers
        self.update_legend_markers()

    def recalculate_angles(self):
        angle = 0
        slices = self.main_series.slices()
        for pie_slice in slices:
            breakdown_series = pie_slice.get_breakdown_series()
            breakdown_series.setPieStartAngle(angle)
            angle += pie_slice.percentage() * 360.0  # full pie is 360.0
            breakdown_series.setPieEndAngle(angle)

    def update_legend_markers(self):
        # go through all markers
        for series in self.series():
            markers = self.legend().markers(series)
            for marker in markers:
                if series == self.main_series:
                    # hide markers from main series
                    marker.setVisible(False)
                else:
                    # modify markers from breakdown series
                    label = marker.slice().label()
                    p = marker.slice().percentage() * 10 * 10
                    marker.setLabel(f"{label} {p:.2f}%")
                    marker.setFont(QFont("Arial", 8))


class Donut_MainSlice(QPieSlice):
    def __init__(self, breakdown_series, parent=None):
        super().__init__(parent)

        self.breakdown_series = breakdown_series
        self.name = None

        self.percentageChanged.connect(self.update_label)

    def get_breakdown_series(self):
        return self.breakdown_series

    def set_name(self, name):
        self.name = name

    def name(self):
        return self.name

    @Slot()
    def update_label(self):
        p = self.percentage() * 100
        self.setLabel(f"{self.name} {p:.2f}%")


class AnotherWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.series = QPieSeries()
        self.series.append('Jane', 1)
        self.series.append('Joe', 2)
        self.series.append('Andy', 3)
        self.series.append('Barbara', 4)
        self.series.append('Axel', 5)

        self.slice = self.series.slices()[1]
        self.slice.setExploded()
        self.slice.setLabelVisible()
        self.slice.setPen(QPen(Qt.darkGreen, 2))
        self.slice.setBrush(Qt.green)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle('Simple pie chart example')
        self.chart.legend().hide()

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self._chart_view)


class Afficher_Donut_Depenses(QMainWindow):
    def __init__(self):
        super().__init__()

        self.series1 = QPieSeries()
        self.series1.setName("Revenus")
        self.series1.append("Paie GRICS", 2284.29)
        # self.series1.append("Autre revenu", 0.00)
        self.series1.append("Factures communes - De Diane", 239.29)

        self.series2 = QPieSeries()
        self.series2.setName("Dépenses variables")
        # self.series2.append("Capital One", 0.00)
        # self.series2.append("Dépenses personnelles", 0.00)
        # self.series2.append("Dépenses pour maison", 0.00)
        self.series2.append("Épiceries", 250.00)
        self.series2.append("Essences", 100.00)
        self.series2.append("Restaurants", 75.00)
        # self.series2.append("Visa", 0.00)

        self.series3 = QPieSeries()
        self.series3.setName("Dépenses aux 2 semaines")
        self.series3.append("Épargne pour la famille", 150.00)
        self.series3.append("Maison - Paiement pour l'assurance", 24.18)
        self.series3.append("Maison - Paiement du prêt", 271.05)
        self.series3.append("Maison - Paiement des taxes", 53.50)
        # self.series3.append("Nourriture pour les animaux", 0.00)
        self.series3.append("Remboursement RÉER", 25.00)
        self.series3.append("Voiture - Paiement du prêt", 296.36)
        # self.series3.append("goPeer", 227.98)

        self.series4 = QPieSeries()
        self.series4.setName("Factures communes")
        self.series4.append("Apple One", 42.21)
        # self.series4.append("Bell cellulaire", 332.49)
        self.series4.append("Cogeco", 185.16)
        self.series4.append("HP imprimante", 20.00)
        self.series4.append("Hydro-Québec", 227.08)
        self.series4.append("Netflix", 24.13)
        # self.series4.append("Tou.TV", 7.21)
        # self.series4.append("Disney+", 13.79)
        # self.series4.append("Amazon Prime", 12.00)

        self.series5 = QPieSeries()
        self.series5.setName("Dépenses mensuelles")
        self.series5.append("Assurance vie personnelle", 26.00)
        # self.series5.append("Frais bancaire", 13.95)
        self.series5.append("Médicaments", 20.00)
        # self.series5.append("NY Times", 2.30)
        # self.series5.append("Xbox", 19.53)
        # self.series5.append("Paybright iPhone", 30.38)
        # self.series5.append("Paybright Mac", 208.25)
        # self.series5.append("Hector", 50.00)
        # self.series5.append("Financial Fairstone", 160.00)
        # self.series5.append("Flexiti", 50.00)

        donut_breakdown = Donut_BreakdownChart()
        donut_breakdown.setAnimationOptions(QChart.AllAnimations)
        donut_breakdown.setTitle("Revenu total : $ 2289.32")
        donut_breakdown.legend().setAlignment(Qt.AlignRight)
        # donut_breakdown.add_breakdown_series(self.series1, QtPySide6.red)
        donut_breakdown.add_breakdown_series(self.series2, Qt.darkGreen)
        donut_breakdown.add_breakdown_series(self.series3, Qt.darkBlue)
        donut_breakdown.add_breakdown_series(self.series4, Qt.darkYellow)
        donut_breakdown.add_breakdown_series(self.series5, Qt.blue)

        self.chart_view = QChartView(donut_breakdown)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.chart_view)
        available_geometry = self.screen().availableGeometry()
        size = available_geometry.height() * 0.75
        self.resize(size, size * 0.8)


class Afficher_Line_Bar(QMainWindow):
    def __init__(self):
        super().__init__()

        self.bar_series = QBarSeries()
        self.line_series = QLineSeries()

        bar0 = QBarSet("Revenus")
        bar1 = QBarSet("Dépenses")
        # Revenu pour les 6 périodes
        bar0.append([2200, 2200, 2340, 2200, 2200, 2200])
        # Dépenses pour les 6 périodes
        bar1.append([3000, 2500, 2340, 2625, 2100, 2835])
        self.bar_series.append(bar0)
        self.bar_series.append(bar1)

        self.line_series.setName("trend")
        self.line_series.append(QPoint(0, 3000))
        self.line_series.append(QPoint(700, 2500))
        self.line_series.append(QPoint(1400, 2340))
        self.line_series.append(QPoint(2100, 2625))
        self.line_series.append(QPoint(2800, 2100))
        self.line_series.append(QPoint(3500, 2835))

        x_axis = QBarCategoryAxis()
        categories = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui"]
        x_axis.append(categories)

        y_axis = QValueAxis()
        y_axis.setRange(0, 3500)
        y_axis.setLabelFormat("$ %0.2f")
        y_axis.setTickType(QValueAxis.TickType.TicksDynamic)
        y_axis.setTickInterval(700)
        y_axis.setTitleText("Montants")

        chart = QChart()
        chart.addAxis(x_axis, Qt.AlignBottom)
        x_axis.setRange("Jan", "Jui")
        chart.addAxis(y_axis, Qt.AlignLeft)

        chart.addSeries(self.bar_series)
        chart.addSeries(self.line_series)

        for serie in chart.series():
            serie.attachAxis(x_axis)
            serie.attachAxis(y_axis)

        chart.setTitle("Revenus et dépenses")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.chart_view = QChartView(chart)
        self.setGeometry(500, 500, 1000, 800)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.chart_view)


class AfficherStat(QMainWindow):
    def __init__(self):
        super().__init__()

        self.NbShow = 0

        self.window1 = AnotherWindow()
        self.window2 = Afficher_Donut_Depenses()
        self.window3 = Afficher_Line_Bar()

        layoutBouton = QVBoxLayout()
        button1 = QPushButton("Push for Window 1")
        button1.clicked.connect(lambda checked: toggle_window(self.window1))
        layoutBouton.addWidget(button1)

        button2 = QPushButton("Push for Window 2")
        button2.clicked.connect(lambda checked: toggle_window(self.window2))
        layoutBouton.addWidget(button2)

        button3 = QPushButton("Push for Window 3")
        button3.clicked.connect(lambda checked: toggle_window(self.window3))
        layoutBouton.addWidget(button3)

        w = QWidget()
        w.setLayout(layoutBouton)
        self.setCentralWidget(w)

        if self.NbShow == 0:
            self.NbShow += 1
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.show()

    """
    Ce closeEvent est appelé lorsque l'utilisateur clique sur le bouton X de la fenêtre principale. 
    """

    def closeEvent(self, event):
        self.NbShow -= 1


def toggle_window(window):
    if window.isVisible():
        window.hide()
    else:
        window.show()


def Window():
    app = QApplication(sys.argv)
    MyApp()
    sys.exit(app.exec())


if __name__ == '__main__':
    Window()
