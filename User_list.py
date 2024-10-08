from ampalibe import Model

class CustomModel(Model):
    def __init__(self):
        super().__init__()

    @Model.verif_db
    def add_user(self):
        '''
            Method to add a static user
        '''
        req = "INSERT INTO users (messenger_id, name, communication_channel) VALUES ('123456787', 'StaticUser', 'Messenger')"
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