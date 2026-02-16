from database_service import DatabaseService
from email_service import EmailService

class UserService:
    def __init__(self, database_service, email_service):
        self.db = database_service
        self.email = email_service

    def get_user(self, user_id):
        return self.db.query(user_id)

    def create_user(self, name, email):
        user = {"name": name, "email": email}
        self.db.save(user)
        self.email.send_welcome(email)
        return user

    def delete_user(self, user_id):
        return self.db.delete(user_id)