from flask import Blueprint, request, jsonify, current_app, url_for, redirect
from models import db, Usuario
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from oauthlib.oauth2 import WebApplicationClient
import requests
from flasgger import swag_from

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

client = None

def init_google_client(app):
    global client
    client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])


# --- LOGIN NORMAL ---
@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Iniciar sesión y obtener token JWT',
    'description': 'Autentica un usuario mediante email o username y contraseña.',
})
def login():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not password or (not email and not username):
        return jsonify({'ok': False, 'msg': 'Se requiere email/username y contraseña'}), 400

    user = Usuario.query.filter_by(email=email).first() if email else Usuario.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'ok': False, 'msg': 'Credenciales inválidas'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'ok': True, 'token': token}), 200


# --- LOGIN GOOGLE ---
@auth_bp.route('/login/google')
def login_google():
    if not client:
        return jsonify({"error": "Cliente OAuth no inicializado"}), 500

    resp = requests.get(current_app.config["GOOGLE_DISCOVERY_URL"])
    if resp.status_code != 200:
        return jsonify({"error": "No se pudo obtener configuración Google"}), 500

    google_cfg = resp.json()
    authorization_endpoint = google_cfg["authorization_endpoint"]

    redirect_uri = url_for("auth_bp.callback_google", _external=True)

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)


@auth_bp.route('/login/google/callback')
def callback_google():
    if not client:
        return jsonify({"error": "Cliente OAuth no inicializado"}), 500

    code = request.args.get("code")

    google_cfg = requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()
    token_endpoint = google_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config["GOOGLE_CLIENT_ID"], current_app.config["GOOGLE_CLIENT_SECRET"]),
    )

    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = google_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if not userinfo_response.ok:
        return jsonify({"error": "No se pudo obtener info del usuario"}), 400

    user_data = userinfo_response.json()
    email = user_data.get("email")
    nombre = user_data.get("name", "")
    username = email.split("@")[0]

    user = Usuario.query.filter_by(email=email).first()
    if not user:
        user = Usuario(username=username, email=email, nombre=nombre)
        user.password_hash = generate_password_hash("sso_user")
        db.session.add(user)
        db.session.commit()

    jwt_token = create_access_token(identity=str(user.id))

    return jsonify({
        "ok": True,
        "msg": "Inicio de sesión con Google exitoso",
        "token": jwt_token,
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email
        }
    })