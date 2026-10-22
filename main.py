from getpass import getpass
from conexion import ConexionDB
from clases import (CuentasAcceso, Empleados, Departamentos, Proyectos,
                    EmpleadoProyecto, Registrotiempo, Administrador,
                    Gerente, GestorProyectos)
from datetime import datetime
from decimal import Decimal, InvalidOperation
import oracledb

conexion = ConexionDB()

def pedir_fecha(mensaje):
    while True:
        fecha = input(mensaje).strip()
        try:
            datetime.strptime(fecha, "%d-%m-%Y")
            return fecha
        except ValueError:
            print("Fecha no válida; usa formato DD-MM-YYYY.")

def contiene_id(registros, id_busqueda):
    return any(registro[0] == id_busqueda for registro in registros)

def menu_gerente(conexion, sesion):
    while True:
        print("--- Menú de Gerente ---")
        print("1. Crear departamento")
        print("2. Ver departamentos")
        print("3. Asignar o mover empleado")
        print("4. Editar departamento")
        print("5. Buscar departamento")
        print("6. Eliminar departamento")
        print("7. Cerrar sesión")
        
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "7":
            print("Cerrando sesión...")
            return
        
        try:
            if opcion == "1":
                nombre = input("Nombre del departamento: ").strip()
                if not nombre or len(nombre) > 50:
                    print("El nombre es obligatorio y debe tener máximo 50 caracteres.")
                    continue

                tipos = {"1": "Desarrollo Sostenible", 
                         "2": "Ventas", 
                         "3": "Investigacion"}
                print("Tipo de departamento: 1. Desarrollo Sostenible | 2. Ventas | 3. Investigacion")
                tipo = tipos.get(input("Selecciona el tipo: ").strip())

                if tipo is None:
                    print("Tipo de departamento no válido.")
                    continue

                nuevo_id = sesion.crear_departamento(conexion, nombre, tipo)
                print(f"Departamento creado. ID: {nuevo_id}")

            elif opcion == "2":
                departamentos = Departamentos().consultar_todos(conexion)
                if not departamentos:
                    print("No hay departamentos registrados.")
                    continue

                print("--- Departamentos existentes ---")
                for id_depa, nombre, tipo, gerente_id in departamentos:
                    gerente = gerente_id if gerente_id is not None else "Sin asignar"
                    print(f"ID: {id_depa} | {nombre} | {tipo} | Gerente ID: {gerente}")

            elif opcion == "3":
                departamentos = Departamentos().consultar_todos(conexion)
                empleados = Empleados().consultar_todos(conexion)

                if not departamentos:
                    print("Primero debe existir un departamento.")
                    continue

                if not empleados:
                    print("No hay empleados registrados.")
                    continue

                print("--- Departamentos ---")
                for id_depa, nombre, tipo, gerente_id in departamentos:
                    print(f"ID: {id_depa} | {nombre} | {tipo}")

                print("--- Empleados ---")
                for id_empleado, nombre, paterno, materno, fecha in empleados:
                    apellidos = " ".join(a for a in (paterno, materno) if a)
                    print(f"ID: {id_empleado} | {nombre} {apellidos}")

                id_depa = int(input("ID del departamento: ").strip())
                id_empleado = int(input("ID del empleado que asignarás o moverás: ").strip())

                if not contiene_id(departamentos, id_depa):
                    print("No existe ese departamento.")
                    continue

                if not contiene_id(empleados, id_empleado):
                    print("No existe ese empleado.")
                    continue

                sesion.asignar_empleado_departamento(
                    conexion, id_empleado, id_depa
                )
                print("Empleado asignado al departamento.")

            elif opcion == "4":
                departamentos = Departamentos().consultar_todos(conexion)
                if not departamentos:
                    print("No hay departamentos registrados.")
                    continue

                for id_depa, nombre, tipo, gerente_id in departamentos:
                    print(f"ID: {id_depa} | {nombre} | {tipo}")

                id_depa = int(input("ID del departamento que editarás: ").strip())
                if not contiene_id(departamentos, id_depa):
                    print("No existe ese departamento.")
                    continue

                nombre = input("Nuevo nombre del departamento: ").strip()
                if not nombre or len(nombre) > 50:
                    print("El nombre es obligatorio y debe tener máximo 50 caracteres.")
                    continue

                tipos = {"1": "Desarrollo Sostenible", "2": "Ventas", "3": "Investigacion"}
                print("Tipo: 1. Desarrollo Sostenible | 2. Ventas | 3. Investigacion")
                tipo = tipos.get(input("Selecciona el nuevo tipo: ").strip())
                if tipo is None:
                    print("Tipo de departamento no válido.")
                    continue

                departamento = Departamentos(id_depa=id_depa,
                                             nombre_depa=nombre,
                                             tipo_depa=tipo)
                departamento.actualizar(conexion)
                print("Departamento actualizado.")

            elif opcion == "5":
                id_depa = int(input("ID del departamento que buscarás: ").strip())
                departamento = Departamentos().buscar_por_id(conexion, id_depa)
                if departamento is None:
                    print("No existe ese departamento.")
                    continue

                id_depa, nombre, tipo, gerente_id = departamento
                gerente = gerente_id if gerente_id is not None else "Sin asignar"
                print(f"ID: {id_depa} | {nombre} | {tipo} | Gerente ID: {gerente}")

            elif opcion == "6":
                departamentos = Departamentos().consultar_todos(conexion)
                if not departamentos:
                    print("No hay departamentos registrados.")
                    continue

                for id_depa, nombre, tipo, gerente_id in departamentos:
                    print(f"ID: {id_depa} | {nombre} | {tipo}")

                id_depa = int(input("ID del departamento que eliminarás: ").strip())
                if not contiene_id(departamentos, id_depa):
                    print("No existe ese departamento.")
                    continue

                Departamentos(id_depa=id_depa).eliminar(conexion)
                print("Departamento eliminado.")
            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"Error en ID ingresado: {error}")
        except oracledb.IntegrityError:
            if opcion == "6":
                print("No se puede eliminar el departamento mientras tenga empleados asociados.")
            else:
                print("La operación viola una restricción de la base de datos.")
        except oracledb.Error as error:
            print(f"Operación rechazada: {error}")
        except ConnectionError as error:
            print(error)

