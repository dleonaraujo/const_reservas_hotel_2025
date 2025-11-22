from flask import Blueprint, request, jsonify
from models import db, Servicio
from flask_jwt_extended import jwt_required

servicios_bp = Blueprint("servicios_bp", __name__, url_prefix="/api/servicios")

# =========================================================
# LISTAR SERVICIOS
# =========================================================
@servicios_bp.route('/', methods=['GET'])
@jwt_required()
def listar_servicios():
    servicios = Servicio.query.all()

    data = [{
        "id": s.id,
        "nombre": s.nombre,
        "precio": s.precio
    } for s in servicios]

    return jsonify(data), 200


# =========================================================
# OBTENER SERVICIO POR ID
# =========================================================
@servicios_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_servicio(id):
    s = Servicio.query.get_or_404(id)

    return jsonify({
        "id": s.id,
        "nombre": s.nombre,
        "precio": s.precio
    }), 200


# =========================================================
# CREAR SERVICIO
# =========================================================
@servicios_bp.route('/', methods=['POST'])
@jwt_required()
def crear_servicio():
    data = request.json
    nombre = data.get("nombre")
    precio = data.get("precio")

    if not nombre or precio is None:
        return jsonify({"ok": False, "msg": "Datos incompletos"}), 400

    s = Servicio(nombre=nombre, precio=precio)
    db.session.add(s)
    db.session.commit()

    return jsonify({"ok": True, "msg": "Servicio creado", "id": s.id}), 201


# =========================================================
# ACTUALIZAR SERVICIO
# =========================================================
@servicios_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_servicio(id):
    s = Servicio.query.get_or_404(id)
    data = request.json

    if "nombre" in data:
        s.nombre = data["nombre"]

    if "precio" in data:
        s.precio = data["precio"]

    db.session.commit()
    return jsonify({"ok": True, "msg": "Servicio actualizado"}), 200


# =========================================================
# DELETE LÓGICO (lo marcamos como inactivo)
# =========================================================
@servicios_bp.route('/<int:id>/desactivar', methods=['PUT'])
@jwt_required()
def desactivar_servicio(id):
    s = Servicio.query.get_or_404(id)

    s.nombre = s.nombre + " (inactivo)"
    db.session.commit()

    return jsonify({"ok": True, "msg": "Servicio desactivado"}), 200


# =========================================================
# DELETE REAL
# =========================================================
@servicios_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_servicio(id):
    s = Servicio.query.get_or_404(id)

    db.session.delete(s)
    db.session.commit()

    return jsonify({"ok": True, "msg": "Servicio eliminado"}), 200
