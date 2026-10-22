import hashlib
import hmac

def _obtener_cursor(conexion_db, mensaje):
    cursor = conexion_db.cursor
    if cursor is None:
        raise ConnectionError(mensaje)
    return cursor

class Empleados:
    def __init__(self, id_empleado=None, nombre=None, apellido_paterno=None,
                 apellido_materno=None, direccion=None, telefono=None, correo=None,
                 fecha_contrato=None, salario=None, departamento_id=None):
        self.id_empleado= id_empleado
        self.nombre= nombre
        self.apellido_paterno= apellido_paterno
        self.apellido_materno= apellido_materno
        self.direccion= direccion
        self.telefono= telefono
        self.correo= correo
        self.fecha_contrato= fecha_contrato
        self.salario= salario
        self.departamento_id= departamento_id

    def consultar_todos(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        cursor.execute("""
        SELECT id_empleado, nombre, apellido_paterno,
               apellido_materno,
               TO_CHAR(fecha_contrato, 'DD-MM-YYYY') AS fecha_contrato
        FROM EMPLEADOS
        ORDER BY id_empleado
        """)
        return cursor.fetchall()

    def registrar(self, conexion_db, nombre_usuario, contrasena,
                  rol):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")

        hash_contrasena = hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest().upper()

        try:
            id_generado = cursor.var(int)
            cursor.execute("""
            INSERT INTO EMPLEADOS (
            nombre,
            apellido_paterno, apellido_materno, direccion,
            telefono, correo, fecha_contrato, salario,
            departamento_id
            )
            VALUES (
            :nombre, :apellido_paterno, :apellido_materno,
            :direccion, :telefono, :correo,
            TO_DATE(:fecha_contrato, 'DD-MM-YYYY'),
            :salario, :departamento_id)
            RETURNING id_empleado
            INTO :id_generado
            """, {
                "nombre": self.nombre,
                "apellido_paterno": self.apellido_paterno,
                "apellido_materno": self.apellido_materno,
                "direccion": self.direccion,
                "telefono": self.telefono,
                "correo": self.correo,
                "fecha_contrato": self.fecha_contrato,
                "salario": self.salario,
                "departamento_id": self.departamento_id,
                "id_generado": id_generado
            })

            nuevo_id = id_generado.getvalue()
            if isinstance(nuevo_id, list):
                nuevo_id = nuevo_id[0]

            cursor.execute("""
            INSERT INTO CUENTAS_ACCESO (
            empleado_id,
            nombre_usuario,
            password_hash,
            rol
            )
            VALUES (
            :empleado_id,
            :nombre_usuario,
            :password_hash,
            :rol
            )
            """, {
                 "empleado_id": nuevo_id,
                 "nombre_usuario": nombre_usuario,
                 "password_hash": hash_contrasena,
                 "rol": rol
            })
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise
        self.id_empleado = nuevo_id
        return nuevo_id

    def asignar_departamento(self, conexion_db, departamento_id):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con base de datos.")

        try:
            cursor.execute("""
            UPDATE EMPLEADOS
            SET departamento_id = :departamento_id
            WHERE id_empleado = :id_empleado
            """, {
                "departamento_id": departamento_id,
                "id_empleado": self.id_empleado
            })

            if cursor.rowcount == 0:
                raise ValueError("No se encontró empleado.")
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise
        self.departamento_id = departamento_id

class Departamentos:
    def __init__(self, id_depa=None, nombre_depa=None,
                 tipo_depa=None, gerente_id=None):
        self.id_depa = id_depa
        self.nombre_depa = nombre_depa
        self.tipo_depa = tipo_depa
        self.gerente_id = gerente_id

    def consultar_todos(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        cursor.execute("""
            SELECT id_depa, nombre_depa, tipo_depa, gerente_id
            FROM DEPARTAMENTOS
            ORDER BY id_depa
        """)
        return cursor.fetchall()

    def consulta_gerente(self, conexion_db, gerente_id):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        cursor.execute("""
            SELECT id_depa, nombre_depa, tipo_depa
            FROM DEPARTAMENTOS
            WHERE gerente_id = :gerente_id
            ORDER BY id_depa
        """, {"gerente_id": gerente_id})
        return cursor.fetchall()

    def buscar_por_id(self, conexion_db, id_depa):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        cursor.execute("""
            SELECT id_depa, nombre_depa, tipo_depa, gerente_id
            FROM DEPARTAMENTOS
            WHERE id_depa = :id_depa
        """, {"id_depa": id_depa})
        return cursor.fetchone()

    def registrar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        try:
            id_generado = cursor.var(int)
            cursor.execute("""
                INSERT INTO DEPARTAMENTOS (
                    nombre_depa, tipo_depa, gerente_id
                )
                VALUES (
                    :nombre_depa, :tipo_depa, :gerente_id
                )
                RETURNING id_depa INTO :id_generado
            """, {
                "nombre_depa": self.nombre_depa,
                "tipo_depa": self.tipo_depa,
                "gerente_id": self.gerente_id,
                "id_generado": id_generado
            })

            nuevo_id = id_generado.getvalue()
            if isinstance(nuevo_id, list):
                nuevo_id = nuevo_id[0]
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise
        self.id_depa = nuevo_id
        return nuevo_id

    def actualizar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")

        try:
            cursor.execute("""
                UPDATE DEPARTAMENTOS
                SET nombre_depa = :nombre_depa,
                    tipo_depa = :tipo_depa
                WHERE id_depa = :id_depa
            """, {
                "nombre_depa": self.nombre_depa,
                "tipo_depa": self.tipo_depa,
                "id_depa": self.id_depa
            })

            if cursor.rowcount == 0:
                raise ValueError("No se encontró el departamento.")
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

    def eliminar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")

        try:
            cursor.execute("""
                DELETE FROM DEPARTAMENTOS
                WHERE id_depa = :id_depa
            """, {"id_depa": self.id_depa})

            if cursor.rowcount == 0:
                raise ValueError("No se encontró el departamento.")
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

class Proyectos:
    def __init__(self, id_proyecto=None, nombre_proyecto=None, descripcion=None,
                fecha_inicio=None):
        self.id_proyecto= id_proyecto
        self.nombre_proyecto= nombre_proyecto
        self.descripcion= descripcion
        self.fecha_inicio= fecha_inicio

    def consultar_proyectos(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "Error de conexión con base de datos")
        cursor.execute("""
        SELECT id_proyecto, nombre_proyecto, descripcion,
        TO_CHAR(fecha_inicio, 'DD-MM-YYYY') AS fecha_inicio
        FROM PROYECTOS
        ORDER BY id_proyecto
        """)
        return cursor.fetchall()

    def buscar_por_id(self, conexion_db, id_proyecto):
        cursor = _obtener_cursor(conexion_db, "Error de conexión con base de datos")
        cursor.execute("""
            SELECT id_proyecto, nombre_proyecto, descripcion,
                   TO_CHAR(fecha_inicio, 'DD-MM-YYYY') AS fecha_inicio
            FROM PROYECTOS
            WHERE id_proyecto = :id_proyecto
        """, {"id_proyecto": id_proyecto})
        return cursor.fetchone()

    def registrar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "Error de conexión con base de datos")
        try:
            id_generado = cursor.var(int)
            cursor.execute("""
            INSERT INTO PROYECTOS (
            nombre_proyecto, descripcion, fecha_inicio
            )
            VALUES (
            :nombre_proyecto,
            :descripcion,
            TO_DATE(:fecha_inicio, 'DD-MM-YYYY')
            )
            RETURNING id_proyecto INTO :id_generado
            """, {
                "nombre_proyecto": self.nombre_proyecto,
                "descripcion": self.descripcion,
                "fecha_inicio": self.fecha_inicio,
                "id_generado": id_generado
            })

            nuevo_id = id_generado.getvalue()
            if isinstance(nuevo_id, list):
                nuevo_id = nuevo_id[0]
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise
        self.id_proyecto = nuevo_id
        return nuevo_id

    def actualizar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "Error de conexión con base de datos")
        try:
            cursor.execute("""
                UPDATE PROYECTOS
                SET nombre_proyecto = :nombre_proyecto,
                    descripcion = :descripcion,
                    fecha_inicio = TO_DATE(:fecha_inicio, 'DD-MM-YYYY')
                WHERE id_proyecto = :id_proyecto
            """, {
                "nombre_proyecto": self.nombre_proyecto,
                "descripcion": self.descripcion,
                "fecha_inicio": self.fecha_inicio,
                "id_proyecto": self.id_proyecto
            })

            if cursor.rowcount == 0:
                raise ValueError("No se encontró el proyecto.")
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

    def eliminar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "Error de conexión con base de datos")
        try:
            cursor.execute("""
                DELETE FROM PROYECTOS
                WHERE id_proyecto = :id_proyecto
            """, {"id_proyecto": self.id_proyecto})

            if cursor.rowcount == 0:
                raise ValueError("No se encontró el proyecto.")
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

