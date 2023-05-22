import socket
import threading

class ClienteP2P:
    def __init__(self, direccion_servidor, puerto_servidor):
        self.direccion_servidor = direccion_servidor
        self.puerto_servidor = puerto_servidor
        self.ip_anfitrion = None
        self.ip_pareja = None

    def login(self):
        # Conectarse al servidor y obtener la dirección IP asignada
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect((self.direccion_servidor, self.puerto_servidor))
        self.ip_anfitrion = socket_cliente.recv(1024).decode()
        socket_cliente.close()

    def intercambiar_ips(self):
        # Conectarse con la otra máquina y enviar/recibir direcciones IP
        socket_pareja = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pareja.connect((self.ip_pareja, self.puerto_servidor))
        socket_pareja.send(self.ip_anfitrion.encode())
        self.ip_pareja = socket_pareja.recv(1024).decode()
        socket_pareja.close()

    def manejar_conexion(self, socket_cliente, direccion):
        # Manejar la conexión con la otra máquina
        self.ip_pareja = socket_cliente.recv(1024).decode()
        socket_cliente.send(self.ip_anfitrion.encode())
        socket_cliente.close()

    def iniciar_escucha(self):
        # Iniciar un socket en espera de conexiones entrantes
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.bind(('0.0.0.0', self.puerto_servidor))
        socket_servidor.listen(1)

        while True:
            socket_cliente, direccion = socket_servidor.accept()
            threading.Thread(target=self.manejar_conexion, args=(socket_cliente, direccion)).start()

    def enviar_mensaje(self, mensaje):
        # Enviar mensaje a la otra máquina
        socket_pareja = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pareja.connect((self.ip_pareja, self.puerto_servidor))
        socket_pareja.send(mensaje.encode())

        respuesta = socket_pareja.recv(1024).decode()
        print(f'Respuesta recibida: {respuesta}')

        socket_pareja.close()

    def iniciar(self):
        # Iniciar el proceso P2P
        self.login()
        print(f'IP asignada: {self.ip_anfitrion}')

        self.ip_pareja = input('Ingrese la dirección IP de la otra máquina: ')

        self.intercambiar_ips()
        print(f'Conectado con la otra máquina. Su IP es: {self.ip_pareja}')

        threading.Thread(target=self.iniciar_escucha).start()

        while True:
            mensaje = input('Mensaje a enviar: ')
            self.enviar_mensaje(mensaje)


if __name__ == '__main__':
    direccion_servidor = 'localhost' 
    puerto_servidor = 5000
    cliente = ClienteP2P(direccion_servidor, puerto_servidor)
    cliente.iniciar()
