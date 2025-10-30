from flask import Blueprint, request, jsonify, current_app
from models import db, Usuario, Cliente, Habitacion, Reserva, DetalleReserva, Pago, Servicio, TipoHabitacion
from flasgger import swag_from
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Iniciar sesión y obtener token JWT',
    'description': 'Autentica un usuario mediante correo electrónico o username y contraseña. Devuelve un token JWT válido por 24 horas.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    'email': 'admin@hotel.com',
                    'password': '123456'
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Inicio de sesión exitoso'},
        401: {'description': 'Credenciales inválidas'}
    }
})
def login():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not password or (not email and not username):
        return jsonify({'ok': False, 'msg': 'Se requiere email o username y contraseña'}), 400

    # Buscar por email o username
    user = None
    if email:
        user = Usuario.query.filter_by(email=email).first()
    elif username:
        user = Usuario.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'ok': False, 'msg': 'Credenciales inválidas'}), 401

    # Crear token
    token = create_access_token(identity=str(user.id))
    return jsonify({'ok': True, 'token': token}), 200

@api.route('/login/google')
def login_google():
    google_cfg = requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()
    authorization_endpoint = google_cfg["authorization_endpoint"]

    redirect_uri = url_for("api.callback_google", _external=True)

    return redirect(
        f"{authorization_endpoint}?client_id={current_app.config['GOOGLE_CLIENT_ID']}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid%20email%20profile"
        f"&response_type=code"
    )

@api.route('/login/google/callback')
def callback_google():
    code = request.args.get("code")
    google_cfg = requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()
    token_endpoint = google_cfg["token_endpoint"]

    token_data = {
        "code": code,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": url_for("api.callback_google", _external=True),
        "grant_type": "authorization_code"
    }

    token_response = requests.post(token_endpoint, data=token_data).json()
    access_token = token_response.get("access_token")


    userinfo_endpoint = google_cfg["userinfo_endpoint"]
    userinfo = requests.get(userinfo_endpoint, headers={
        "Authorization": f"Bearer {access_token}"
    }).json()

    email = userinfo["email"]
    nombre = userinfo.get("name", "")
    username = email.split("@")[0]


    user = Usuario.query.filter_by(email=email).first()
    if not user:
        user = Usuario(username=username, email=email, nombre=nombre)
        user.password_hash = generate_password_hash("sso_user")  # valor simbólico
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


# --- CRUD Usuarios ---
@api.route('/usuarios', methods=['POST'])
@jwt_required()
def create_usuario():
    """Crear usuario con password encriptado"""
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'ok': False, 'msg': 'Username y password son obligatorios'}), 400

    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'ok': False, 'msg': 'El usuario ya existe'}), 400

    u = Usuario(
        username=data['username'],
        nombre=data.get('nombre'),
        email=data.get('email'),
        role_id=data.get('role_id')
    )
    u.set_password(data['password'])
    db.session.add(u)
    db.session.commit()
    return jsonify({'ok': True, 'msg': 'Usuario creado exitosamente'}), 201


@api.route('/usuarios', methods=['GET'])
@jwt_required()
def list_usuarios():
    all_u = Usuario.query.all()
    out = [{'id': u.id, 'username': u.username, 'nombre': u.nombre, 'email': u.email, 'role_id': u.role_id} for u in all_u]
    return jsonify(out), 200


# --- Habitaciones disponibles corregido ---
@api.route('/habitaciones/disponibles', methods=['GET'])
@jwt_required()
def habitaciones_disponibles():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'ok': False, 'msg': 'Debe proporcionar start y end'}), 400

    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'ok': False, 'msg': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400

    # Subconsulta para habitaciones reservadas en el rango
    sub = db.session.query(DetalleReserva.habitacion_id).join(Reserva).filter(
        Reserva.fecha_inicio <= end_date,
        Reserva.fecha_fin >= start_date
    ).subquery()

    disponibles = Habitacion.query.filter(~Habitacion.id.in_(sub)).all()
    out = [{
        'id': h.id,
        'numero': h.numero,
        'tipo': h.tipo.nombre if h.tipo else None,
        'precio': h.precio,
        'estado': h.estado
    } for h in disponibles]
    return jsonify(out), 200


# --- Registrar reserva ---
@api.route('/reservas/registrar', methods=['POST'])
@jwt_required()
def registrar_reserva():
    data = request.json
    cliente_id = data.get('cliente_id')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    habitaciones = data.get('habitaciones', [])

    if not all([cliente_id, fecha_inicio, fecha_fin, habitaciones]):
        return jsonify({'ok': False, 'msg': 'Datos incompletos para crear la reserva'}), 400

    r = Reserva(
        cliente_id=cliente_id,
        fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
        fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d').date(),
        estado='planificada',
        total=0
    )
    db.session.add(r)
    db.session.flush()  # para obtener ID antes del commit

    total = 0
    for hab_id in habitaciones:
        h = Habitacion.query.get(hab_id)
        if not h:
            continue
        d = DetalleReserva(reserva_id=r.id, habitacion_id=h.id, precio=h.precio)
        total += h.precio
        db.session.add(d)

    r.total = total
    db.session.commit()
    return jsonify({'ok': True, 'reserva_id': r.id, 'total': total}), 201


# --- Cancelar reserva ---
@api.route('/reservas/<int:id>/cancelar', methods=['PUT'])
@jwt_required()
def cancelar_reserva(id):
    r = Reserva.query.get_or_404(id)
    if r.estado == 'cancelada':
        return jsonify({'ok': False, 'msg': 'La reserva ya está cancelada'}), 400
    r.estado = 'cancelada'
    db.session.commit()
    return jsonify({'ok': True, 'msg': 'Reserva cancelada correctamente'}), 200


# --- Actualizar reserva ---
@api.route('/reservas/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_reserva(id):
    r = Reserva.query.get_or_404(id)
    data = request.json
    if 'fecha_inicio' in data:
        r.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
    if 'fecha_fin' in data:
        r.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
    if 'estado' in data:
        r.estado = data['estado']
    db.session.commit()
    return jsonify({'ok': True, 'msg': 'Reserva actualizada correctamente'}), 200


# --- Reportes ---
@api.route('/reportes/reservas-por-estado', methods=['GET'])
@jwt_required()
def reporte_reservas_por_estado():
    resultados = db.session.query(Reserva.estado, db.func.count(Reserva.id)).group_by(Reserva.estado).all()
    return jsonify([{'estado': e, 'cantidad': c} for e, c in resultados]), 200


@api.route('/reportes/ingresos', methods=['GET'])
@jwt_required()
def reporte_ingresos():
    resultados = db.session.query(
        db.func.date(Pago.fecha).label('fecha'),
        db.func.sum(Pago.monto)
    ).group_by(db.func.date(Pago.fecha)).all()

    return jsonify([{'fecha': str(f), 'ingresos': float(i)} for f, i in resultados]), 200


@api.route('/reportes/habitaciones-populares', methods=['GET'])
@jwt_required()
def reporte_habitaciones_populares():
    resultados = db.session.query(
        Habitacion.numero,
        db.func.count(DetalleReserva.id)
    ).join(DetalleReserva).group_by(Habitacion.numero).order_by(db.func.count(DetalleReserva.id).desc()).limit(10).all()

    return jsonify([{'habitacion': n, 'reservas': c} for n, c in resultados]), 200