class EmpleadoProyecto:
    def __init__(self, empleado_id=None, proyecto_id=None, fecha_asignacion=None):
        self.empleado_id= empleado_id
        self.proyecto_id= proyecto_id
        self.fecha_asignacion= fecha_asignacion

    def asignar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "Error con conexión a base de datos")
        try:
            cursor.execute("""
            INSERT INTO EMPLEADO_PROYECTO (
            empleado_id, proyecto_id, fecha_asignacion
            )
            VALUES (
            :empleado_id,
            :proyecto_id,
            TO_DATE(:fecha_asignacion, 'DD-MM-YYYY')
            )
            """, {
                "empleado_id": self.empleado_id,
                "proyecto_id": self.proyecto_id,
                "fecha_asignacion": self.fecha_asignacion
            })
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

    def desasignar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "Error con conexión a base de datos")
        try:
            cursor.execute("""
                DELETE FROM EMPLEADO_PROYECTO
                WHERE empleado_id = :empleado_id
                  AND proyecto_id = :proyecto_id
            """, {
                "empleado_id": self.empleado_id,
                "proyecto_id": self.proyecto_id
            })

            if cursor.rowcount == 0:
                raise ValueError("No se encontró la asignación del empleado.")
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

    def consultar_proyectos_empleado(self, conexion_db, empleado_id):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        cursor.execute("""
            SELECT ep.proyecto_id, p.nombre_proyecto,
                   TO_CHAR(ep.fecha_asignacion, 'DD-MM-YYYY')
            FROM EMPLEADO_PROYECTO ep
            JOIN PROYECTOS p ON p.id_proyecto = ep.proyecto_id
            WHERE ep.empleado_id = :empleado_id
            ORDER BY ep.proyecto_id
        """, {"empleado_id": empleado_id})

        return cursor.fetchall()

    def consultar_empleados_proyecto(self, conexion_db, proyecto_id):
        cursor = _obtener_cursor(conexion_db, "No hay conexión con la base de datos.")
        cursor.execute("""
            SELECT e.id_empleado, e.nombre, e.apellido_paterno,
                   e.apellido_materno
            FROM EMPLEADO_PROYECTO ep
            JOIN EMPLEADOS e ON e.id_empleado = ep.empleado_id
            WHERE ep.proyecto_id = :proyecto_id
            ORDER BY e.id_empleado
        """, {"proyecto_id": proyecto_id})

        return cursor.fetchall()

