from flask import Blueprint, request, jsonify
from models import db, Usuario, Cliente, Habitacion, Reserva, DetalleReserva, Pago, Servicio
from schemas import UsuarioSchema
from flasgger import swag_from

api = Blueprint('api', __name__, url_prefix='/api')

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# --- CRUD Usuarios (ejemplo) ---
@api.route('/usuarios', methods=['POST'])
@swag_from({
    'tags': ['Usuarios'],
    'parameters': [{'in':'body','schema':UsuarioSchema}],
    'responses': {201: {'description':'Creado'}}
})
def create_usuario():
    data = request.json
    u = Usuario(username=data['username'], nombre=data.get('nombre'), role_id=data.get('role_id'))
    db.session.add(u)
    db.session.commit()
    return usuario_schema.jsonify(u), 201

@api.route('/usuarios', methods=['GET'])
def list_usuarios():
    all_u = Usuario.query.all()
    return usuarios_schema.jsonify(all_u), 200

@api.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    u = Usuario.query.get_or_404(id)
    return usuario_schema.jsonify(u)

@api.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    u = Usuario.query.get_or_404(id)
    data = request.json
    u.nombre = data.get('nombre', u.nombre)
    u.username = data.get('username', u.username)
    u.role_id = data.get('role_id', u.role_id)
    db.session.commit()
    return usuario_schema.jsonify(u)

@api.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    u = Usuario.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    return '', 204

# --- Endpoint no-CRUD: registrar pago ---
@api.route('/pagos/registrar', methods=['POST'])
@swag_from({
    'tags': ['Pagos'],
})
def registrar_pago():
    data = request.json
    pago = Pago(reserva_id=data.get('reserva_id'), monto=data['monto'], metodo=data.get('metodo'))
    db.session.add(pago)
    # actualizar reserva -> sumar al total
    if pago.reserva_id:
        r = Reserva.query.get(pago.reserva_id)
        if r:
            r.total = (r.total or 0) + pago.monto
    db.session.commit()
    return jsonify({'ok': True, 'pago_id': pago.id}), 201

# --- Reporte: reservas por rango de fecha ---
@api.route('/reportes/reservas', methods=['GET'])
def reporte_reservas():
    start = request.args.get('start')
    end = request.args.get('end')
    q = Reserva.query
    if start:
        q = q.filter(Reserva.fecha_inicio >= start)
    if end:
        q = q.filter(Reserva.fecha_fin <= end)
    res = q.all()
    # serializa manualmente breve
    out = [{'id': r.id, 'cliente_id': r.cliente_id, 'inicio': str(r.fecha_inicio), 'fin': str(r.fecha_fin), 'total': r.total} for r in res]
    return jsonify(out)

# --- Búsqueda: habitaciones disponibles entre fechas ---
@api.route('/habitaciones/disponibles', methods=['GET'])
def habitaciones_disponibles():
    start = request.args.get('start')
    end = request.args.get('end')
    # lógica simple: habitaciones que no están en reservas entre fechas
    sub = db.session.query(DetalleReserva.habitacion_id).join(Reserva).filter(
        Reserva.fecha_inicio <= end, Reserva.fecha_fin >= start
    ).subquery()
    disponibles = Habitacion.query.filter(~Habitacion.id.in_(sub)).all()
    out = [{'id': h.id, 'numero': h.numero, 'tipo': h.tipo.nombre if h.tipo else None, 'precio': h.precio} for h in disponibles]
    return jsonify(out)
