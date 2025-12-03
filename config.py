import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES = {
    'user': os.getenv('DB_USER', 'postgres'),
    'pw': os.getenv('DB_PASS', ''),
    'db': os.getenv('DB_NAME', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
}

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES['user']}:{POSTGRES['pw']}"
    f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}?sslmode=require"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Swagger
SWAGGER = {
    'title': 'API Hotel - Sistema de Reservas',
    'uiversion': 3
}



# Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = os.getenv(
    'GOOGLE_DISCOVERY_URL',
    'https://accounts.google.com/.well-known/openid-configuration'
)