def menu_gestor_proyecto(conexion, sesion):
    while True:
        print("--- Menú de Gestor de Proyecto ---")
        print("1. Crear proyecto")
        print("2. Consultar proyectos")
        print("3. Asignar empleado a proyecto")
        print("4. Editar proyecto")
        print("5. Buscar proyecto")
        print("6. Eliminar proyecto")
        print("7. Desasignar empleado de proyecto")
        print("8. Cerrar sesión")
        opcion = input("Selecciona una opción: ").strip()
        if opcion == "8":
            print("Cerrando sesión...")
            return
        try:
            if opcion == "1":
                nombre = input("Nombre del proyecto: ").strip()
                if not nombre or len(nombre) > 20:
                    print("Nombre obligatorio y máximo 20 caracteres.")
                    continue
                
                descripcion = input("Descripción proyecto (opcional): ").strip() or None
                if descripcion is not None and len(descripcion) > 80:
                    print("Descripción máxima de 80 caracteres.")
                    continue

                fecha_inicio = pedir_fecha("Fecha inicio de proyecto (DD-MM-YYYY): ")

                proyecto = Proyectos(nombre_proyecto=nombre, descripcion=descripcion,
                                     fecha_inicio=fecha_inicio)
                nuevo_id = proyecto.registrar(conexion)
                print(f"Proyecto creado. ID: {nuevo_id}")

            elif opcion == "2":
                proyectos = Proyectos().consultar_proyectos(conexion)
                if not proyectos:
                    print("No hay proyectos registrados.")
                    continue
                print("--- Proyectos ---")
                for id_proyecto, nombre, descripcion, fecha in proyectos:
                    print(f"ID: {id_proyecto} | {nombre} | {descripcion or 'Sin descripcion'} | Inicio: {fecha or 'Sin fecha'}")

            elif opcion == "3":
                proyectos = Proyectos().consultar_proyectos(conexion)
                empleados = Empleados().consultar_todos(conexion)
                if not proyectos:
                    print("No hay proyectos.")
                    continue
                if not empleados:
                    print("No hay empleados.")
                    continue

                print("--- Proyectos ---")
                for id_proyecto, nombre, descripcion, fecha in proyectos:
                    print(f"ID: {id_proyecto} | {nombre} | {descripcion} | {fecha}")
                
                print("--- Empleados ---")
                for id_empleado, nombre, paterno, materno, fecha in empleados:
                    apellidos = " ".join(a for a in (paterno, materno) if a)
                    print(f"ID: {id_empleado} | {nombre} {apellidos}")

                id_proyecto = int(input("ID del proyecto: ").strip())
                empleado_id = int(input("ID del empleado: ").strip())

                if not contiene_id(proyectos, id_proyecto):
                    print("Proyecto no existe.")
                    continue

                if not contiene_id(empleados, empleado_id):
                    print("Empleado no existe.")
                    continue

                fecha_asignacion = pedir_fecha("Fecha de asignación (DD-MM-YYYY): ")
                sesion.asignar_empleado_proyecto(
                    conexion, empleado_id, id_proyecto, fecha_asignacion
                )
                print("Empleado asignado a proyecto.")

            elif opcion == "4":
                proyectos = Proyectos().consultar_proyectos(conexion)
                if not proyectos:
                    print("No hay proyectos registrados.")
                    continue

                for id_proyecto, nombre, descripcion, fecha in proyectos:
                    print(f"ID: {id_proyecto} | {nombre} | {fecha}")

                id_proyecto = int(input("ID del proyecto que editarás: ").strip())
                if not contiene_id(proyectos, id_proyecto):
                    print("Proyecto no existe.")
                    continue

                nombre = input("Nuevo nombre del proyecto: ").strip()
                if not nombre or len(nombre) > 20:
                    print("Nombre obligatorio y máximo 20 caracteres.")
                    continue

                descripcion = input("Nueva descripción (opcional): ").strip() or None
                if descripcion is not None and len(descripcion) > 80:
                    print("Descripción máxima de 80 caracteres.")
                    continue

                fecha_inicio = pedir_fecha("Nueva fecha de inicio (DD-MM-YYYY): ")

                proyecto = Proyectos(id_proyecto=id_proyecto,
                                     nombre_proyecto=nombre,
                                     descripcion=descripcion,
                                     fecha_inicio=fecha_inicio)
                proyecto.actualizar(conexion)
                print("Proyecto actualizado.")

            elif opcion == "5":
                id_proyecto = int(input("ID del proyecto que buscarás: ").strip())
                proyecto = Proyectos().buscar_por_id(conexion, id_proyecto)
                if proyecto is None:
                    print("Proyecto no existe.")
                    continue

                id_proyecto, nombre, descripcion, fecha = proyecto
                print(
                    f"ID: {id_proyecto} | {nombre} | "
                    f"{descripcion or 'Sin descripcion'} | "
                    f"Inicio: {fecha or 'Sin fecha'}"
                )

            elif opcion == "6":
                proyectos = Proyectos().consultar_proyectos(conexion)
                if not proyectos:
                    print("No hay proyectos registrados.")
                    continue

                for id_proyecto, nombre, descripcion, fecha in proyectos:
                    print(f"ID: {id_proyecto} | {nombre} | {fecha}")

                id_proyecto = int(input("ID del proyecto que eliminarás: ").strip())
                if not contiene_id(proyectos, id_proyecto):
                    print("Proyecto no existe.")
                    continue

                Proyectos(id_proyecto=id_proyecto).eliminar(conexion)
                print("Proyecto eliminado.")

            elif opcion == "7":
                proyectos = Proyectos().consultar_proyectos(conexion)
                if not proyectos:
                    print("No hay proyectos registrados.")
                    continue

                for id_proyecto, nombre, descripcion, fecha in proyectos:
                    print(f"ID: {id_proyecto} | {nombre}")

                id_proyecto = int(input("ID del proyecto: ").strip())
                if not contiene_id(proyectos, id_proyecto):
                    print("Proyecto no existe.")
                    continue

                empleados = EmpleadoProyecto().consultar_empleados_proyecto(
                    conexion, id_proyecto
                )
                if not empleados:
                    print("El proyecto no tiene empleados asignados.")
                    continue

                for id_empleado, nombre, paterno, materno in empleados:
                    apellidos = " ".join(a for a in (paterno, materno) if a)
                    print(f"ID: {id_empleado} | {nombre} {apellidos}")

                empleado_id = int(input("ID del empleado que desasignarás: ").strip())
                if not contiene_id(empleados, empleado_id):
                    print("Ese empleado no está asignado al proyecto.")
                    continue

                sesion.desasignar_empleado_proyecto(
                    conexion, empleado_id, id_proyecto
                )
                print("Empleado desasignado del proyecto.")
            else:
                print("Opción no válida.")
        except ValueError as error:
            print(f"Comprueba ID ingresado: {error}")
        except oracledb.IntegrityError:
            if opcion == "1":
                print("Ya existe un proyecto con ese nombre.")
            elif opcion == "4":
                print("Ya existe otro proyecto con ese nombre.")
            elif opcion == "3":
                print("El empleado ya está asignado a ese proyecto.")
            elif opcion == "6":
                print("No se puede eliminar: el proyecto tiene asignaciones o registros de tiempo asociados.")
            elif opcion == "7":
                print("No se puede desasignar: hay registros de tiempo asociados a esa asignación.")
            else:
                print("La operación contiene un dato duplicado o inválido.")
        except oracledb.Error as error:
            print(f"Operación fallida en base de datos: {error}")
        except ConnectionError as error:
            print(error)

