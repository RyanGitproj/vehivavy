from ampalibe import Model
from datetime import datetime
import mysql

class UserModel(Model):
    def __init__(self, sender_id):
        super().__init__()
        self.sender_id = sender_id
        self.created_at = datetime.now()  # Assigner l'heure actuelle

    @Model.verif_db
    def ajout_user(self):

        try :
            # Ajout utilisateur
            req = """INSERT INTO users (messenger_id, created_at)
            VALUES (%s, %s)"""

            self.cursor.execute(req, (self.sender_id, self.created_at))

            self.db.commit()
        except mysql.connector.Error as err:
            # Gestion d'erreurs de la base de données
            print(f"Erreur lors de l'ajout de l'utilisateur : {err}")
            self.db.rollback()  # Annuler la transaction en cas d'erreur

    @Model.verif_db
    def trouver_id(self):
        try :
            #  Trouver l'utilisateur grace à son sender_id
            req = """SELECT id FROM users WHERE messenger_id = %s"""
            self.cursor.execute(req, (self.sender_id, ))
            data = self.cursor.fetchone()
            if data :
                return data[0]
            else:
                return None
        except mysql.connector.Error as err:
            # Gestion d'erreurs de la base de données
            print(f"Erreur lors de la recherche de l'utilisateur : {err}")
            return None  # Retourner None en cas d'erreur

