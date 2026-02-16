from datetime import datetime


class Database:
    def __init__(self):
        self.storage = {}

    def save(self, key, value):
        self.storage[key] = value
        return True

    def get(self, key):
        return self.storage.get(key, None)

    def delete(self, key):
        if key in self.storage:
            del self.storage[key]
            return True
        return False


class EmailService:
    def __init__(self, smtp_host):
        self.smtp_host = smtp_host

    def send_welcome(self, email):
        print(f"Sending welcome email to {email}")
        return True

    def send_reset_password(self, email, token):
        print(f"Sending reset token {token} to {email}")
        return True

    def send_notification(self, email, message):
        print(f"Notifying {email}: {message}")
        return True


class AuthService:
    def __init__(self, db):
        self.db = db
        self.active_tokens = {}

    def generate_token(self, user_id):
        token = f"token_{user_id}_{datetime.now().timestamp()}"
        self.active_tokens[user_id] = token
        return token

    def validate_token(self, token):
        return token in self.active_tokens.values()

    def revoke_token(self, user_id):
        if user_id in self.active_tokens:
            del self.active_tokens[user_id]
            return True
        return False


class UserService:
    def __init__(self, db, email_service, auth_service):
        self.db = db
        self.email_service = email_service
        self.auth_service = auth_service

    def register(self, name, email, password):
        user = {
            "name": name,
            "email": email,
            "password": password,
            "created_at": datetime.now().isoformat()
        }
        self.db.save(email, user)
        self.email_service.send_welcome(email)
        return user

    def login(self, email, password):
        user = self.db.get(email)
        if not user or user["password"] != password:
            return None
        token = self.auth_service.generate_token(email)
        return token

    def delete_account(self, email):
        self.auth_service.revoke_token(email)
        self.db.delete(email)
        return True

    def reset_password(self, email):
        token = self.auth_service.generate_token(email)
        self.email_service.send_reset_password(email, token)
        return token


class OrderService:
    def __init__(self, db, user_service, email_service):
        self.db = db
        self.user_service = user_service
        self.email_service = email_service

    def place_order(self, user_email, items):
        order = {
            "user": user_email,
            "items": items,
            "status": "placed",
            "created_at": datetime.now().isoformat()
        }
        order_id = f"order_{datetime.now().timestamp()}"
        self.db.save(order_id, order)
        self.email_service.send_notification(
            user_email,
            f"Order {order_id} placed successfully"
        )
        return order_id

    def cancel_order(self, order_id, user_email):
        self.db.delete(order_id)
        self.email_service.send_notification(
            user_email,
            f"Order {order_id} cancelled"
        )
        return True

    def get_order(self, order_id):
        return self.db.get(order_id)


class PaymentService:
    def __init__(self, db, order_service, email_service):
        self.db = db
        self.order_service = order_service
        self.email_service = email_service

    def process_payment(self, order_id, user_email, amount):
        order = self.order_service.get_order(order_id)
        if not order:
            return False
        payment = {
            "order_id": order_id,
            "amount": amount,
            "status": "paid",
            "paid_at": datetime.now().isoformat()
        }
        self.db.save(f"payment_{order_id}", payment)
        self.email_service.send_notification(
            user_email,
            f"Payment of {amount} received for order {order_id}"
        )
        return True

    def refund(self, order_id, user_email, amount):
        self.db.delete(f"payment_{order_id}")
        self.email_service.send_notification(
            user_email,
            f"Refund of {amount} processed for order {order_id}"
        )
        return True