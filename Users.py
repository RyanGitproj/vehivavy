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
    @Model.verif_db
    def trouver_cycle_id(self):
        try:
            # D'abord, récupérer l'user_id en fonction du sender_id
            req_user = """SELECT id FROM users WHERE messenger_id = %s"""
            self.cursor.execute(req_user, (self.sender_id,))
            user = self.cursor.fetchone()

            if not user:
                raise ValueError("Aucun utilisateur trouvé pour ce sender_id.")

            user_id = user[0]

            # Ensuite, récupérer le cycle le plus récent pour cet user_id
            req_cycle = """SELECT id FROM cycles WHERE user_id = %s ORDER BY created_at DESC LIMIT 1"""
            self.cursor.execute(req_cycle, (user_id,))
            cycle = self.cursor.fetchone()

            if cycle:
                return cycle[0]  # Retourne l'ID du cycle
            else:
                raise ValueError("Aucun cycle trouvé pour cet utilisateur.")

        except mysql.connector.Error as err:
            print(f"Erreur lors de la récupération du cycle_id : {err}")
            return None

