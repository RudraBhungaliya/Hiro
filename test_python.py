
class UserService:
    def __init__(self, database):
        self.db = database
    
    def get_user(self, user_id):
        return self.db.query(user_id)
    
    def create_user(self, name, email):
        return self.db.insert({'name': name, 'email': email})

class DatabaseService:
    def query(self, id):
        pass
    
    def insert(self, data):
        pass
