from ampalibe import Model
from datetime import datetime

class UserModel(Model):
    def __init__(self, sender_id):
        super().__init__()
        self.sender_id = sender_id
        self.created_at = datetime.now()  # Assigner l'heure actuelle

