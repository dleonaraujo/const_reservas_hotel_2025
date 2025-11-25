from flask import Blueprint, jsonify, request
from models import db, TipoHabitacion
from flask_jwt_extended import jwt_required

tipo_habitacion_bp = Blueprint("tipo_habitacion_bp", __name__, url_prefix="/api/tipos-habitacion")


# ===============================
# LISTAR TIPOS DE HABITACIÓN
# ===============================
@tipo_habitacion_bp.route('/', methods=['GET'])
@jwt_required()
def listar_tipos():
    tipos = TipoHabitacion.query.all()
    out = [{
        "id": t.id,
        "nombre": t.nombre,
        "descripcion": t.descripcion
    } for t in tipos]
    return jsonify(out), 200


# ===============================
# CREAR TIPO DE HABITACIÓN
# ===============================
@tipo_habitacion_bp.route('/', methods=['POST'])
@jwt_required()
def crear_tipo():
    data = request.json

    nuevo = TipoHabitacion(
        nombre=data.get('nombre'),
        descripcion=data.get('descripcion')
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"msg": "Tipo creado", "id": nuevo.id}), 201


# ===============================
# ACTUALIZAR TIPO DE HABITACIÓN
# ===============================
@tipo_habitacion_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_tipo(id):
    tipo = TipoHabitacion.query.get(id)

    if not tipo:
        return jsonify({"msg": "Tipo no encontrado"}), 404

    data = request.json
    tipo.nombre = data.get('nombre', tipo.nombre)
    tipo.descripcion = data.get('descripcion', tipo.descripcion)

    db.session.commit()

    return jsonify({"msg": "Tipo actualizado"}), 200


# ===============================
# ELIMINAR TIPO DE HABITACIÓN
# ===============================
@tipo_habitacion_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_tipo(id):
    tipo = TipoHabitacion.query.get(id)

    if not tipo:
        return jsonify({"msg": "Tipo no encontrado"}), 404

    db.session.delete(tipo)
    db.session.commit()

    return jsonify({"msg": "Tipo eliminado"}), 200
