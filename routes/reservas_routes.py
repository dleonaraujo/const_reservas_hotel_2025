from flask import Blueprint, jsonify, request
from models import db, Reserva, Habitacion, DetalleReserva
from flask_jwt_extended import jwt_required
from datetime import datetime

reservas_bp = Blueprint("reservas_bp", __name__, url_prefix="/api/reservas")


@reservas_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_reserva():
    data = request.json
    cliente_id = data.get('cliente_id')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    habitaciones = data.get('habitaciones', [])

    if not all([cliente_id, fecha_inicio, fecha_fin, habitaciones]):
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    r = Reserva(
        cliente_id=cliente_id,
        fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
        fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d').date(),
        estado='planificada',
        total=0
    )
    db.session.add(r)
    db.session.flush()

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


@reservas_bp.route('/<int:id>/cancelar', methods=['PUT'])
@jwt_required()
def cancelar_reserva(id):
    r = Reserva.query.get_or_404(id)
    if r.estado == 'cancelada':
        return jsonify({'ok': False, 'msg': 'La reserva ya está cancelada'}), 400

    r.estado = 'cancelada'
    db.session.commit()

    return jsonify({'ok': True, 'msg': 'Reserva cancelada correctamente'}), 200


@reservas_bp.route('/<int:id>', methods=['PUT'])
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