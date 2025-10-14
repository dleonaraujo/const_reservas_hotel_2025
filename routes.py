from flask import Blueprint, request, jsonify
from models import db, Usuario, Cliente, Habitacion, Reserva, DetalleReserva, Pago, Servicio
from schemas import UsuarioSchema
from flasgger import swag_from

api = Blueprint('api', __name__, url_prefix='/api')

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)


# --- CRUD Usuarios ---
@api.route('/usuarios', methods=['POST'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Crear un nuevo usuario',
    'description': 'Crea un usuario con su nombre, username y role_id.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    'username': 'admin',
                    'nombre': 'Administrador',
                    'role_id': 1
                }
            }
        }
    },
    'responses': {201: {'description': 'Usuario creado exitosamente'}}
})
def create_usuario():
    data = request.json
    u = Usuario(username=data['username'], nombre=data.get('nombre'), role_id=data.get('role_id'))
    db.session.add(u)
    db.session.commit()
    return jsonify(usuario_schema.dump(u)), 201


@api.route('/usuarios', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Listar todos los usuarios',
    'responses': {200: {'description': 'Lista de usuarios obtenida'}}
})
def list_usuarios():
    all_u = Usuario.query.all()
    return jsonify(usuarios_schema.dump(all_u)), 200


@api.route('/usuarios/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Obtener un usuario por ID',
    'parameters': [{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}],
    'responses': {200: {'description': 'Usuario encontrado'}}
})
def get_usuario(id):
    u = Usuario.query.get_or_404(id)
    return jsonify(usuario_schema.dump(u))


@api.route('/usuarios/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Actualizar un usuario existente',
    'parameters': [{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    'username': 'nuevo_user',
                    'nombre': 'Usuario Editado',
                    'role_id': 2
                }
            }
        }
    },
    'responses': {200: {'description': 'Usuario actualizado exitosamente'}}
})
def update_usuario(id):
    u = Usuario.query.get_or_404(id)
    data = request.json
    u.nombre = data.get('nombre', u.nombre)
    u.username = data.get('username', u.username)
    u.role_id = data.get('role_id', u.role_id)
    db.session.commit()
    return jsonify(usuario_schema.dump(u))


@api.route('/usuarios/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Eliminar un usuario por ID',
    'parameters': [{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}],
    'responses': {204: {'description': 'Usuario eliminado'}}
})
def delete_usuario(id):
    u = Usuario.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    return '', 204


# --- Endpoint no-CRUD: Registrar pago ---
@api.route('/pagos/registrar', methods=['POST'])
@swag_from({
    'tags': ['Pagos'],
    'summary': 'Registrar un nuevo pago',
    'description': 'Registra un pago y actualiza el total de la reserva correspondiente.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    'reserva_id': 1,
                    'monto': 250.00,
                    'metodo': 'tarjeta'
                }
            }
        }
    },
    'responses': {201: {'description': 'Pago registrado correctamente'}}
})
def registrar_pago():
    data = request.json
    pago = Pago(reserva_id=data.get('reserva_id'), monto=data['monto'], metodo=data.get('metodo'))
    db.session.add(pago)
    if pago.reserva_id:
        r = Reserva.query.get(pago.reserva_id)
        if r:
            r.total = (r.total or 0) + pago.monto
    db.session.commit()
    return jsonify({'ok': True, 'pago_id': pago.id}), 201


# --- Reporte: Reservas por rango de fecha ---
@api.route('/reportes/reservas', methods=['GET'])
@swag_from({
    'tags': ['Reportes'],
    'summary': 'Obtener reservas por rango de fecha',
    'parameters': [
        {'name': 'start', 'in': 'query', 'schema': {'type': 'string', 'format': 'date'}, 'required': False},
        {'name': 'end', 'in': 'query', 'schema': {'type': 'string', 'format': 'date'}, 'required': False}
    ],
    'responses': {200: {'description': 'Reporte de reservas generado'}}
})
def reporte_reservas():
    start = request.args.get('start')
    end = request.args.get('end')
    q = Reserva.query
    if start:
        q = q.filter(Reserva.fecha_inicio >= start)
    if end:
        q = q.filter(Reserva.fecha_fin <= end)
    res = q.all()
    out = [{'id': r.id, 'cliente_id': r.cliente_id, 'inicio': str(r.fecha_inicio),
            'fin': str(r.fecha_fin), 'total': r.total} for r in res]
    return jsonify(out)


# --- Búsqueda: Habitaciones disponibles ---
@api.route('/habitaciones/disponibles', methods=['GET'])
@swag_from({
    'tags': ['Habitaciones'],
    'summary': 'Consultar habitaciones disponibles',
    'description': 'Devuelve las habitaciones disponibles entre las fechas indicadas.',
    'parameters': [
        {'name': 'start', 'in': 'query', 'schema': {'type': 'string', 'format': 'date'}, 'required': True},
        {'name': 'end', 'in': 'query', 'schema': {'type': 'string', 'format': 'date'}, 'required': True}
    ],
    'responses': {200: {'description': 'Lista de habitaciones disponibles'}}
})
def habitaciones_disponibles():
    start = request.args.get('start')
    end = request.args.get('end')
    sub = db.session.query(DetalleReserva.habitacion_id).join(Reserva).filter(
        Reserva.fecha_inicio <= end, Reserva.fecha_fin >= start
    ).subquery()
    disponibles = Habitacion.query.filter(~Habitacion.id.in_(sub)).all()
    out = [{'id': h.id, 'numero': h.numero,
            'tipo': h.tipo.nombre if h.tipo else None,
            'precio': h.precio} for h in disponibles]
    return jsonify(out)
