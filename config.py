import os

POSTGRES = {
    'user': os.getenv('DB_USER','postgres'),
    'pw': os.getenv('DB_PASS','123456'),
    'db': os.getenv('DB_NAME','hotel_db'),
    'host': os.getenv('DB_HOST','localhost'),
    'port': os.getenv('DB_PORT','5432'),
}

SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES['user']}:{POSTGRES['pw']}@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SWAGGER = {
    'title': 'API Hotel - Sistema de Reservas',
    'uiversion': 3
}
