import ampalibe
from ampalibe import Messenger, Payload, crontab
from User_list import CustomModel
from ampalibe.messenger import Action
from ampalibe.ui import Type, Button
from Calcul_periode import Calcul_periode
from Users import UserModel
from Cycles import CyclesModel
import re
import calendar
from datetime import datetime, timedelta
from NotificationsModel import NotificationsModel


chat = Messenger()
query = CustomModel()


# Démarrer
chat.get_started()

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
    
    # Enregistrer l'utilisateur
    user_request = UserModel(sender_id)
    user_request.ajout_user()

@ampalibe.command('/reset')
def reset(sender_id, cmd, **ext):

        # Envoyer un message de confirmation à l'utilisateur
        print(sender_id, "La conversation a été réinitialisée. Vous pouvez recommencer.")
        
        # Rediriger vers le menu principal
        main(sender_id, cmd, **ext)
        print(cmd)
        print("-------")
        print(ext)

@ampalibe.command('/saisie_date')
def saisie_date(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.typing_on)

    # Demander la date de début des règles
    chat.send_text(sender_id, "Peux-tu me donner la date de début de tes dernières règles ? (Format: JJ/MM/AAAA)")
    query.set_action(sender_id, "/get_date")

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
    chat.send_text(sender_id, f"🟩 Zone Verte 🟢 : Période peu fertile. C'est une phase où il y a moins de chances de concevoir.\n🟧 Zone Orange 🟠 : Période ovulatoire. Cette phase correspond à la fenêtre de fertilité possible où l'ovulation approche.\n🟥 Zone Rouge 🔴 : Soit Menstruations || soit période fertile élevée. Cette phase est marquée par soit les règles || soit une haute probabilité de fertilité.")
    calcul(sender_id, debut_date, cycle_dure)
    # Ajouter des boutons pour demander si l'utilisateur veut mettre à jour
    buttons = [
        Button(
            type=Type.postback,
            title='Mettre à jour',
            payload=Payload('/update_cycle')
        ),
        Button(
            type=Type.postback,
            title='Pas maintenant',
            payload=Payload('/no_update')
        )
    ]
    chat.send_button(sender_id, buttons, "Souhaites-tu mettre à jour les dates de ton cycle ?")

# UPDATE
@ampalibe.command('/update_cycle')
def update_cycle(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.mark_seen)
    # Envoyer des boutons pour Oui et Non
    buttons = [
        Button(
            type=Type.postback,
            title='Oui',
            payload=Payload('/start_update')
        ),
        Button(
            type=Type.postback,
            title='Non',
            payload=Payload('/no_update')
        )
    ]
    chat.send_button(sender_id, buttons, "Est-ce que les dernières règles sont bien arrivé ? Cela permettra de mettre à jour les informations. ?")

@ampalibe.command('/start_update')
def start_update(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.typing_on)
    chat.send_text(sender_id, "Peux-tu me donner la nouvelle date de début de tes dernières règles ? (Format: JJ/MM/AAAA)")
    query.set_action(sender_id, "/get_new_date")

@ampalibe.action('/get_new_date')
def get_new_date(sender_id, cmd, **ext):
    try:
        query.set_action(sender_id, None)
        if re.match(r'^\d{2}/\d{2}/\d{4}$', cmd):
            day, month, year = map(int, cmd.split('/'))
            if month < 1 or month > 12 or day < 1 or day > calendar.monthrange(year, month)[1]:
                raise ValueError("La date est invalide.")
            query.set_temp(sender_id, 'new_date_debut', cmd)
            chat.send_text(sender_id, "Quel est la durée de votre nouveau cycle en jours ?")
            query.set_action(sender_id, "/get_new_duration")
        else:
            raise ValueError("Le format de la date est incorrect.")
    except ValueError as e:
        chat.send_text(sender_id, str(e) + " Merci de réessayer au format JJ/MM/AAAA.")
        query.set_action(sender_id, "/get_new_date")
    
@ampalibe.action('/get_new_duration')
def get_new_duration(sender_id, cmd, **ext):
    try:
        query.set_action(sender_id, None)
        dure_cycle = int(cmd)
        query.set_temp(sender_id, 'new_dure_cycle', dure_cycle)
        confirmer_mise_a_jour(sender_id)
    except ValueError:
        chat.send_text(sender_id, "La durée doit être un nombre entier. Peux-tu réessayer ?")
        query.set_action(sender_id, "/get_new_duration")

