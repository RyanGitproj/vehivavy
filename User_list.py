from ampalibe import Model
from datetime import datetime
import mysql

class CustomModel(Model):
    def __init__(self):
        super().__init__()

    @Model.verif_db
    def add_user(self):
        '''
            Method to add a static user
        '''
        req = "INSERT INTO users (messenger_id) VALUES ('123456787')"
        self.cursor.execute(req)
        self.db.commit()

    @Model.verif_db
    def get_all_users(self):
        '''
            Method to retrieve all users from the database
        '''
        req = "SELECT * FROM users"
        self.cursor.execute(req)
        data = self.cursor.fetchall()  # Fetch all rows
        return data
    
    @Model.verif_db
    def verifier_notification_a_envoyer(self):
        """Récupérer les notifications non envoyées pour aujourd'hui"""
        try:
            req = """SELECT id, cycle_id, zone_type FROM notifications
            WHERE notification_date = %s AND sent = 0"""
            today = datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute(req, (today,))

            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erreur lors de la récupération des notifications : {err}")
            return []

    @Model.verif_db
    def marquer_comme_envoyee(self, notification_id):
        """Marquer une notification comme envoyée"""
        try:
            req = """UPDATE notifications SET sent = 1 WHERE id = %s"""
            self.cursor.execute(req, (notification_id,))
            self.db.commit()
        except mysql.connector.Error as err:
            print(f"Erreur lors de la mise à jour de la notification : {err}")
            self.db.rollback()

    @Model.verif_db
    def get_messenger_id(self, cycle_id):
        try:
            req = """
            SELECT u.messenger_id 
            FROM users u
            JOIN cycles c ON u.id = c.user_id
            WHERE c.id = %s
            """
            self.cursor.execute(req, (cycle_id,))
            result = self.cursor.fetchone()  # Récupérer un seul résultat
            return result[0] if result else None  # Accéder par indice
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    @Model.verif_db
    def get_rappel(self, cycle_id):
        try:
            # Requête pour obtenir les dates d'ovulation et de fin des règles
            req = """
            SELECT next_ovulation, next_period
            FROM cycles
            WHERE id = %s
            """
            self.cursor.execute(req, (cycle_id,))
            result = self.cursor.fetchone()  # Récupérer un seul résultat
            if result:
                # Retourner les dates sous forme de tuple
                next_ovulation, next_period = result
                return next_ovulation, next_period
            else:
                print(f"Aucune donnée trouvée pour le cycle_id {cycle_id}")
                return None, None
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {str(e)}")
            return None, None
