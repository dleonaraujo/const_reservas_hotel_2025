from flask import Blueprint, request, jsonify
from models import db, Usuario, Cliente, Habitacion, Reserva, DetalleReserva, Pago, Servicio
from schemas import UsuarioSchema, ClienteSchema, HabitacionSchema, ReservaSchema, PagoSchema, ServicioSchema
from flasgger import swag_from
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

# Esquemas
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)
habitacion_schema = HabitacionSchema()
habitaciones_schema = HabitacionSchema(many=True)
reserva_schema = ReservaSchema()
reservas_schema = ReservaSchema(many=True)
pago_schema = PagoSchema()
pagos_schema = PagoSchema(many=True)
servicio_schema = ServicioSchema()
servicios_schema = ServicioSchema(many=True)


# ===========================
# USUARIOS
# ===========================
@api.route('/usuarios', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Listar todos los usuarios',
    'responses': {200: {'description': 'Lista completa de usuarios'}}
})
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(usuarios))

@api.route('/usuarios/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Obtener usuario por ID',
    'parameters': [{'name': 'id', 'in': 'path', 'type': 'integer'}],
    'responses': {200: {'description': 'Usuario encontrado'}}
})
def get_usuario(id):
    u = Usuario.query.get_or_404(id)
    return jsonify(usuario_schema.dump(u))

@api.route('/usuarios', methods=['POST'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Crear nuevo usuario',
    'requestBody': {
        'required': True,
        'content': {'application/json': {'schema': UsuarioSchema}}
    },
    'responses': {201: {'description': 'Usuario creado exitosamente'}}
})
def create_usuario():
    data = request.json
    nuevo = Usuario(username=data['username'], nombre=data.get('nombre'), role_id=data.get('role_id'))
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(usuario_schema.dump(nuevo)), 201

@api.route('/usuarios/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Actualizar usuario existente',
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
    'summary': 'Eliminar usuario por ID',
})
def delete_usuario(id):
    u = Usuario.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    return '', 204


# ===========================
# CLIENTES
# ===========================
@api.route('/clientes', methods=['GET'])
@swag_from({
    'tags': ['Clientes'],
    'summary': 'Listar clientes registrados',
})
def get_clientes():
    c = Cliente.query.all()
    return jsonify(clientes_schema.dump(c))

@api.route('/clientes', methods=['POST'])
@swag_from({
    'tags': ['Clientes'],
    'summary': 'Registrar nuevo cliente',
})
def create_cliente():
    data = request.json
    c = Cliente(nombre=data['nombre'], email=data.get('email'), telefono=data.get('telefono'))
    db.session.add(c)
    db.session.commit()
    return jsonify(cliente_schema.dump(c)), 201


# ===========================
# HABITACIONES
# ===========================
@api.route('/habitaciones', methods=['GET'])
@swag_from({
    'tags': ['Habitaciones'],
    'summary': 'Listar todas las habitaciones',
})
def list_habitaciones():
    h = Habitacion.query.all()
    return jsonify(habitaciones_schema.dump(h))

@api.route('/habitaciones/disponibles', methods=['GET'])
@swag_from({
    'tags': ['Habitaciones'],
    'summary': 'Consultar habitaciones disponibles en un rango de fechas',
    'parameters': [
        {'name': 'inicio', 'in': 'query', 'type': 'string'},
        {'name': 'fin', 'in': 'query', 'type': 'string'}
    ]
})
def habitaciones_disponibles():
    start = request.args.get('inicio')
    end = request.args.get('fin')
    if not start or not end:
        return jsonify({'error': 'Debe enviar inicio y fin (YYYY-MM-DD)'}), 400

    sub = db.session.query(DetalleReserva.habitacion_id).join(Reserva).filter(
        Reserva.fecha_inicio <= end, Reserva.fecha_fin >= start
    ).subquery()

    disponibles = Habitacion.query.filter(~Habitacion.id.in_(sub)).all()
    return jsonify(habitaciones_schema.dump(disponibles))


