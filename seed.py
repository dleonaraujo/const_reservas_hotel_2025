from app import create_app
from models import db, Usuario, Rol, Permiso, Cliente, TipoHabitacion, Habitacion
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # === Roles ===
    admin_role = Rol(nombre='Administrador')
    recepcionista_role = Rol(nombre='Recepcionista')
    db.session.add_all([admin_role, recepcionista_role])

    # === Permisos ===
    p1 = Permiso(nombre='gestionar_usuarios')
    p2 = Permiso(nombre='gestionar_reservas')
    p3 = Permiso(nombre='ver_reportes')
    db.session.add_all([p1, p2, p3])
    db.session.commit()

    # Asociar permisos a roles
    admin_role.permisos = [p1, p2, p3]
    recepcionista_role.permisos = [p2]
    db.session.commit()

    # === Usuarios ===
    admin = Usuario(
        username='admin',
        nombre='Administrador del sistema',
        email='admin@hotel.com',
        password_hash=generate_password_hash('123456'),
        role=admin_role
    )
    recep = Usuario(
        username='recepcion1',
        nombre='Recepcionista',
        email='recep@hotel.com',
        password_hash=generate_password_hash('123456'),
        role=recepcionista_role
    )
    db.session.add_all([admin, recep])

    # === Clientes ===
    cliente1 = Cliente(nombre='Juan Pérez', email='juan@example.com', telefono='987654321')
    cliente2 = Cliente(nombre='María López', email='maria@example.com', telefono='999111222')
    db.session.add_all([cliente1, cliente2])

    # === Tipos de habitación ===
    simple = TipoHabitacion(nombre='Simple', descripcion='Habitación individual con baño privado')
    doble = TipoHabitacion(nombre='Doble', descripcion='Habitación doble con vista al mar')
    suite = TipoHabitacion(nombre='Suite', descripcion='Suite con jacuzzi y minibar')
    db.session.add_all([simple, doble, suite])
    db.session.commit()

    # === Habitaciones ===
    habitaciones = [
        Habitacion(numero='101', tipo=simple, precio=120.0, estado='disponible'),
        Habitacion(numero='102', tipo=doble, precio=180.0, estado='disponible'),
        Habitacion(numero='103', tipo=suite, precio=250.0, estado='mantenimiento'),
    ]
    db.session.add_all(habitaciones)
    db.session.commit()

    print("Datos de prueba cargados correctamente.")