from ampalibe import Model
from datetime import datetime
import mysql

class CyclesModel(Model):
    def __init__(self, user_id, start_date, duration, next_ovulation, next_period, fin_regle, debut_fenetre, fin_fenetre):
        super().__init__()
        self.user_id = user_id
        # Convertir toutes les dates du format JJ/MM/AAAA au format AAAA-MM-JJ pour MySQL
        self.start_date = self._convert_to_mysql_format(start_date)
        self.duration = duration
        self.next_ovulation = self._convert_to_mysql_format(next_ovulation)
        self.next_periode = self._convert_to_mysql_format(next_period)
        self.fin_regle = self._convert_to_mysql_format(fin_regle)
        self.debut_fenetre = self._convert_to_mysql_format(debut_fenetre)
        self.fin_fenetre = self._convert_to_mysql_format(fin_fenetre)
        self.created_at = datetime.now()

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
    def update_cycle_dates(self, start_date, duration, next_ovulation, next_period, fin_regle, debut_fenetre, fin_fenetre):
        try:
            # Conversion des dates pour MySQL
            start_date_mysql = self._convert_to_mysql_format(start_date)
            next_ovulation_mysql = self._convert_to_mysql_format(next_ovulation)
            next_period_mysql = self._convert_to_mysql_format(next_period)
            fin_regle_mysql = self._convert_to_mysql_format(fin_regle)
            debut_fenetre_mysql = self._convert_to_mysql_format(debut_fenetre)
            fin_fenetre_mysql = self._convert_to_mysql_format(fin_fenetre)

            # Mise à jour du cycle dans la base de données
            req = """
                UPDATE cycles
                SET start_date = %s, next_ovulation = %s, next_period = %s, fin_regles = %s, debut_fenetre = %s, fin_fenetre = %s, duration = %s
                WHERE user_id = %s ORDER BY created_at DESC LIMIT 1
            """
            self.cursor.execute(req, (start_date_mysql, next_ovulation_mysql, next_period_mysql, fin_regle_mysql,
                                      debut_fenetre_mysql, fin_fenetre_mysql, duration, self.user_id))
            self.db.commit()
            print("Cycle mis à jour avec succès dans la base de données.")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la mise à jour du cycle : {err}")
            self.db.rollback()