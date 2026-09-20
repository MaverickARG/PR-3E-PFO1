import socket
import sys

# Configuración del servidor (misma que en server.py)
HOST = "localhost"
PORT = 5000
PALABRA_SALIDA = "éxito"  # Palabra que corta el chat


def inicializar_conexion(host, port):
    # Crear el socket TCP y conectar al servidor
    try:
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((host, port))
        print(f"Conectado al servidor {host}:{port}")
        return cliente_socket
    except ConnectionRefusedError:
        # El servidor no está corriendo o no acepta conexiones
        print("No se pudo conectar: el servidor no está disponible.")
        sys.exit(1)
    except OSError as e:
        print(f"Error de conexión: {e}")
        sys.exit(1)


def enviar_mensajes(sock, palabra_salida):
    # Bucle principal: manda mensajes y muestra la respuesta hasta escribir "éxito"
    with sock:
        while True:
            mensaje = input(f"Escribí tu mensaje ('{palabra_salida}' para salir): ")

            if mensaje.strip().lower() == palabra_salida:
                print("Cerrando conexión...")
                break  # Corta el bucle y cierra la conexión

            if not mensaje.strip():
                print("El mensaje está vacío, escribí algo.")
                continue

            try:
                # Enviar el mensaje al servidor
                sock.sendall(mensaje.encode("utf-8"))
                # Recibir la respuesta del servidor
                respuesta = sock.recv(1024).decode("utf-8")
                print(f"Servidor: {respuesta}")
            except (ConnectionResetError, BrokenPipeError):
                print("Se perdió la conexión con el servidor.")
                break


def main():
    cliente_socket = inicializar_conexion(HOST, PORT)
    enviar_mensajes(cliente_socket, PALABRA_SALIDA)


if __name__ == "__main__":
    main()