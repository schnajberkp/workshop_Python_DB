import argparse
import psycopg
from psycopg.errors import UniqueViolation
from getpass import getpass

from create_DB import check_password, DB_NAME, DB_USER, DB_HOST, DB_PORT
from models import User

MIN_PASSWORD_LENGTH = 8

def create_user(username, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        print("Password must be at least 8 characters long.")
        return

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            existing_user = User.load_user_by_username(cur, username)
            if existing_user:
                print("User already exists.")
                return

            user = User(username)
            user.set_password(password)
            try:
                user.save_to_db(cur)
                print(f"User '{username}' created successfully.")
            except UniqueViolation:
                print("User already exists.")

def edit_password(username, password, new_password):
    if len(new_password) < MIN_PASSWORD_LENGTH:
        print("New password must be at least 8 characters long.")
        return

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            user = User.load_user_by_username(cur, username)
            if not user:
                print("User does not exist.")
                return

            if check_password(password, user.hashed_password):
                user.set_password(new_password)
                user.save_to_db(cur)
                print("Password updated.")
            else:
                print("Incorrect password!")

def delete_user(username, password):
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            user = User.load_user_by_username(cur, username)
            if not user:
                print("User does not exist.")
                return

            if check_password(password, user.hashed_password):
                user.delete(cur)
                print(f"User '{username}' deleted.")
            else:
                print("Incorrect password!")

def list_users():
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            users = User.load_all_users(cur)
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}")

def main():
    parser = argparse.ArgumentParser(description="User management CLI.")
    parser.add_argument("-u", "--username", help="Username")
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument("-n", "--new_pass", help="New password")
    parser.add_argument("-l", "--list", action="store_true", help="List all users")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete user")
    parser.add_argument("-e", "--edit", action="store_true", help="Edit user password")

    args = parser.parse_args()

    # Získání hesla k PostgreSQL
    global DB_PASSWORD
    DB_PASSWORD = getpass("Enter your PostgreSQL password: ")

    if args.list:
        list_users()
    elif args.username and args.password and args.delete:
        delete_user(args.username, args.password)
    elif args.username and args.password and args.edit and args.new_pass:
        edit_password(args.username, args.password, args.new_pass)
    elif args.username and args.password and not args.edit and not args.delete and not args.new_pass:
        create_user(args.username, args.password)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