# ===========================
# RESERVAS
# ===========================
@api.route('/reservas', methods=['GET'])
@swag_from({
    'tags': ['Reservas'],
    'summary': 'Listar todas las reservas'
})
def get_reservas():
    r = Reserva.query.all()
    return jsonify(reservas_schema.dump(r))

@api.route('/reservas', methods=['POST'])
@swag_from({
    'tags': ['Reservas'],
    'summary': 'Registrar nueva reserva',
})
def create_reserva():
    data = request.json
    r = Reserva(
        cliente_id=data['cliente_id'],
        fecha_inicio=data['fecha_inicio'],
        fecha_fin=data['fecha_fin'],
        estado=data.get('estado', 'pendiente'),
        total=data.get('total', 0)
    )
    db.session.add(r)
    db.session.commit()
    return jsonify(reserva_schema.dump(r)), 201

@api.route('/reservas/<int:id>/checkin', methods=['POST'])
@swag_from({
    'tags': ['Reservas'],
    'summary': 'Marcar una reserva como check-in'
})
def checkin(id):
    r = Reserva.query.get_or_404(id)
    r.estado = 'ocupada'
    db.session.commit()
    return jsonify({'ok': True, 'mensaje': f'Reserva {id} marcada como check-in.'})

@api.route('/reservas/<int:id>/checkout', methods=['POST'])
@swag_from({
    'tags': ['Reservas'],
    'summary': 'Marcar una reserva como check-out'
})
def checkout(id):
    r = Reserva.query.get_or_404(id)
    r.estado = 'finalizada'
    db.session.commit()
    return jsonify({'ok': True, 'mensaje': f'Reserva {id} marcada como check-out.'})

@api.route('/reservas/cliente/<int:cliente_id>', methods=['GET'])
@swag_from({
    'tags': ['Reservas'],
    'summary': 'Listar reservas por cliente',
})
def reservas_cliente(cliente_id):
    r = Reserva.query.filter_by(cliente_id=cliente_id).all()
    return jsonify(reservas_schema.dump(r))


# ===========================
# PAGOS
# ===========================
@api.route('/pagos', methods=['GET'])
@swag_from({
    'tags': ['Pagos'],
    'summary': 'Listar todos los pagos registrados',
})
def listar_pagos():
    p = Pago.query.all()
    return jsonify(pagos_schema.dump(p))

@api.route('/pagos/registrar', methods=['POST'])
@swag_from({
    'tags': ['Pagos'],
    'summary': 'Registrar nuevo pago asociado a una reserva',
})
def registrar_pago():
    data = request.json
    reserva_id = data.get('reserva_id')
    reserva = Reserva.query.get(reserva_id)
    if not reserva:
        return jsonify({'error': f'La reserva con id={reserva_id} no existe.'}), 400

    pago = Pago(reserva_id=reserva_id, monto=data['monto'], metodo=data.get('metodo'))
    db.session.add(pago)
    reserva.total = (reserva.total or 0) + pago.monto
    db.session.commit()
    return jsonify(pago_schema.dump(pago)), 201


# ===========================
# REPORTES
# ===========================
@api.route('/reportes/ocupacion', methods=['GET'])
@swag_from({
    'tags': ['Reportes'],
    'summary': 'Reporte de ocupación actual',
})
def reporte_ocupacion():
    total = Habitacion.query.count()
    ocupadas = Habitacion.query.join(DetalleReserva).join(Reserva).filter(Reserva.estado == 'ocupada').count()
    return jsonify({'ocupadas': ocupadas, 'total': total, 'porcentaje': round(ocupadas / total * 100, 2)})

@api.route('/reportes/ingresos', methods=['GET'])
@swag_from({
    'tags': ['Reportes'],
    'summary': 'Reporte de ingresos por rango de fecha',
})
def reporte_ingresos():
    start = request.args.get('inicio')
    end = request.args.get('fin')
    q = db.session.query(db.func.sum(Pago.monto))
    if start:
        q = q.filter(Pago.fecha >= start)
    if end:
        q = q.filter(Pago.fecha <= end)
    total = q.scalar() or 0
    return jsonify({'total_ingresos': float(total)})
