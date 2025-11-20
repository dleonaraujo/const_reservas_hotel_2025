from flask import Blueprint, jsonify, request
from models import db, Usuario
from flask_jwt_extended import jwt_required

usuarios_bp = Blueprint("usuarios_bp", __name__, url_prefix="/api/usuarios")


@usuarios_bp.route('', methods=['POST'])
@jwt_required()
def create_usuario():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({'ok': False, 'msg': 'Username y password obligatorios'}), 400

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


@usuarios_bp.route('', methods=['GET'])
@jwt_required()
def list_usuarios():
    all_u = Usuario.query.all()
    out = [
        {'id': u.id, 'username': u.username, 'nombre': u.nombre, 'email': u.email, 'role_id': u.role_id}
        for u in all_u
    ]
    return jsonify(out), 200