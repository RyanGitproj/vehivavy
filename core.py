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
import redis

# Initialisation de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Fonctions auxiliaires pour gérer les données temporaires
def set_temp_data(user_id, key, value, expiration=3600):
    """
    Stocke une donnée temporaire dans Redis avec une expiration (par défaut 1 heure).
    """
    redis_client.setex(f"{user_id}:{key}", expiration, value)

def get_temp_data(user_id, key):
    """
    Récupère une donnée temporaire depuis Redis.
    """
    return redis_client.get(f"{user_id}:{key}")

def del_temp_data(user_id, key):
    """
    Supprime une donnée temporaire dans Redis.
    """
    redis_client.delete(f"{user_id}:{key}")

def schedule_notification(user_id, message, send_date):
    """
    Planifie une notification en la stockant dans Redis avec une date d'envoi.
    """
    redis_client.zadd("notifications", {f"{user_id}:{message}": send_date.timestamp()})

def get_due_notifications():
    """
    Récupère les notifications qui doivent être envoyées maintenant ou avant.
    """
    current_time = datetime.now().timestamp()
    return redis_client.zrangebyscore("notifications", 0, current_time)

def remove_notification(notification_key):
    """
    Supprime une notification après son envoi.
    """
    redis_client.zrem("notifications", notification_key)

def get_cached_data(key):
    """Récupère les données du cache"""
    return redis_client.get(key)

def set_cached_data(key, value, expiration=3600):
    """Ajoute des données dans le cache avec une expiration"""
    redis_client.set(key, value, ex=expiration)

def delete_cached_data(key):
    """Supprime une donnée dans le cache"""
    redis_client.delete(key)

chat = Messenger()
query = CustomModel()


# Démarrer
chat.get_started()

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.mark_seen)

    # Initialisation du modèle utilisateur
    user_request = UserModel(sender_id)

    # Récupérer les données utilisateur
    result = user_request.get_user()

    # Vérifier si le cycle a été saisi
    if result and result.get('cycle_saisi') == 1:
        buttons = [
            Button(type=Type.postback, title='Oui', payload=Payload('/update_cycle')),
            Button(type=Type.postback, title='Non', payload=Payload('/no_update')),
        ]
        chat.send_button(sender_id, buttons, "Souhaites-tu mettre à jour ton cycle ?")
    else:
        buttons = [
            Button(type=Type.postback, title='Oui', payload=Payload('/saisie_date')),
            Button(type=Type.postback, title='Non', payload=Payload('/')),
        ]
        chat.send_button(
            sender_id, buttons, "Bonjour ! Je suis là pour t'aider à suivre ton cycle menstruel. Veux-tu commencer ?"
        )

    # Enregistrer l'utilisateur si ce n'est pas déjà fait
    if not user_request.is_user_exists():
        user_request.ajout_user()
        print("Nouvel utilisateur ajouté.")
    else:
        print("L'utilisateur est déjà enregistré.")


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

            # Convertir la date saisie en objet datetime
            date_debut = datetime(year, month, day).date()
            today = datetime.now().date()
            trois_mois_en_arriere = today - timedelta(days=45)

            # Vérification que la date est dans les 3 derniers mois et pas après aujourd'hui
            if date_debut < trois_mois_en_arriere:
                raise ValueError("La date ne peut pas être antérieure à 45 jours.")
            if date_debut > today:
                raise ValueError("La date ne peut pas être dans le futur.")

            # Si tout est correct, enregistrer la date
            set_temp_data(sender_id, 'date_debut', cmd)
            chat.send_text(sender_id, "Quel est la durée de votre dernier cycle en jours ? (par exemple: 30)")
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
        
        # Vérification que la durée du cycle est entre 21 et 45 jours
        if dure_cycle < 21 or dure_cycle > 45:
            raise ValueError("La durée du cycle doit être comprise entre 21 et 45 jours.")

        set_temp_data(sender_id, 'dure_cycle', dure_cycle)

        # Mise à jour de cycle_saisi à 1
        user_request = UserModel(sender_id)  # Initialiser le modèle utilisateur
        user_request.update_cycle_saisi(1)  # Met cycle_saisi à 1

        # Passer ensuite à la confirmation après avoir envoyé ce message
        confirmation(sender_id)
    except ValueError as e:
        # chat.send_text(sender_id, str(e) + " Merci de réessayer en entrant un nombre entier entre 21 et 45.")
        chat.send_text(sender_id, " Merci de réessayer avec une valeur entre 21 et 45.")
        query.set_action(sender_id, "/get_dure")
    print(cmd)



