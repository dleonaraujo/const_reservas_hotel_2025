
from flask import Flask, jsonify
from config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SWAGGER,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_DISCOVERY_URL
)
from models import db
from flasgger import Swagger

from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from routes.auth_routes import auth_bp,init_google_client
from routes.usuarios_routes import usuarios_bp
from routes.habitaciones_routes import habitaciones_bp
from routes.reservas_routes import reservas_bp
from routes.reportes_routes import reportes_bp
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SWAGGER'] = SWAGGER

    #  Configuración JWT
    app.config['JWT_SECRET_KEY'] = '123456'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400

    #  Configuración OAuth de Google
    app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET
    app.config['GOOGLE_DISCOVERY_URL'] = GOOGLE_DISCOVERY_URL

    # Inicializa extensiones
    swagger = Swagger(app)
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)

    #  Inicializa el cliente de Google OAuth después de crear la app
    init_google_client(app)

    # Registra rutas
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(habitaciones_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(reportes_bp)

    @app.route('/')
    def home():
        return jsonify({
            "ok": True,
            "message": "API Hotel running. Visita /apidocs para Swagger UI"
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)