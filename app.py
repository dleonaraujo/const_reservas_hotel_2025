from flask import Flask, jsonify
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SWAGGER
from models import db
from flasgger import Swagger
from routes import api
from flask_migrate import Migrate   

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SWAGGER'] = {
        'title': 'API Hotel - Sistema de Reservas',
        'uiversion': 3
    }

    swagger = Swagger(app)

    db.init_app(app)
    
    Migrate(app, db)   

    app.register_blueprint(api)

    @app.route('/')
    def home():
        return jsonify({"ok": True, "message": "API Hotel running. Visita /apidocs para Swagger UI"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
