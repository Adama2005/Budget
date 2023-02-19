import sys
from PySide6.QtWidgets import QMessageBox
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


class Sql:
    def __init__(self):
        # super().__init__()
        self.baseDeDonnees = ""
        self.requeteSQL = ""
        self.nbRequeteOuverte = -1
        self.sqlQuery = []
        self.connecteurSQL = QSqlDatabase()
        self.erreurSQL = 1

    def ouvrirBD(self, base_de_donnees):
        self.baseDeDonnees = base_de_donnees
        self.erreurSQL = 1

        self.connecteurSQL = QSqlDatabase.addDatabase("QSQLITE")
        self.connecteurSQL.setDatabaseName(self.baseDeDonnees)

        # Try to open the connection and handle possible errors
        if not self.connecteurSQL.open():
            QMessageBox.critical(
                    fenetre_principale,
                    "Erreur d'ouverture de la base de données!",
                    "Database Erreur: %s" % self.connecteur.lastError().databaseText(),
            )
            self.erreurSQL = 0
            sys.exit(self.erreurSQL)
        return self.erreurSQL

    def fermerDB(self):
        self.erreurSQL = 1

        self.connecteurSQL.close()

        return self.erreurSQL

    def ouvrirRequete(self, requete_sql):
        self.erreurSQL = 1
        self.nbRequeteOuverte += 1
        self.requeteSQL = requete_sql

        self.sqlQuery.append(self.nbRequeteOuverte)
        self.sqlQuery[self.nbRequeteOuverte] = QSqlQuery()
        self.sqlQuery[self.nbRequeteOuverte].prepare(self.requeteSQL)
        if not self.sqlQuery[self.nbRequeteOuverte].exec(self.requeteSQL):
            QMessageBox.critical(
                    None,
                    "Erreur d'exécution de la requête SQL",
                    "Database Erreur: %s" % self.sqlQuery[self.nbRequeteOuverte].lastError().databaseText(),
                    "Requête :" + self.requeteSQL,
            )
            self.erreurSQL = 3

        return self.erreurSQL

    def lireEnr(self):
        if self.sqlQuery[self.nbRequeteOuverte].next():
            return self.sqlQuery[self.nbRequeteOuverte]
        else:
            None

    def valeur(self, colonne):
        self.sqlQuery[self.nbRequeteOuverte].value(colonne)
