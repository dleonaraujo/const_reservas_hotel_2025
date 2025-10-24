from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Asociativa many-to-many ejemplo Roles<->Permisos
roles_permisos = db.Table('roles_permisos',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permiso_id', db.Integer, db.ForeignKey('permisos.id'), primary_key=True)
)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(120))
    email = db.Column(db.String(120),unique = True)
    password_hash = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Rol', back_populates='usuarios')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    usuarios = db.relationship('Usuario', back_populates='role')
    permisos = db.relationship('Permiso', secondary=roles_permisos, back_populates='roles')

class Permiso(db.Model):
    __tablename__ = 'permisos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    roles = db.relationship('Rol', secondary=roles_permisos, back_populates='permisos')

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(30))

class Empleado(db.Model):
    __tablename__ = 'empleados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120))
    puesto_id = db.Column(db.Integer, db.ForeignKey('puestos_trabajo.id'))
    puesto = db.relationship('PuestoTrabajo')

class PuestoTrabajo(db.Model):
    __tablename__ = 'puestos_trabajo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120))

class TipoHabitacion(db.Model):
    __tablename__ = 'tipos_habitacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80))
    descripcion = db.Column(db.String(255))

class Habitacion(db.Model):
    __tablename__ = 'habitaciones'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_habitacion.id'))
    tipo = db.relationship('TipoHabitacion')
    precio = db.Column(db.Float)
    estado = db.Column(db.String(30), default='disponible')

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    cliente = db.relationship('Cliente')
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.String(30), default='planificada')
    total = db.Column(db.Float, default=0.0)

class DetalleReserva(db.Model):
    __tablename__ = 'detalles_reserva'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    reserva = db.relationship('Reserva', backref='detalles')
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitaciones.id'))
    habitacion = db.relationship('Habitacion')
    precio = db.Column(db.Float)

class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120))
    precio = db.Column(db.Float)

class ReservaServicio(db.Model):
    __tablename__ = 'reserva_servicio'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'))
    cantidad = db.Column(db.Integer, default=1)

class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=True)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    total = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class CheckIn(db.Model):
    __tablename__ = 'checkins'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))

class CheckOut(db.Model):
    __tablename__ = 'checkouts'
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))

class HistorialAcceso(db.Model):
    __tablename__ = 'historial_acceso'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(120))
    accion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
