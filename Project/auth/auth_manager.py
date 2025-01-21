class AuthManager:
    def __init__(self, db):
        self.db = db

    def validate_password(self, password):
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not any(char.islower() for char in password):
            return "Password must contain at least one lowercase letter."
        if not any(char.isupper() for char in password):
            return "Password must contain at least one uppercase letter."
        if not any(char.isdigit() for char in password):
            return "Password must contain at least one number."
        if not any(char in "!@#$%^&*()_+" for char in password):
            return "Password must contain at least one special character."
        return "Valid"
   ## here we can create validate email function also
         

    def signup(self, username, email, password):
        return self.db.add_user(username, email, password)

    def login(self, email, password):
        return self.db.check_user(email, password)

