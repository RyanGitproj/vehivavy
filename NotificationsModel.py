from ampalibe import Model
from datetime import datetime, timedelta
import mysql

from Notification import NotificationModel

class NotificationsModel(Model):
    def __init__(self, cycle_id=None, notification_date=None, zone_type=None, sent=False):
        super().__init__()
        self.cycle_id = cycle_id
        self.notification_date = self._convert_to_mysql_format(notification_date) if notification_date else None
        self.zone_type = zone_type
        self.sent = sent
        self.created_at = datetime.now()

    def _convert_to_mysql_format(self, date_str):
        """Convertir une date du format JJ/MM/AAAA au format AAAA-MM-JJ pour MySQL"""
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

    @Model.verif_db
    def ajouter_notification(self):
        try:
            req = """INSERT INTO notifications (cycle_id, notification_date, zone_type, sent, created_at)
            VALUES (%s, %s, %s, %s, %s)"""

            self.cursor.execute(req, (self.cycle_id, self.notification_date, self.zone_type, self.sent, self.created_at))
            self.db.commit()
        except mysql.connector.Error as err:
            print(f"Erreur lors de l'ajout de la notification : {err}")
            self.db.rollback()

    @Model.verif_db
    def verifier_notification_a_envoyer(self):
        """Récupérer les notifications non envoyées pour aujourd'hui"""
        try:
            req = """SELECT id, cycle_id, zone_type FROM notifications
                     WHERE notification_date = %s AND sent = 0"""
            today = datetime.now().strftime("%Y-%m-%d")
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

    def generer_notification(self, cycle_id, start_date, next_period):
        """Générer des notifications en fonction des dates de fertilité stockées dans la base de données"""
        try:
            # Récupérer les dates de fertilité du cycle
            req = """SELECT next_ovulation, debut_fenetre, fin_fenetre, fin_regles
                    FROM cycles WHERE id = %s"""
            
            self.cursor.execute(req, (cycle_id,))
            cycle_data = self.cursor.fetchone()

            if not cycle_data:
                raise ValueError("Aucune donnée de cycle trouvée pour cet ID.")
            
            # Décomposer les dates de fertilité
            date_ovulation, debut_fenetre_fertile, fin_fenetre_fertile, fin_regle = cycle_data

            # Convertir toutes les dates en `datetime.date` pour des comparaisons uniformes
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(date_ovulation, datetime):
                date_ovulation = date_ovulation.date()
            if isinstance(debut_fenetre_fertile, datetime):
                debut_fenetre_fertile = debut_fenetre_fertile.date()
            if isinstance(fin_fenetre_fertile, datetime):
                fin_fenetre_fertile = fin_fenetre_fertile.date()
            if isinstance(fin_regle, datetime):
                fin_regle = fin_regle.date()
            if isinstance(next_period, str):
                next_period = datetime.strptime(next_period, "%Y-%m-%d").date()

            # Générer des notifications pour chaque jour entre start_date et next_period
            current_date = start_date
            while current_date < next_period:
                zone_type = self.determine_zone(current_date, start_date, date_ovulation, debut_fenetre_fertile, fin_fenetre_fertile, fin_regle)
                notification = NotificationsModel(cycle_id, current_date.strftime('%d/%m/%Y'), zone_type)
                notification.ajouter_notification()
                current_date += timedelta(days=1)  # Passer au jour suivant

        except mysql.connector.Error as err:
            print(f"Erreur lors de la récupération des données de cycle : {err}")


    def determine_zone(self, date, start_date, date_ovulation, debut_fenetre_fertile, fin_fenetre_fertile, fin_regle):
        """Déterminer la zone du cycle pour une date donnée"""

        if debut_fenetre_fertile <= date <= fin_fenetre_fertile:
            return 'orange'  # Fenêtre fertile
        elif date == date_ovulation:
            return 'rouge'  # Ovulation
        elif start_date <= date <= fin_regle :
            return 'bleue' # période de règles
        else:
            return 'verte'  # Autre période
    @Model.verif_db
    def supprimer_notifications_cycle(self, cycle_id):
        """Supprimer toutes les notifications d'un cycle spécifique."""
        try:
            req = "DELETE FROM notifications WHERE cycle_id = %s"
            self.cursor.execute(req, (cycle_id,))
            self.db.commit()
        except mysql.connector.Error as err:
            print(f"Erreur lors de la suppression des notifications : {err}")
            self.db.rollback()
    def generer_notifications(self, cycle_id, date_debut):
        """Générer des notifications après la mise à jour d'un cycle"""
        # Supprimer les anciennes notifications pour le cycle mis à jour
        self.supprimer_notifications_cycle(cycle_id)

        try:
            # Récupérer les nouvelles dates de fertilité du cycle mis à jour
            req = """SELECT date_ovulation, debut_fenetre_fertile, fin_fenetre_fertile, prochaine_date_regle, fin_regle
                    FROM cycles WHERE id = %s"""
            self.cursor.execute(req, (cycle_id,))
            cycle_data = self.cursor.fetchone()

            if not cycle_data:
                raise ValueError("Aucune donnée de cycle trouvée pour cet ID.")

            # Décomposer les dates de fertilité
            date_ovulation, debut_fenetre_fertile, fin_fenetre_fertile, prochaine_date_regle, fin_regle = cycle_data

            # Créer les nouvelles notifications pour chaque date du cycle
            for date in [debut_fenetre_fertile, date_ovulation, fin_fenetre_fertile, prochaine_date_regle, fin_regle]:
                zone_type = self.determine_zone(date, date_ovulation)
                notification = NotificationModel(cycle_id, date.strftime('%d/%m/%Y'), zone_type)
                notification.ajouter_notification()

        except mysql.connector.Error as err:
            print(f"Erreur lors de la récupération des données de cycle : {err}")
        
    def supprimer_notifications(self, cycle_id):
        """Supprimer toutes les notifications associées à un cycle."""
        try:
            req = "DELETE FROM notifications WHERE cycle_id = %s"
            self.cursor.execute(req, (cycle_id,))
            self.db.commit()
            print(f"Notifications supprimées pour le cycle_id {cycle_id}")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la suppression des notifications : {err}")
            self.db.rollback()



