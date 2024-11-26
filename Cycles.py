from ampalibe import Model
from datetime import datetime
import mysql

class CyclesModel(Model):
    def __init__(self, user_id, start_date=None, duration=None, next_ovulation=None, next_period=None, fin_regle=None, debut_fenetre=None, fin_fenetre=None, cycle_id=None):
        super().__init__()
        self.user_id = user_id
        # Convertir les dates en format MySQL si elles sont fournies
        self.start_date = self._convert_to_mysql_format(start_date) if start_date else None
        self.duration = duration
        self.next_ovulation = self._convert_to_mysql_format(next_ovulation) if next_ovulation else None
        self.next_periode = self._convert_to_mysql_format(next_period) if next_period else None
        self.fin_regle = self._convert_to_mysql_format(fin_regle) if fin_regle else None
        self.debut_fenetre = self._convert_to_mysql_format(debut_fenetre) if debut_fenetre else None
        self.fin_fenetre = self._convert_to_mysql_format(fin_fenetre) if fin_fenetre else None
        self.created_at = datetime.now()
        self.cycle_id = cycle_id

    def _convert_to_mysql_format(self, date_str):
        """Convertir une date du format JJ/MM/AAAA au format AAAA-MM-JJ pour MySQL"""
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

    @Model.verif_db
    def ajout_cycle(self):
        try:
            # Ajout cycle dans la base de données
            req = """INSERT INTO cycles (user_id, start_date, duration, next_ovulation, next_period, fin_regles, debut_fenetre, fin_fenetre, created_at)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(req, (self.user_id, self.start_date, self.duration, self.next_ovulation, 
                                      self.next_periode, self.fin_regle, self.debut_fenetre, self.fin_fenetre, self.created_at))

            self.db.commit()

        except mysql.connector.Error as err:
            # Gestion d'erreurs de la base de données
            print(f"Erreur lors de l'ajout du cycle : {err}")
            self.db.rollback()  # Annuler la transaction en cas d'erreur

    @Model.verif_db
    def update_cycle(self):
        try:
            # Mise à jour du cycle dans la base de données
            req = """
            UPDATE cycles
            SET start_date = %s, duration = %s, next_ovulation = %s, 
                next_period = %s, fin_regles = %s, debut_fenetre = %s, 
                fin_fenetre = %s, created_at = %s
            WHERE user_id = %s
            """
            self.cursor.execute(req, (self.start_date, self.duration, self.next_ovulation, 
                                    self.next_periode, self.fin_regle, self.debut_fenetre, 
                                    self.fin_fenetre, self.created_at, self.user_id))
            self.db.commit()
            print("Cycle mis à jour avec succès.")

        except mysql.connector.Error as err:
            # Gestion d'erreurs de la base de données
            print(f"Erreur lors de la mise à jour du cycle : {err}")
            self.db.rollback()  # Annuler la transaction en cas d'erreur

    @Model.verif_db
    def get_cycle_id(self):
        """Récupérer l'ID du cycle actif pour un utilisateur"""
        try:
            req = """SELECT id FROM cycles 
                     WHERE user_id = %s 
                     ORDER BY created_at DESC LIMIT 1"""  # Récupère le dernier cycle créé pour l'utilisateur
            self.cursor.execute(req, (self.user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                raise ValueError("Aucun cycle trouvé pour cet utilisateur.")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la récupération du cycle ID : {err}")
            return None