class Registrotiempo:
    def __init__(self, id_registro=None, empleado_id=None, proyecto_id=None, fecha=None,
                horas_trabajadas=None, descripcion_tareas=None):
        self.id_registro= id_registro
        self.empleado_id= empleado_id
        self.proyecto_id= proyecto_id
        self.fecha= fecha
        self.horas_trabajadas= horas_trabajadas
        self.descripcion_tareas= descripcion_tareas

    def registrar(self, conexion_db):
        cursor = _obtener_cursor(conexion_db, "No hay conexion con base de datos.")
        try:
            cursor.execute("""
            INSERT INTO REGISTRO_TIEMPO (
            empleado_id, proyecto_id, fecha,
            horas_trabajadas, descripcion_tareas
            )
            VALUES (
            :empleado_id,
            :proyecto_id,
            TO_DATE(:fecha, 'DD-MM-YYYY'),
            :horas_trabajadas,
            :descripcion_tareas
            )
            """, {
                "empleado_id": self.empleado_id,
                "proyecto_id": self.proyecto_id,
                "fecha": self.fecha,
                "horas_trabajadas": self.horas_trabajadas,
                "descripcion_tareas": self.descripcion_tareas
            })
            conexion_db.conexion.commit()

        except Exception:
            conexion_db.conexion.rollback()
            raise

    def consultar_por_empleado(self, conexion_db, empleado_id):
        cursor = _obtener_cursor(conexion_db, "No hay conexion con base de datos.")
        cursor.execute("""
        SELECT rt.id_registro, p.nombre_proyecto,
        TO_CHAR(rt.fecha, 'DD-MM-YYYY'),
        rt.horas_trabajadas, rt.descripcion_tareas
        FROM REGISTRO_TIEMPO rt
        JOIN PROYECTOS p ON p.id_proyecto = rt.proyecto_id
        WHERE rt.empleado_id = :empleado_id
        ORDER BY rt.fecha, rt.id_registro
        """, {"empleado_id": empleado_id})

        return cursor.fetchall()

