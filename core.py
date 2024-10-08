import ampalibe
from ampalibe import Messenger, Payload, Model
from User_list import CustomModel
from ampalibe.messenger import Action
from ampalibe.ui import Type, Button

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
    chat.send_action(sender_id,Action.typing_on)

    # Demander la date de début des règles
    chat.send_text(sender_id, "Peux-tu me donner la date de début de tes dernières règles ? (Format: JJ/MM/AAAA)")
    query.set_action(sender_id,"/get_date")

@ampalibe.action('/get_date')
def get_date(sender_id, cmd, **ext):
    query.set_action(sender_id, None)
    chat.send_text(sender_id, f'La date de votre dernier règle est le {cmd}')
    chat.send_text(sender_id, "quel est la durée de votre dernier règle?")
    query.set_action(sender_id, "/get_dure")

@ampalibe.action('/get_dure')
def get_dure(sender_id, cmd, **ext):
    query.set_action(sender_id,None)
    chat.send_text(sender_id, f'La durée de votre dernier règle est de {cmd} jours')


@ampalibe.command('/test')
def test(sender_id, cmd, **ext):
    # Ajouter un utilisateur statique dès qu'un message est reçu
    query.add_user()
    
    # Récupérer et imprimer tous les utilisateurs
    users = query.get_all_users()
    
    # Affiche la liste des utilisateurs dans la console
    print("List of users:")
    for user in users:
        print(user)