def confirmation(sender_id, **ext):
    query.set_action(sender_id, None)
    debut_date = query.get_temp(sender_id, 'date_debut')
    cycle_dure = query.get_temp(sender_id, 'dure_cycle')
    chat.send_text(sender_id, f'Merci ! Tes dernières règles ont commencé le {debut_date} et ont duré {cycle_dure} jours. Je vais t\'envoyer des rappels pour les phases importantes de ton cycle, ainsi que des notifications quotidiennes sur ta zone.')
    chat.send_text(sender_id, 
               "Pour mieux comprendre ton cycle menstruel, voici une explication des différentes zones et leurs significations :\n\n"
               f"🟩 Zone Verte 🟢 : Période peu fertile. C'est une phase où il y a moins de chances de concevoir."
               f"\n🟧 Zone Orange 🟠 : Période ovulatoire. Cette phase correspond à la fenêtre de fertilité possible où l'ovulation approche."
               f"\n🟥 Zone Rouge 🔴 : Période fertile élevée. Cette phase est marquée par une haute probabilité de fertilité."
               f"\n🟦 Zone Bleue 🔵 : Période de menstruation. C'est la phase où tu as tes règles, avec un très faible risque de grossesse."
                )
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
    chat.send_button(sender_id, buttons, "Est-ce que les dernières règles sont bien arrivé ? Cela permettra de mettre à jour les informations.")

@ampalibe.command('/start_update')
def start_update(sender_id, cmd, **ext):
    chat.send_action(sender_id, Action.typing_on)
    chat.send_text(sender_id, "Peux-tu me donner la nouvelle date de début de tes dernières règles ? (Format: JJ/MM/AAAA)")
    query.set_action(sender_id, "/get_new_date")

@ampalibe.action('/get_new_date')
def get_new_date(sender_id, cmd, **ext):
    try:
        query.set_action(sender_id, None)

        # Vérification du format de la date (JJ/MM/AAAA)
        if re.match(r'^\d{2}/\d{2}/\d{4}$', cmd):
            day, month, year = map(int, cmd.split('/'))

            # Vérification que la date est valide
            if month < 1 or month > 12 or day < 1 or day > calendar.monthrange(year, month)[1]:
                raise ValueError("La date est invalide.")

            # Convertir la date entrée en objet datetime
            date_debut = datetime(year, month, day).date()
            today = datetime.now().date()
            trois_mois_en_arriere = today - timedelta(days=45)

            # Vérification que la date est dans la plage autorisée
            if date_debut < trois_mois_en_arriere:
                raise ValueError("La date ne peut pas être antérieure à 45 jours.")
            if date_debut > today:
                raise ValueError("La date ne peut pas être dans le futur.")

            # Si la date est valide, enregistrer la date et passer à l'étape suivante
            set_temp_data(sender_id, 'new_date_debut', cmd)
            chat.send_text(sender_id, "Quel est la durée de votre cycle en jours ? (par exemple: 30)")
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

        # Vérification que la durée du cycle est un entier
        dure_cycle = int(cmd)

        # Vérification que la durée du cycle est entre 21 et 45 jours
        if dure_cycle < 21 or dure_cycle > 45:
            raise ValueError("La durée du cycle doit être comprise entre 21 et 45 jours.")

        # Si la durée est valide, enregistrer la durée et confirmer la mise à jour
        set_temp_data(sender_id, 'new_dure_cycle', dure_cycle)
        confirmer_mise_a_jour(sender_id)

    except ValueError as e:
        # chat.send_text(sender_id, str(e) + " Merci de réessayer avec une valeur entre 21 et 45.")
        chat.send_text(sender_id, " Merci de réessayer avec une valeur entre 21 et 45.")
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
    
    # Supprimer les anciennes notifications
    notification_model = NotificationsModel()
    cycle_id = cycle_request.get_cycle_id()  # Assurez-vous que cette méthode existe
    notification_model.supprimer_notifications(cycle_id)

    # Générer de nouvelles notifications
    creation_notification(sender_id, new_start_date, new_duration)
    
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
                                f"La date probable de votre ovulation est estimée au : {resultats['date_ovulation']}\n"
                                f"Prochaine date des règles : {resultats['prochaine_date_regle']}\n")
    
    cycle_request = CyclesModel(id_user, start_date, duration, next_ovulation, next_periode, fin_regle, debut_fenetre, fin_fenetre)
    cycle_request.ajout_cycle()
    creation_notification(sender_id, start_date, dure_cycle)

