from datetime import datetime, timedelta

class Calcul_periode:
    def __init__(self, date_debut, dure_cycle: int):
        self.date_debut = date_debut
        self.dure_cycle = dure_cycle
        self.dure_periode = 5

    def _convertir_date(self):
        """Convertit la date de début en format datetime"""
        try:
            debut_date = datetime.strptime(self.date_debut, "%d/%m/%Y")
            return debut_date
        except ValueError:
            raise ValueError("La date doit être au format JJ/MM/AAAA")

    def _verifier_dure_cycle(self):
        """Vérifie que la durée du cycle est un entier"""
        if not isinstance(self.dure_cycle, int):
            raise ValueError("La durée du cycle doit être un nombre entier.")
        return True

    def calcul_prochaine_date_regles(self):
        """Calcule la date des prochaines règles"""
        self._verifier_dure_cycle()
        debut_date = self._convertir_date()
        prochaine_date_regles = debut_date + timedelta(days=self.dure_cycle)
        return prochaine_date_regles

    def calcul_date_ovulation(self, prochaine_date_regles):
        """Calcule la date d'ovulation"""
        try:
            date_ovulation = prochaine_date_regles - timedelta(days=14)
            return date_ovulation
        except Exception as e:
            raise Exception(f"Erreur lors du calcul de l'ovulation : {str(e)}")

    def calcul_fenetre_fertile(self, date_ovulation):
        """Calcule la fenêtre fertile"""
        try:
            debut_fenetre_fertile = date_ovulation - timedelta(days=5)
            fin_fenetre_fertile = date_ovulation + timedelta(days=1)
            return debut_fenetre_fertile, fin_fenetre_fertile
        except Exception as e:
            raise Exception(f"Erreur lors du calcul de la fenêtre fertile : {str(e)}")

    def calcul_fin_regles(self, debut_date):
        """Calcule la fin des règles"""
        try:
            fin_regle = debut_date + timedelta(days=self.dure_periode)
            return fin_regle
        except Exception as e:
            raise Exception(f"Erreur lors du calcul de la fin des règles : {str(e)}")

    def calculer_periode(self):
        """Calcule toutes les phases du cycle menstruel"""
        try:
            debut_date = self._convertir_date()
            prochaine_date_regles = self.calcul_prochaine_date_regles()
            date_ovulation = self.calcul_date_ovulation(prochaine_date_regles)
            debut_fenetre_fertile, fin_fenetre_fertile = self.calcul_fenetre_fertile(date_ovulation)
            fin_regle = self.calcul_fin_regles(debut_date)

            return {
                "date_ovulation": date_ovulation.strftime("%d/%m/%Y"),
                "debut_fenetre_fertile": debut_fenetre_fertile.strftime("%d/%m/%Y"),
                "fin_fenetre_fertile": fin_fenetre_fertile.strftime("%d/%m/%Y"),
                "prochaine_date_regle": prochaine_date_regles.strftime("%d/%m/%Y"),
                "fin_regle": fin_regle.strftime("%d/%m/%Y")
            }

        except Exception as e:
            return {"error": f"Une erreur s'est produite : {str(e)}"}