def registrar_empleado(conexion, sesion):
    nombre = input("Nombre: ").strip()
    while not nombre or len(nombre) > 50:
        print("Nombre obligatorio, máximo 50 caracteres.")
        nombre = input("Nombre: ").strip()

    apellido_paterno = input("Apellido paterno (opcional): ").strip() or None
    apellido_materno = input("Apellido materno (opcional): ").strip() or None

    direccion = input("Dirección (opcional): ").strip() or None
    telefono = input("Teléfono (opcional): ").strip() or None

    correo = input("Correo: ").strip()
    while (not correo or len(correo) > 30 or "@" not in correo
           or "." not in correo.split("@")[-1]):
        print("Ingresa un correo válido.")
        correo = input("Correo: ").strip()

    fecha_contrato = pedir_fecha("Fecha de contrato (DD-MM-YYYY): ")

    while True:
        try:
            salario = Decimal(input("Salario (mínimo 300000): ").strip())
            if salario >= 300000:
                break
            print("El salario debe ser igual o superior a 300000.")
        except InvalidOperation:
            print("Ingresa un salario numérico válido.")

    nombre_usuario = input("Nombre de usuario: ").strip()
    while not nombre_usuario or len(nombre_usuario) > 50:
        print("Nombre de usuario obligatorio, máximo 50 caracteres.")
        nombre_usuario = input("Nombre de usuario: ").strip()

    while True:
        contrasena = getpass("Contraseña de la cuenta: ")
        confirmacion = getpass("Confirme la contraseña: ")

        if contrasena and contrasena == confirmacion:
            break
        print("La contraseña está vacía o no coinciden. Inténtalo de nuevo.")

    roles = {"1": "Empleado", "2": "Gerente",
             "3": "Gestor de Proyecto", "4": "Administrador"}
    print("Rol de la cuenta: 1. Empleado | 2. Gerente | 3. Gestor de Proyecto | 4. Administrador")

    rol = roles.get(input("Selecciona el rol: ").strip())
    if rol is None:
        print("Opción de rol no válida.")
        return

    empleado = Empleados(None, nombre, apellido_paterno, apellido_materno,
                         direccion, telefono, correo, fecha_contrato,
                         salario, None)
    nuevo_id = sesion.registrar_empleado(
        conexion,
        empleado,
        nombre_usuario,
        contrasena,
        rol
    )
    print(f"Empleado y cuenta registrados. ID: {nuevo_id}")

