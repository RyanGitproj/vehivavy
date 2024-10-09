import ampalibe
from ampalibe import Messenger, Payload
from User_list import CustomModel
from ampalibe.messenger import Action
from ampalibe.ui import Type, Button
from Calcul_periode import Calcul_periode
import re
import calendar

chat = Messenger()
query = CustomModel()

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.mark_seen)
    # Envoyer le message d'accueil avec deux options (Oui et Non)
    buttons = [
        Button(
            type=Type.postback,
            title='Oui',
            payload=Payload('/saisie_date')
        ),
        Button(
            type=Type.postback,
            title='Non',
            payload=Payload('/sortie')
        )
    ]
    chat.send_button(sender_id, buttons, "Bonjour ! Je suis là pour t'aider à suivre ton cycle menstruel. Veux-tu commencer ?")

@ampalibe.command('/saisie_date')
def saisie_date(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.typing_on)

    # Demander la date de début des règles
    chat.send_text(sender_id, "Peux-tu me donner la date de début de tes dernières règles ? (Format: JJ/MM/AAAA)")
    query.set_action(sender_id,"/get_date")

@ampalibe.action('/get_date')
def get_date(sender_id, cmd, **ext):
    try:
        query.set_action(sender_id, None)
        # Vérification du format de la date (JJ/MM/AAAA)
        if re.match(r'^\d{2}/\d{2}/\d{4}$', cmd):
            day, month, year = map(int, cmd.split('/'))

            # Vérification que la date est valide
            if month < 1 or month > 12:
                raise ValueError("Le mois est invalide.")
            if day < 1 or day > calendar.monthrange(year, month)[1]:
                raise ValueError("Le jour est invalide pour ce mois et cette année.")

            # Si tout est correct, enregistrer la date
            query.set_temp(sender_id, 'date_debut', cmd)
            chat.send_text(sender_id, "Quel est la durée de votre dernier cycle en jours ?")
            query.set_action(sender_id, "/get_dure")
        else:
            raise ValueError("Le format de la date est incorrect.")
    except ValueError as e:
        chat.send_text(sender_id, str(e) + " Merci de réessayer au format JJ/MM/AAAA.")
        query.set_action(sender_id, "/get_date")
    print(cmd)


@ampalibe.action('/get_dure')
def get_dure(sender_id, cmd, **ext):
    try:
        query.set_action(sender_id, None)
        # Vérification si la durée est bien un entier
        dure_cycle = int(cmd)
        query.set_temp(sender_id, 'dure_cycle', dure_cycle)
        # Passer ensuite à la confirmation après avoir envoyé ce message
        confirmation(sender_id)
    except ValueError:
        chat.send_text(sender_id, "La durée doit être un nombre entier. Peux-tu réessayer ?")
        query.set_action(sender_id, "/get_dure")
    print(cmd)

def confirmation(sender_id, **ext):
    query.set_action(sender_id, None)
    debut_date = query.get_temp(sender_id, 'date_debut')
    cycle_dure = query.get_temp(sender_id, 'dure_cycle')
    chat.send_text(sender_id, f'Merci ! Tes dernières règles ont commencé le {debut_date} et ont duré {cycle_dure} jours. Je vais t\'envoyer des rappels pour les phases importantes de ton cycle, ainsi que des notifications quotidiennes sur ta zone.')
    calcul(sender_id, debut_date, cycle_dure)

def calcul(sender_id, date_debut, dure_cycle):
    calculs = Calcul_periode(date_debut, dure_cycle)
    resultats = calculs.calculer_periode()
    
    # Vérifie si le résultat contient une erreur
    if isinstance(resultats, dict) and 'error' in resultats:
        chat.send_text(sender_id, resultats['error'])
        return
    
    # Envoyer les résultats à l'utilisateur
    chat.send_text(sender_id, f"Voici les résultats de ton cycle :\n"
                                f"Date d'ovulation : {resultats['date_ovulation']}\n"
                                f"Fenêtre fertile : {resultats['debut_fenetre_fertile']} à {resultats['fin_fenetre_fertile']}\n"
                                f"Prochaine date des règles : {resultats['prochaine_date_regle']}\n"
                                f"Fin des règles : {resultats['fin_regle']}")
    
    query.del_temp(sender_id, 'date_debut')
    query.del_temp(sender_id, 'dure_cycle')
