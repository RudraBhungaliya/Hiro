class EmailService:
    def send_welcome(self, email):
        print(f"Sending welcome to {email}")
        return True

    def send_notification(self, email, message):
        print(f"Notifying {email}: {message}")
        return True