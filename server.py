import socket
import sqlite3
import sys
from datetime import datetime

# Configuración del servidor
HOST = "localhost"       # Escucha en localhost (máquina local)
PORT = 5000              # Puerto arbitrario (debe ser > 1024)
DB_PATH = "mensajes.db"  # Archivo donde se guarda la base de datos SQLite

    # Crea la tabla de mensajes
def inicializar_db(db_path):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        """)
        conexion.commit()
        conexion.close()
        print(f"Base de datos '{db_path}' lista.")
    except sqlite3.Error as e:
        # Caso "DB no accesible": permisos, disco lleno, ruta inválida, etc.
        print(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)  # Sin base de datos no tiene sentido seguir

# Inserta un mensaje nuevo en la tabla y devuelve si salió bien o no
def guardar_mensaje(db_path, contenido, ip_cliente, fecha_envio):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)",
            (contenido, fecha_envio, ip_cliente)
        )
        conexion.commit()
        conexion.close()
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar el mensaje en la base de datos: {e}")
        return False

#Configuración del socket TCP/IP
def inicializar_socket(host, port):
    try:
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sys.platform == "win32":
            # En Windows, SO_REUSEADDR permite bindear un puerto ya ocupado sin
            # avisar. SO_EXCLUSIVEADDRUSE evita eso y sí lanza "address already in use".
            servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            # Permite reusar el puerto enseguida si el servidor se reinicia
            servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Vincular el socket al puerto y host
        servidor_socket.bind((host, port))
        # Escuchar conexiones entrantes (cola de hasta 5 pendientes)
        servidor_socket.listen(5)
        print(f"Servidor escuchando en {host}:{port}...")
        return servidor_socket
    except OSError as e:
        # "Address already in use" (puerto ocupado)
        print(f"Error al inicializar el socket: {e}")
        sys.exit(1)


def atender_cliente(conn, addr, db_path):
    # Atiende a un cliente ya conectado
    ip_cliente = addr[0]
    print(f"Conexión establecida desde {ip_cliente}")

    with conn:
        while True:
            try:
                # Recibir el mensaje del cliente (hasta 1024 bytes)
                datos = conn.recv(1024)
            except ConnectionResetError:
                print(f"El cliente {ip_cliente} cerró la conexión abruptamente.")
                break

            if not datos:
                break  # Si no hay datos cerrar conexión

            mensaje = datos.decode("utf-8")
            print(f"Mensaje de {ip_cliente}: {mensaje}")

            # Guardar el mensaje en la base de datos
            fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guardado = guardar_mensaje(db_path, mensaje, ip_cliente, fecha_envio)

            # Armar la respuesta según si se pudo guardar o no
            if guardado:
                respuesta = f"Mensaje recibido: {fecha_envio}"
            else:
                respuesta = "Error: no se pudo guardar el mensaje en el servidor"

            # Enviar la respuesta al cliente
            conn.sendall(respuesta.encode("utf-8"))

    print(f"Conexión con {ip_cliente} cerrada.")


def main():
    # Preparar la base de datos y el socket antes de aceptar clientes
    inicializar_db(DB_PATH)
    servidor_socket = inicializar_socket(HOST, PORT)

    try:
        while True:
            # Aceptar una conexión entrante
            conn, addr = servidor_socket.accept()
            atender_cliente(conn, addr, DB_PATH)
    except KeyboardInterrupt:
        print("\nServidor detenido manualmente (Ctrl+C).")
    finally:
        servidor_socket.close()


if __name__ == "__main__":
    main()