class DatabaseService:
    def query(self, user_id):
        return {"id": user_id, "name": "Test User"}

    def save(self, data):
        return True

    def delete(self, user_id):
        return True