def confirmer_mise_a_jour(sender_id):
    new_start_date = query.get_temp(sender_id, 'new_date_debut')
    new_duration = query.get_temp(sender_id, 'new_dure_cycle')
    chat.send_text(sender_id, f"Merci ! Tes informations ont été mises à jour avec la nouvelle date de début: {new_start_date} et une durée de {new_duration} jours. Je vais t'envoyer des rappels pour les phases importantes de ton cycle, ainsi que des notifications quotidiennes sur ta zone.")
    
    # Calculer les nouvelles dates et les mettre à jour
    user_id = UserModel(sender_id).trouver_id()
    calculs = Calcul_periode(new_start_date, new_duration).calculer_periode()
    
    # Récupérer les nouvelles dates calculées
    next_ovulation = calculs['date_ovulation']
    next_periode = calculs['prochaine_date_regle']
    fin_regle = calculs['fin_regle']
    debut_fenetre = calculs['debut_fenetre_fertile']
    fin_fenetre = calculs['fin_fenetre_fertile']
    
    # Mise à jour dans la base de données
    cycle_request = CyclesModel(user_id, new_start_date, new_duration, next_ovulation, next_periode, fin_regle, debut_fenetre, fin_fenetre)
    cycle_request.update_cycle()
    # calcul(sender_id, new_start_date, new_duration)
    # Ajouter des boutons pour demander si l'utilisateur veut mettre à jour
    buttons = [
        Button(
            type=Type.postback,
            title='Mettre à jour',
            payload=Payload('/update_cycle')
        ),
        Button(
            type=Type.postback,
            title='Pas maintenant',
            payload=Payload('/no_update')
        )
    ]
    chat.send_button(sender_id, buttons, "Souhaites-tu mettre à jour les dates de ton cycle ?")

@ampalibe.command('/no_update')
def no_update(sender_id, cmd, **ext):
    chat.send_text(sender_id, "Tu recevras des rappels quotidiens sur ta zone et les dates clés. N'hésite pas à revenir si tu as des questions !")
# Ajouter des boutons pour demander si l'utilisateur veut mettre à jour
    buttons = [
        Button(
            type=Type.postback,
            title='Mettre à jour',
            payload=Payload('/update_cycle')
        ),
        Button(
            type=Type.postback,
            title='Pas maintenant',
            payload=Payload('/no_update')
        )
    ]
    chat.send_button(sender_id, buttons, "Souhaites-tu mettre à jour les dates de ton cycle ?")

def calcul(sender_id, date_debut, dure_cycle):
    query.set_action(sender_id, None)
    calculs = Calcul_periode(date_debut, dure_cycle)
    resultats = calculs.calculer_periode()
    
    # Vérifie si le résultat contient une erreur
    if isinstance(resultats, dict) and 'error' in resultats:
        chat.send_text(sender_id, resultats['error'])
        return
    user_id = UserModel(sender_id)
    id_user = user_id.trouver_id()
    print(f'id_user : {id_user}')
    start_date = query.get_temp(sender_id, 'date_debut')
    duration = query.get_temp(sender_id, 'dure_cycle')
    next_ovulation = resultats['date_ovulation']
    next_periode = resultats['prochaine_date_regle']
    fin_regle = resultats['fin_regle']
    debut_fenetre = resultats['debut_fenetre_fertile']
    fin_fenetre = resultats['fin_fenetre_fertile']

    # Envoyer les résultats à l'utilisateur
    chat.send_text(sender_id, f"Voici les résultats de ton cycle :\n"
                                f"Date probable d'ovulation : {resultats['date_ovulation']}\n"
                                f"Fenêtre fertile : {resultats['debut_fenetre_fertile']} à {resultats['fin_fenetre_fertile']}\n"
                                f"Prochaine date des règles : {resultats['prochaine_date_regle']}\n"
                                f"Fin des règles : {resultats['fin_regle']}")
    chat.send_text(sender_id, f"Rappels clés supplémentaires\n"
                                f"🟠 Ton ovulation est prévue le : {resultats['date_ovulation']}\n"
                                f"🔴 Prochaine date des règles : {resultats['prochaine_date_regle']}\n")
    
    cycle_request = CyclesModel(id_user, start_date, duration, next_ovulation, next_periode, fin_regle, debut_fenetre, fin_fenetre)
    cycle_request.ajout_cycle()
    creation_notification(sender_id, start_date, dure_cycle)