class CuentasAcceso:
    def __init__(self, id_acceso=None, empleado_id=None, nombre_usuario=None, password_hash=None,
                 rol=None):
        self.id_acceso= id_acceso
        self.empleado_id= empleado_id
        self.nombre_usuario= nombre_usuario
        self.password_hash= password_hash
        self.rol= rol

    def autenticar(self, nombre_usuario, contrasena, conexion_db):
        if conexion_db.cursor is None:
            return False

        cursor = conexion_db.cursor
        cursor.execute("""
        SELECT id_acceso, empleado_id, password_hash, rol
        FROM CUENTAS_ACCESO
        WHERE nombre_usuario = :usuario
        """, {"usuario": nombre_usuario})

        fila = cursor.fetchone()

        if fila is None:
            return False

        hash_ingresado = hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest().upper()

        if not hmac.compare_digest(hash_ingresado, fila[2]):
            return False

        self.id_acceso = fila[0]
        self.empleado_id = fila[1]
        self.nombre_usuario = nombre_usuario
        self.password_hash = fila[2]
        self.rol = fila[3]

        return True

    def autorizar(self, roles_permitidos):
        return self.rol in roles_permitidos

class RegistroEmpleados:
    def registrar(self, conexion_db, empleado, nombre_usuario, contrasena, rol):
        return empleado.registrar(
            conexion_db,
            nombre_usuario,
            contrasena,
            rol
        )

class Administrador(Empleados):
    def registrar_empleado(self, conexion_db, empleado, nombre_usuario,
                           contrasena, rol):
        return RegistroEmpleados().registrar(
            conexion_db,
            empleado,
            nombre_usuario,
            contrasena,
            rol
        )

class Gerente(Empleados):
    def crear_departamento(self, conexion_db, nombre_depa, tipo_depa):
        departamento = Departamentos(
            nombre_depa=nombre_depa,
            tipo_depa=tipo_depa,
            gerente_id=self.id_empleado
        )
        return departamento.registrar(conexion_db)

    def asignar_empleado_departamento(self, conexion_db, empleado_id,
                                      departamento_id):
        empleado = Empleados(id_empleado=empleado_id)
        empleado.asignar_departamento(conexion_db, departamento_id)

class GestorProyectos(Empleados):
    def asignar_empleado_proyecto(self, conexion_db, empleado_id,
                                  proyecto_id, fecha_asignacion):
        asignacion = EmpleadoProyecto(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            fecha_asignacion=fecha_asignacion
        )
        asignacion.asignar(conexion_db)

    def desasignar_empleado_proyecto(self, conexion_db, empleado_id,
                                     proyecto_id):
        asignacion = EmpleadoProyecto(
            empleado_id=empleado_id,
            proyecto_id=proyecto_id
        )
        asignacion.desasignar(conexion_db)