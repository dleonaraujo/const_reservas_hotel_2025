from flask import Flask, jsonify
from flask_cors import CORS
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
from routes.auth_routes import auth_bp, init_google_client
from routes.usuarios_routes import usuarios_bp
from routes.habitaciones_routes import habitaciones_bp
from routes.reservas_routes import reservas_bp
from routes.reportes_routes import reportes_bp
from routes.servicios_routes import servicios_bp
from routes.clientes_routes import clientes_bp
from routes.tipo_habitacion_routes import tipo_habitacion_bp
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SWAGGER'] = SWAGGER
    app.config['JWT_SECRET_KEY'] = '123456'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
    app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET
    app.config['GOOGLE_DISCOVERY_URL'] = GOOGLE_DISCOVERY_URL
    app.config["FRONTEND_URL"] = "https://const-reservas-hotel-front-2025.vercel.app"

    # Permitir frontend
    
    # DESCOMENTAR LA SIGUIENTE LINEA PARA USAR EN PRODUCCION
    CORS(app, origins=["https://const-reservas-hotel-front-2025.vercel.app"], supports_credentials=True)

    # DESCOMENTAR LA SIGUIENTE LINEA PARA USAR EN LOCAL
    # CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    

    # Inicializa extensiones
    swagger = Swagger(app)
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)

    init_google_client(app)

    # Registra rutas
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(habitaciones_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(tipo_habitacion_bp)

    @app.route('/')
    def home():
        return jsonify({
            "ok": True,
            "message": "API Hotel running. Visita /apidocs para Swagger UI"
        })

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