def creation_notification(sender_id, date_debut, dure_cycle):
    try:
        # Créer une instance de CyclesModel pour récupérer le cycle_id
        cycle_req = UserModel(sender_id)
        cycle_id = cycle_req.trouver_cycle_id()
        if not cycle_id:
            raise ValueError("Aucun cycle trouvé pour cet utilisateur.")

        # Calculer la date de la prochaine période
        start_date = datetime.strptime(date_debut, "%d/%m/%Y")
        next_period = start_date + timedelta(days=dure_cycle)

        # Générer les notifications
        notification_model = NotificationsModel()
        notification_model.generer_notification(cycle_id, start_date.strftime('%Y-%m-%d'), next_period.strftime('%Y-%m-%d'))
        
        # Planifier la notification dans Redis
        redis_client.zadd("notifications", {
            f"{cycle_id}:orange": (start_date + timedelta(days=10)).timestamp(),  # Exemple de zone
            f"{cycle_id}:verte": (start_date + timedelta(days=20)).timestamp(),  # Exemple de zone
        })
        
        print(f"Notifications créées avec succès pour l'utilisateur {sender_id}.")
        
    except Exception as e:
        print(f"Erreur lors de la création de notification : {str(e)}")

    # Nettoyer les variables temporaires
    # query.del_temp(sender_id, 'date_debut')
    # query.del_temp(sender_id, 'dure_cycle')
        
        
@ampalibe.crontab('*/5 * * * *')
async def envoie_notifications():
    try:
        current_time = datetime.now().timestamp()
        # Récupérer les notifications dues
        due_notifications = redis_client.zrangebyscore("notifications", 0, current_time)
        
        print("Notifications à envoyer:", due_notifications)

        for notification in due_notifications:
            try:
                cycle_id, zone_type = notification.split(":")
                messenger_id = query.get_messenger_id(cycle_id)

                if messenger_id:
                    # Envoyer les messages selon la zone_type
                    if zone_type == 'orange':
                        chat.send_text(messenger_id, "🟧 Rappel du cycle: \nAttention, tu es en zone 🟠 aujourd'hui. C'est une période où tu pourrais être fertile, reste attentive à ton corps.")
                    elif zone_type == 'verte':
                        chat.send_text(messenger_id, "🟩 Rappel de cycle : \nAujourd'hui, tu es en zone 🟢. C'est une phase peu fertile. Profite de ta journée en toute tranquillité !")
                    elif zone_type == 'rouge':
                        chat.send_text(messenger_id, "🟥 Rappel de cycle : \nAujourd'hui, tu es en zone 🔴. Cela signifie que tu es dans une phase fertile élevée. Prends soin de toi.")
                    elif zone_type == 'bleue':
                        chat.send_text(messenger_id, "🟦 Rappel de cycle : \nTu es actuellement en période de menstruation (zone bleue 🔵), avec un très faible risque de grossesse.")
                    else:
                        chat.send_text(messenger_id, "Rappel de cycle : informations de zone inconnues.")

                    # Ajouter les informations sur l'ovulation et la fin des règles
                    ovulation, next_period = query.get_rappel(cycle_id)
                    if ovulation and next_period:
                        chat.send_text(messenger_id, f"⚠️ Date probable d'ovulation : {ovulation}. Tes prochaines règles devraient arriver autour du {next_period}.")
                    else:
                        chat.send_text(messenger_id, "Les informations sur l'ovulation et les règles ne sont pas disponibles.")


                    # Demander à l'utilisateur s'il veut recevoir une notification demain
                        chat.ask_quick_reply(
                            messenger_id,
                            "Souhaites-tu recevoir un rappel de ton cycle demain ?",
                            quick_replies=[
                                {"title": "Recevoir", "payload": "/recevoir_demain"}
                            ]
                        )
                    
                    print(f"Notification envoyée avec succès à {messenger_id} (zone: {zone_type}).")

                # Supprimer la notification après envoi
                redis_client.zrem("notifications", notification)

            except Exception as inner_e:
                print(f"Erreur lors du traitement de la notification {notification}: {str(inner_e)}")
    except Exception as e:
        print(f"Erreur lors de l'envoi des notifications : {str(e)}")


@ampalibe.action("/recevoir_demain")
def recevoir_notification_demain(sender_id, cmd, **ext):
    try:
        # Confirmer à l'utilisateur
        chat.send_text(sender_id, "Merci ! Nous t'enverrons une notification demain.")
        
        # Marquer l'utilisateur pour recevoir une notification le lendemain
        query.marquer_notification_demain(sender_id)  # Implémentez cette fonction pour enregistrer la demande.
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la demande de notification : {str(e)}")


