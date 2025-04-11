import argparse
import psycopg
from getpass import getpass

from create_DB import check_password, DB_NAME, DB_USER, DB_HOST, DB_PORT
from models import User, Message

def list_messages(username, password):
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

            if not check_password(password, user.hashed_password):
                print("Incorrect password!")
                return

            messages = Message.load_all_messages(cur)
            found = False
            for msg in messages:
                if msg.to_id == user.id:
                    found = True
                    sender = User.load_user_by_id(cur, msg.from_id)
                    print(f"\nFrom: {sender.username}")
                    print(f"Date: {msg.creation_date}")
                    print(f"Message: {msg.text}")
            if not found:
                print("No messages found.")

def send_message(from_username, password, to_username, text):
    if len(text) > 255:
        print("Message too long! Max 255 characters.")
        return

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            sender = User.load_user_by_username(cur, from_username)
            if not sender:
                print("Sender does not exist.")
                return

            if not check_password(password, sender.hashed_password):
                print("Incorrect password!")
                return

            recipient = User.load_user_by_username(cur, to_username)
            if not recipient:
                print("Recipient does not exist.")
                return

            message = Message(sender.id, recipient.id, text)
            message.save_to_db(cur)
            print("Message sent.")

def main():
    parser = argparse.ArgumentParser(description="Messaging CLI")
    parser.add_argument("-u", "--username", help="Your username")
    parser.add_argument("-p", "--password", help="Your password")
    parser.add_argument("-t", "--to", help="Recipient username")
    parser.add_argument("-s", "--send", help="Message to send")
    parser.add_argument("-l", "--list", action="store_true", help="List messages")

    args = parser.parse_args()

    global DB_PASSWORD
    DB_PASSWORD = getpass("Enter your PostgreSQL password: ")

    if args.username and args.password and args.list:
        list_messages(args.username, args.password)
    elif args.username and args.password and args.to and args.send:
        send_message(args.username, args.password, args.to, args.send)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