def menu_administrador(conexion, sesion):
    while True:
        print("--- Menú de Administrador ---")
        print("1. Registrar empleado")
        print("2. Consultar empleados")
        print("3. Generar informes")
        print("0. Cerrar sesión")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            print("Cerrando sesión...")
            return

        if opcion == "3":
            informes = {"1": "empleados", "2": "proyectos", "3": "departamentos",
                        "4": "registros de tiempo"}
            while True:
                print("--- Informes ---")
                print("1. Informe de empleados")
                print("2. Informe de proyectos")
                print("3. Informe de departamentos")
                print("4. Informe de registros de tiempo")
                print("5. Volver al menú de administrador")
                opcion_informe = input("Seleccione un informe: ").strip()

                if opcion_informe == "5":
                    break

                if opcion_informe not in informes:
                    print("Opción no válida.")
                    continue

                print(f"Informe de {informes[opcion_informe]} creado.")
            continue

        try:
            if opcion == "1":
                registrar_empleado(conexion, sesion)

            elif opcion == "2":
                empleados = Empleados().consultar_todos(conexion)
                if not empleados:
                    print("No hay empleados registrados.")
                    continue
                print("--- Empleados ---")
                for id_empleado, nombre, paterno, materno, fecha in empleados:
                    apellidos = " ".join(a for a in (paterno, materno) if a)
                    print(f"ID: {id_empleado} | {nombre} {apellidos} | Contrato: {fecha or 'Sin fecha'}")
            else:
                print("Opción no válida.")
        except oracledb.IntegrityError:
            print("El correo o nombre de usuario ya está registrado.")
        except oracledb.Error as error:
            print(f"La base de datos rechazó la operación: {error}")
        except ConnectionError as error:
            print(error)