def creation_notification(sender_id, date_debut, dure_cycle):
    try:
        # Créer une instance de CyclesModel pour récupérer le cycle_id
        cycle_req = UserModel(sender_id)
        
        # Trouver le cycle_id correspondant au sender_id
        cycle_id = cycle_req.trouver_cycle_id()
        if not cycle_id:
            raise ValueError("Aucun cycle trouvé pour cet utilisateur.")

        print(f'cycle_id : {cycle_id}')
        # Calculer la date de la prochaine période
        start_date = datetime.strptime(date_debut, "%d/%m/%Y")
        next_period = start_date + timedelta(days=dure_cycle)

        # Utiliser NotificationsModel pour générer les notifications
        notification_model = NotificationsModel()
        notification_model.generer_notification(cycle_id, start_date.strftime('%Y-%m-%d'), next_period.strftime('%Y-%m-%d'))
        
        print(f"Notifications créées avec succès pour l'utilisateur {sender_id}.")
        
    except ValueError as e:
        print(f"Erreur lors de la création de notification pour {sender_id} : {str(e)}")
    except Exception as e:
        print(f"Erreur inattendue lors de la création de notification pour {sender_id} : {str(e)}")

    # Nettoyer les variables temporaires
    query.del_temp(sender_id, 'date_debut')
    query.del_temp(sender_id, 'dure_cycle')


@ampalibe.crontab('* * * * *')
async def envoie_notifications():
    try:
        # Récupérer les notifications non envoyées pour aujourd'hui
        notifications = query.verifier_notification_a_envoyer()

        print("Notifications à envoyer:", notifications)  # Vérification du contenu

        # Vérifier si notifications est une liste
        if isinstance(notifications, list):
            # Parcourir chaque notification
            for notification in notifications:
                # Vérification si la notification est un tuple
                if isinstance(notification, tuple) and len(notification) == 3:
                    notification_id = notification[0]  # Accéder par indice
                    cycle_id = notification[1]          # Accéder par indice
                    zone_type = notification[2]         # Accéder par indice

                    # Récupérer le messenger_id associé au cycle_id
                    messenger_id = query.get_messenger_id(cycle_id)

                    if messenger_id:
                        # Récupérer les dates d'ovulation et de fin des règles
                        ovulation, fin_regles = query.get_rappel(cycle_id)

                        # Envoyer un message basé sur le zone_type
                        if zone_type == 'orange':
                            chat.send_text(messenger_id, "🟧 Rappel du cycle: \nAttention, tu es en zone 🟠 aujourd'hui. C'est une période où tu pourrais être fertile, reste attentive à ton corps")
                        elif zone_type == 'verte':
                            chat.send_text(messenger_id, "🟩 Rappel de cycle : \nAujourd'hui, tu es en zone 🟢. C'est une phase peu fertile. Profite de ta journée en toute tranquillité !")
                        elif zone_type == 'rouge':
                            chat.send_text(messenger_id, "🟥 Rappel de cycle : \nAujourd'hui, tu es en zone 🔴. Cela signifie que tu es soit en menstruation || soit dans une phase fertile élevée. Prends soin de toi.")
                        else:
                            chat.send_text(messenger_id, "Rappel de cycle : informations de zone inconnues.")

                        # Ajouter les informations sur l'ovulation et la fin des règles
                        if ovulation and fin_regles:
                            chat.send_text(messenger_id, f"⚠️ Ton ovulation est prévue le {ovulation}. Tes prochaines règles devraient arriver autour du {fin_regles}.")
                        else:
                            chat.send_text(messenger_id, "Les informations sur l'ovulation et les règles ne sont pas disponibles.")

                        # Marquer la notification comme envoyée
                        query.marquer_comme_envoyee(notification_id)
                        print(f"Notification envoyée avec succès à {messenger_id} (zone: {zone_type}).")
                    else:
                        print(f"Aucun utilisateur trouvé pour le cycle_id {cycle_id}")
                else:
                    print(f"La notification n'est pas un tuple valide : {notification}")
        else:
            print(f"Les notifications ne sont pas sous forme de liste : {notifications}")

    except Exception as e:
        print(f"Erreur lors de l'envoi des notifications : {str(e)}")





# # Planification pour exécuter la fonction toutes les minutes
# crontab('* * * * *', func=envoie_notifications, loop=ampalibe.core.loop)
    
# def send_notifications_all_users():
#     try:
#         # Récupérer la liste des utilisateurs
#         all_users = query.get_list_user()

#         # Parcourir chaque utilisateur et envoyer une notification simple
#         for user in all_users:
#             sender_id = user  # Chaque 'user' contient uniquement le messenger_id
#             chat.send_text(sender_id, "Ceci est un rappel pour votre cycle menstruel.")

#     except Exception as e:
#         print(f"Erreur lors de l'envoi des notifications : {str(e)}")


