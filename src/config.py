import os

from dotenv import load_dotenv

load_dotenv()


def get_secrets():
    return {'client_id': os.getenv('CLIENT_ID'), 'client_secret': os.getenv('CLIENT_SECRET')}

def get_redirect_uri():
    return os.getenv('REDIRECT_URI')

def get_bot_token():
    return os.getenv('BOT_TOKEN')