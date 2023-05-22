import socket
import threading

class ServidorP2P:
    def __init__(self, direccion_servidor, puerto_servidor):
        self.direccion_servidor = direccion_servidor
        self.puerto_servidor = puerto_servidor

    def manejar_conexion(self, socket_cliente, direccion):
        # Manejar la conexión con un cliente
        ip_cliente = socket_cliente.recv(1024).decode()
        print(f'Conexión establecida con {ip_cliente}')

        # Enviar la dirección IP del servidor al cliente
        socket_cliente.send(self.direccion_servidor.encode())

        socket_cliente.close()

    def iniciar(self):
        # Iniciar el servidor
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.bind((self.direccion_servidor, self.puerto_servidor))
        socket_servidor.listen(5)

        print(f'Servidor P2P en {self.direccion_servidor}:{self.puerto_servidor}')

        while True:
            socket_cliente, direccion = socket_servidor.accept()
            threading.Thread(target=self.manejar_conexion, args=(socket_cliente, direccion)).start()

if __name__ == '__main__':
    direccion_servidor = 'localhost'  # Dirección IP del servidor (localhost para pruebas en la misma máquina)
    puerto_servidor = 5000  # Número de puerto para el servidor P2P
    servidor = ServidorP2P(direccion_servidor, puerto_servidor)
    servidor.iniciar()
