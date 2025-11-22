from flask import Blueprint, jsonify, request
from models import db, Reserva, Habitacion, DetalleReserva, Cliente
from flask_jwt_extended import jwt_required
from datetime import datetime

reservas_bp = Blueprint("reservas_bp", __name__, url_prefix="/api/reservas")

# =========================================================
# LISTAR TODAS LAS RESERVAS
# =========================================================
@reservas_bp.route('/', methods=['GET'])
@jwt_required()
def listar_reservas():
    reservas = Reserva.query.all()

    data = []
    for r in reservas:
        data.append({
            "id": r.id,
            "cliente": r.cliente.nombre if r.cliente else None,
            "cliente_id": r.cliente_id,
            "fecha_inicio": r.fecha_inicio.isoformat(),
            "fecha_fin": r.fecha_fin.isoformat(),
            "estado": r.estado,
            "total": r.total,
            "habitaciones": [
                {
                    "id": d.habitacion.id,
                    "numero": d.habitacion.numero,
                    "precio": d.precio
                } for d in r.detalles
            ]
        })

    return jsonify(data), 200


# =========================================================
# OBTENER UNA RESERVA POR ID
# =========================================================
@reservas_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_reserva(id):
    r = Reserva.query.get_or_404(id)

    return jsonify({
        "id": r.id,
        "cliente_id": r.cliente_id,
        "fecha_inicio": r.fecha_inicio.isoformat(),
        "fecha_fin": r.fecha_fin.isoformat(),
        "estado": r.estado,
        "total": r.total,
        "habitaciones": [
            {
                "id": d.habitacion.id,
                "numero": d.habitacion.numero,
                "precio": d.precio
            } for d in r.detalles
        ]
    }), 200


# =========================================================
# CREAR NUEVA RESERVA
# =========================================================
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


# =========================================================
# ACTUALIZAR RESERVA
# =========================================================
@reservas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_reserva(id):
    r = Reserva.query.get_or_404(id)
    data = request.json

    if 'cliente_id' in data:
        r.cliente_id = data['cliente_id']

    if 'fecha_inicio' in data:
        r.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()

    if 'fecha_fin' in data:
        r.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()

    if 'estado' in data:
        r.estado = data['estado']

    db.session.commit()
    return jsonify({'ok': True, 'msg': 'Reserva actualizada correctamente'}), 200


# =========================================================
# ACTUALIZAR HABITACIONES DE UNA RESERVA
# =========================================================
@reservas_bp.route('/<int:id>/habitaciones', methods=['PUT'])
@jwt_required()
def actualizar_habitaciones(id):
    r = Reserva.query.get_or_404(id)
    habitaciones = request.json.get("habitaciones", [])

    # eliminar detalles anteriores
    DetalleReserva.query.filter_by(reserva_id=id).delete()

    total = 0
    for hab_id in habitaciones:
        h = Habitacion.query.get(hab_id)
        if h:
            d = DetalleReserva(reserva_id=id, habitacion_id=h.id, precio=h.precio)
            db.session.add(d)
            total += h.precio

    r.total = total
    db.session.commit()

    return jsonify({"ok": True, "msg": "Habitaciones actualizadas", "total": total}), 200


# =========================================================
# CANCELAR RESERVA (DELETE LÓGICO)
# =========================================================
@reservas_bp.route('/<int:id>/cancelar', methods=['PUT'])
@jwt_required()
def cancelar_reserva(id):
    r = Reserva.query.get_or_404(id)

    if r.estado == 'cancelada':
        return jsonify({'ok': False, 'msg': 'La reserva ya está cancelada'}), 400

    r.estado = 'cancelada'
    db.session.commit()

    return jsonify({'ok': True, 'msg': 'Reserva cancelada correctamente'}), 200


# =========================================================
# ELIMINAR RESERVA (DELETE REAL - OPCIONAL)
# =========================================================
@reservas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_reserva(id):
    r = Reserva.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()

    return jsonify({'ok': True, 'msg': 'Reserva eliminada'}), 200
