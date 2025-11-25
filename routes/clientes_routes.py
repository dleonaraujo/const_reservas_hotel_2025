from flask import Blueprint, request, jsonify
from models import db, Cliente
from flask_jwt_extended import jwt_required

clientes_bp = Blueprint("clientes_bp", __name__, url_prefix="/api/clientes")

# =========================================================
# LISTAR CLIENTES
# =========================================================
@clientes_bp.route('/', methods=['GET'])
@jwt_required()
def listar_clientes():
    clientes = Cliente.query.all()

    data = [{
        "id": c.id,
        "nombre": c.nombre,
        "email": c.email,
        "telefono": c.telefono,
        "dni": c.dni
    } for c in clientes]

    return jsonify(data), 200


# =========================================================
# OBTENER CLIENTE POR ID
# =========================================================
@clientes_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_cliente(id):
    c = Cliente.query.get_or_404(id)

    return jsonify({
        "id": c.id,
        "nombre": c.nombre,
        "email": c.email,
        "telefono": c.telefono,
        "dni": c.dni
    }), 200


# =========================================================
# CREAR CLIENTE
# =========================================================
@clientes_bp.route('/', methods=['POST'])
@jwt_required()
def crear_cliente():
    data = request.json
    nombre = data.get("nombre")
    email = data.get("email")
    telefono = data.get("telefono")
    dni = data.get("dni")

    if not all([nombre, email]):
        return jsonify({"ok": False, "msg": "Nombre y email son obligatorios"}), 400

    # Validar DNI único si se proporciona
    if dni:
        dni_existente = Cliente.query.filter_by(dni=dni).first()
        if dni_existente:
            return jsonify({"ok": False, "msg": "El DNI ya está registrado"}), 400

    # Validar email único
    email_existente = Cliente.query.filter_by(email=email).first()
    if email_existente:
        return jsonify({"ok": False, "msg": "El email ya está registrado"}), 400

    c = Cliente(nombre=nombre, email=email, telefono=telefono, dni=dni)
    db.session.add(c)
    db.session.commit()

    return jsonify({"ok": True, "msg": "Cliente creado", "id": c.id}), 201


# =========================================================
# ACTUALIZAR CLIENTE
# =========================================================
@clientes_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_cliente(id):
    c = Cliente.query.get_or_404(id)
    data = request.json

    if "nombre" in data:
        c.nombre = data["nombre"]
    
    if "email" in data:
        # Validar que el email no esté en uso por otro cliente
        if data["email"] != c.email:
            email_existente = Cliente.query.filter_by(email=data["email"]).first()
            if email_existente:
                return jsonify({"ok": False, "msg": "El email ya está registrado"}), 400
        c.email = data["email"]
    
    if "telefono" in data:
        c.telefono = data["telefono"]
    
    if "dni" in data:
        # Validar que el DNI no esté en uso por otro cliente
        if data["dni"] and data["dni"] != c.dni:
            dni_existente = Cliente.query.filter_by(dni=data["dni"]).first()
            if dni_existente:
                return jsonify({"ok": False, "msg": "El DNI ya está registrado"}), 400
        c.dni = data["dni"]

    db.session.commit()
    return jsonify({"ok": True, "msg": "Cliente actualizado"}), 200


# =========================================================
# DELETE LÓGICO
# =========================================================
@clientes_bp.route('/<int:id>/desactivar', methods=['PUT'])
@jwt_required()
def desactivar_cliente(id):
    c = Cliente.query.get_or_404(id)

    c.email = f"inactivo_{c.email}"
    if c.dni:
        c.dni = f"inactivo_{c.dni}"
    db.session.commit()

    return jsonify({"ok": True, "msg": "Cliente desactivado"}), 200


# =========================================================
# DELETE REAL
# =========================================================
@clientes_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_cliente(id):
    c = Cliente.query.get_or_404(id)

    db.session.delete(c)
    db.session.commit()

    return jsonify({"ok": True, "msg": "Cliente eliminado"}), 200