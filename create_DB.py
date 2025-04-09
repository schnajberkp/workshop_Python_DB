import psycopg
from psycopg import sql
from psycopg.errors import DuplicateDatabase, DuplicateTable
import getpass
import hashlib
import random
import string

# Config
DB_NAME = "samba"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Charset for salt
ALPHABET = string.ascii_letters + string.digits

def generate_salt():
    """
    Generates a 16-character random salt.
    """
    return ''.join(random.choice(ALPHABET) for _ in range(16))

def hash_password(password, salt=None):
    """
    Hashes the password with optional salt.
    """
    if salt is None:
        salt = generate_salt()
    if len(salt) < 16:
        salt += "a" * (16 - len(salt))
    if len(salt) > 16:
        salt = salt[:16]

    t_sha = hashlib.sha256()
    t_sha.update(salt.encode('utf-8') + password.encode('utf-8'))
    return salt + t_sha.hexdigest()

def check_password(pass_to_check, hashed):
    """
    Checks if a given password matches the hash.
    """
    salt = hashed[:16]
    hash_to_check = hashed[16:]
    new_hash = hash_password(pass_to_check, salt)
    return new_hash[16:] == hash_to_check

def create_database(db_password):
    try:
        with psycopg.connect(
            dbname="postgres",
            user=DB_USER,
            password=db_password,
            host=DB_HOST,
            port=DB_PORT,
            autocommit=True  # needed to create databases
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print(f"Database '{DB_NAME}' created successfully.")
    except DuplicateDatabase:
        print(f"Database '{DB_NAME}' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")

def create_tables(db_password):
    try:
        with psycopg.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=db_password,
            host=DB_HOST,
            port=DB_PORT,
            autocommit=True
        ) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        CREATE TABLE users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            hashed_password VARCHAR(80) NOT NULL
                        );
                    """)
                    print("Table 'users' created successfully.")
                except DuplicateTable:
                    print("Table 'users' already exists.")

                try:
                    cur.execute("""
                        CREATE TABLE messages (
                            id SERIAL PRIMARY KEY,
                            from_id INTEGER REFERENCES users(id),
                            to_id INTEGER REFERENCES users(id),
                            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    print("Table 'messages' created successfully.")
                except DuplicateTable:
                    print("Table 'messages' already exists.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    print("Enter your PostgreSQL password:")
    DB_PASSWORD = getpass.getpass()

    create_database(DB_PASSWORD)
    create_tables(DB_PASSWORD)