def menu_empleado(conexion, sesion):
    while True:
        print("--- Menú de Empleado ---")
        print("1. Consultar mis proyectos")
        print("2. Registrar horas y tareas")
        print("3. Consultar mis registros")
        print("0. Cerrar sesión")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "0":
            print("Cerrando sesión...")
            return

        try:
            if opcion == "1":
                proyectos = EmpleadoProyecto().consultar_proyectos_empleado(
                    conexion, sesion.empleado_id
                )
                if not proyectos:
                    print("No tienes proyectos asignados.")
                    continue
                print("--- Tus proyectos ---")
                for id_proyecto, nombre, fecha_asignacion in proyectos:
                    print(
                        f"ID: {id_proyecto} | {nombre} | "
                        f"Asignado: {fecha_asignacion}"
                    )

            elif opcion == "2":
                proyectos = EmpleadoProyecto().consultar_proyectos_empleado(
                    conexion, sesion.empleado_id
                )
                if not proyectos:
                    print("No tienes proyectos asignados.")
                    continue
                print("--- Tus proyectos ---")
                for id_proyecto, nombre, fecha_asignacion in proyectos:
                    print(f"ID: {id_proyecto} | {nombre}")

                proyecto_id = int(input("ID del proyecto: ").strip())
                if not contiene_id(proyectos, proyecto_id):
                    print("Ese proyecto no está asignado a tu cuenta.")
                    continue

                fecha = pedir_fecha("Fecha del registro (DD-MM-YYYY): ")

                while True:
                    try:
                        horas = Decimal(input("Horas trabajadas: ").strip())
                        if horas.is_finite() and Decimal("0") < horas <= Decimal("999.99"):
                            break
                        print("Las horas deben ser mayores que cero y no superar 999.99.")
                    except InvalidOperation:
                        print("Ingresa una cantidad numérica válida.")

                descripcion = input("Descripción de las tareas: ").strip()
                if not descripcion:
                    print("La descripción de las tareas es obligatoria.")
                    continue

                registro = Registrotiempo(
                    empleado_id=sesion.empleado_id,
                    proyecto_id=proyecto_id,
                    fecha=fecha,
                    horas_trabajadas=horas,
                    descripcion_tareas=descripcion
                )
                registro.registrar(conexion)
                print("Registro de tiempo guardado.")

            elif opcion == "3":
                registros = Registrotiempo().consultar_por_empleado(
                    conexion, sesion.empleado_id
                )
                if not registros:
                    print("Todavía no tienes registros de tiempo.")
                    continue
                print("--- Tus registros de tiempo ---")
                for id_registro, proyecto, fecha, horas, descripcion in registros:
                    print(
                        f"ID: {id_registro} | Proyecto: {proyecto} | "
                        f"Fecha: {fecha} | Horas: {horas} | Tareas: {descripcion}"
                    )
            else:
                print("Opción no válida.")
        except ValueError as error:
            print(f"Revisa el ID ingresado: {error}")
        except oracledb.Error as error:
            print(f"Oracle rechazó la operación: {error}")
        except ConnectionError as error:
            print(error)

sesion = CuentasAcceso()

if conexion.cursor is None:
    print("No se puede iniciar sesión porque no hay conexión con Oracle.")
else:
    usuario = input("Usuario: ")
    contrasena = getpass("Contraseña: ")

    if sesion.autenticar(usuario, contrasena, conexion):
        tipos_empleado = {
            "Administrador": Administrador,
            "Gerente": Gerente,
            "Gestor de Proyecto": GestorProyectos,
            "Empleado": Empleados
        }
        tipo_empleado = tipos_empleado.get(sesion.rol)

        if tipo_empleado is None:
            print("La cuenta tiene un rol no reconocido.")
        else:
            empleado_sesion = tipo_empleado(id_empleado=sesion.empleado_id)

            if isinstance(empleado_sesion, Administrador):
                print(f"Sesión iniciada, rol: {sesion.rol}")
                menu_administrador(conexion, empleado_sesion)
            elif isinstance(empleado_sesion, Gerente):
                print(f"Sesión iniciada, rol: {sesion.rol}")
                menu_gerente(conexion, empleado_sesion)
            elif isinstance(empleado_sesion, GestorProyectos):
                print(f"Sesión iniciada, rol: {sesion.rol}")
                menu_gestor_proyecto(conexion, empleado_sesion)
            else:
                print(f"Sesión iniciada, rol: {sesion.rol}")
                menu_empleado(conexion, empleado_sesion)
    else:
        print("Usuario o contraseña incorrectos")