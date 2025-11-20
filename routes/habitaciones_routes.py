from flask import Blueprint, jsonify, request
from models import db, Habitacion, Reserva, DetalleReserva
from flask_jwt_extended import jwt_required
from datetime import datetime

habitaciones_bp = Blueprint("habitaciones_bp", __name__, url_prefix="/api/habitaciones")

# ============================
# LISTAR DISPONIBLES
# ============================
@habitaciones_bp.route('/disponibles', methods=['GET'])
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
        return jsonify({'ok': False, 'msg': 'Formato de fecha inválido'}), 400

    sub = db.session.query(DetalleReserva.habitacion_id).join(Reserva).filter(
        Reserva.fecha_inicio <= end_date,
        Reserva.fecha_fin >= start_date
    ).subquery()

    disponibles = Habitacion.query.filter(
        ~Habitacion.id.in_(sub),
        Habitacion.estado != "inactivo"
    ).all()

    out = [{
        'id': h.id,
        'numero': h.numero,
        'tipo': h.tipo.nombre if h.tipo else None,
        'precio': h.precio,
        'estado': h.estado
    } for h in disponibles]

    return jsonify(out), 200


# =====================================
# LISTAR TODAS LAS HABITACIONES ACTIVAS
# =====================================
@habitaciones_bp.route('/', methods=['GET'])
@jwt_required()
def listar_habitaciones():
    habitaciones = Habitacion.query.filter(Habitacion.estado != "inactivo").all()
    out = [{
        "id": h.id,
        "numero": h.numero,
        "tipo_id": h.tipo_id,
        "tipo": h.tipo.nombre if h.tipo else None,
        "precio": h.precio,
        "estado": h.estado
    } for h in habitaciones]
    return jsonify(out), 200


# ===========================
# OBTENER HABITACION POR ID
# ===========================
@habitaciones_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_habitacion(id):
    habitacion = Habitacion.query.get(id)

    if not habitacion or habitacion.estado == "inactivo":
        return jsonify({"msg": "Habitación no encontrada"}), 404

    return jsonify({
        "id": habitacion.id,
        "numero": habitacion.numero,
        "tipo_id": habitacion.tipo_id,
        "tipo": habitacion.tipo.nombre if habitacion.tipo else None,
        "precio": habitacion.precio,
        "estado": habitacion.estado
    })


# ===========================
# CREAR HABITACION
# ===========================
@habitaciones_bp.route('/', methods=['POST'])
@jwt_required()
def crear_habitacion():
    data = request.json

    nueva = Habitacion(
        numero=data.get('numero'),
        tipo_id=data.get('tipo_id'),
        precio=data.get('precio'),
        estado=data.get('estado', 'disponible')
    )

    db.session.add(nueva)
    db.session.commit()

    return jsonify({"msg": "Habitación creada", "id": nueva.id}), 201


# ===========================
# ACTUALIZAR HABITACION
# ===========================
@habitaciones_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_habitacion(id):
    habitacion = Habitacion.query.get(id)

    if not habitacion or habitacion.estado == "inactivo":
        return jsonify({"msg": "Habitación no encontrada"}), 404

    data = request.json
    habitacion.numero = data.get('numero', habitacion.numero)
    habitacion.tipo_id = data.get('tipo_id', habitacion.tipo_id)
    habitacion.precio = data.get('precio', habitacion.precio)
    habitacion.estado = data.get('estado', habitacion.estado)

    db.session.commit()

    return jsonify({"msg": "Habitación actualizada"}), 200


# ==============================
# ELIMINAR HABITACION (LÓGICO)
# ==============================
@habitaciones_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_habitacion(id):
    habitacion = Habitacion.query.get(id)

    if not habitacion or habitacion.estado == "inactivo":
        return jsonify({"msg": "Habitación no encontrada"}), 404

    habitacion.estado = "inactivo"
    db.session.commit()

    return jsonify({"msg": "Habitación eliminada lógicamente"}), 200