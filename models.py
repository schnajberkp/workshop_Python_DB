from datetime import datetime
from create_DB import hash_password, check_password 

class User:
    def __init__(self, username, hashed_password=None):
        self._id = -1
        self.username = username
        self._hashed_password = hashed_password

    @property
    def id(self):
        return self._id
    
    @property
    def hashed_password(self):
        return self._hashed_password
    
    def set_password(self, password):
        #Sets the password and hashes it
        self._hashed_password = hash_password(password)
    def save_to_db(self, cursor):
        """
        Saves the user to the database
        If it has ID -1, create a new user
        Else update the existing user
        """
        if self._id == -1:
            # New user, insert into the database
            cursor.execute(
                "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id",
                (self.username, self._hashed_password)
            )
            self._id = cursor.fetchone()[0] # Get ID from DB
        else:
            # Existing user, update the database
            cursor.execute(
                "UPDATE users SET username=%s, hashed_password=%s WHERE id=%s",
                (self.username, self._hashed_password, self._id)
            )
    @staticmethod
    def load_user_by_username(cursor, username):
        #Loads user by username
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE username=%s",(username,)
        )
        data = cursor.fetchone()
        if data:
            user = User(data[1], data[2])
            user._id = data[0]
            return user
        return None
    @staticmethod
    def load_user_by_id(cursor, user_id):
        #Loads user by ID
        cursor.execute(
            "SELECT id, username, hashed_password FROM users WHERE id=%s",(user_id,)
        )
        data = cursor.fetchone()
        if data:
            user = User(data[1], data[2])
            user._id = data[0]
            return user
        return None

    @staticmethod
    def load_all_users(cursor):
        # Loads all users
        cursor.execute("SELECT id, username, hashed_password FROM users")
        users = []
        for row in cursor.fetchall():
            user = User(row[1], row[2])
            user._id = row[0]
            users.append(user)
        return users
    def delete(self, cursor):
        # Deletes the user from the database
        if self._id != -1:
            cursor.execute("DELETE FROM users WHERE id=%s", (self._id,))
            self._id = -1 # Resets ID after deletion

class Message:
    def __init__(self, from_id, to_id, text):
        self._id = -1 #Default ID before saving to DB
        self.from_id = from_id # Sender ID
        self.to_id = to_id # Receiver ID
        self.text = text # Message text
        self.creation_date = None # Creation date, to be set by DB

    @property
    def id(self):
        return self._id
    
    def save_to_db(self, cursor):
        """
        Saves the message to the database
        If its new, insert into the database and set creation_date
        Else update the existing message (has ID)
        """
        if self._id == -1:
            cursor.execute(
                """
                INSERT INTO messages (from_id, to_id, creation_date, text)
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
                RETURNING id, creation_date
                """, 
                (self.from_id, self.to_id, self.text)
            )
            result = cursor.fetchone()
            self._id = result[0]
            self.creation_date = result[1]
        else:
            cursor.execute("UPDATE messages SET text= %s WHERE Id=%s", (self.text, self._id))
    @staticmethod
    def load_all_messages(cursor):
        # Loads all messages from database a return list of message objects
        cursor.execute("SELECT id, from_id, to_id, creation_date, text FROM messages")
        messages = []
        for row in cursor.fetchall():
            message = Message(row[1], row[2], row[4])
            message._id = row[0]
            message.creation_date = row[3]
            messages.append(message)
        return messages