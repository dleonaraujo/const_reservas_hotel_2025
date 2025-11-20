from flask import Blueprint, jsonify
from models import db, Pago, Reserva, Habitacion, DetalleReserva
from flask_jwt_extended import jwt_required

reportes_bp = Blueprint("reportes_bp", __name__, url_prefix="/api/reportes")


@reportes_bp.route('/reservas-por-estado', methods=['GET'])
@jwt_required()
def reporte_reservas_por_estado():
    resultados = db.session.query(Reserva.estado, db.func.count(Reserva.id)).group_by(Reserva.estado).all()
    return jsonify([{'estado': e, 'cantidad': c} for e, c in resultados]), 200


@reportes_bp.route('/ingresos', methods=['GET'])
@jwt_required()
def reporte_ingresos():
    resultados = db.session.query(
        db.func.date(Pago.fecha).label('fecha'),
        db.func.sum(Pago.monto)
    ).group_by(db.func.date(Pago.fecha)).all()

    return jsonify([{'fecha': str(f), 'ingresos': float(i)} for f, i in resultados]), 200


@reportes_bp.route('/habitaciones-populares', methods=['GET'])
@jwt_required()
def reporte_habitaciones_populares():
    resultados = db.session.query(
        Habitacion.numero,
        db.func.count(DetalleReserva.id)
    ).join(DetalleReserva).group_by(Habitacion.numero).order_by(db.func.count(DetalleReserva.id).desc()).limit(10).all()

    return jsonify([{'habitacion': n, 'reservas': c} for n, c in resultados]), 200