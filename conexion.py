import oracledb

class ConexionDB:
    def __init__(self):
        try:
            self.conexion = oracledb.connect(
                user="POO", 
                password="inacap", 
                host="localhost",
                port=1521,          
                service_name="xe"   
            )
            self.cursor = self.conexion.cursor()
            print("Conexión exitosa a localhost.")
            
        except Exception as error:
            print(f"ERROR CRÍTICO DE CONEXIÓN: Detalle: {error}")
            self.conexion = None
            self.cursor = None