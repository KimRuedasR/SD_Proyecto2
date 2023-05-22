import socket
import threading

class NodoP2P:
    def __init__(self, direccion_servidor, puerto_servidor):
        self.direccion_servidor = direccion_servidor
        self.puerto_servidor = puerto_servidor
        self.ip_anfitrion = None
        self.ip_pareja = None

    # Conectarse al servidor y obtener la dirección IP asignada
    def login(self):
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect((self.direccion_servidor, self.puerto_servidor))
        self.ip_anfitrion = socket_cliente.recv(1024).decode()
        socket_cliente.close()

    # Conectarse con la otra máquina y enviar/recibir direcciones IP
    def intercambiar_ips(self):
        socket_pareja = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pareja.connect((self.ip_pareja, self.puerto_servidor))
        socket_pareja.send(self.ip_anfitrion.encode())
        self.ip_pareja = socket_pareja.recv(1024).decode()
        socket_pareja.close()

    # Manejar la conexión con la otra máquina
    def manejar_conexion(self, socket_cliente, direccion):
        self.ip_pareja = socket_cliente.recv(1024).decode()
        socket_cliente.send(self.ip_anfitrion.encode())
        socket_cliente.close()

    # Iniciar un socket en espera de conexiones entrantes
    def iniciar_escucha(self):
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.bind(('0.0.0.0', self.puerto_servidor))
        socket_servidor.listen(1)

        while True:
            socket_cliente, direccion = socket_servidor.accept()
            threading.Thread(target=self.manejar_conexion, args=(socket_cliente, direccion)).start()

    # Iniciar el proceso P2P
    def iniciar(self):
        self.login()
        print(f'IP asignada: {self.ip_anfitrion}')

        self.ip_pareja = input('Ingrese la dirección IP de la otra máquina: ')

        self.intercambiar_ips()
        print(f'Conectado con la otra máquina. Su IP es: {self.ip_pareja}')

        threading.Thread(target=self.iniciar_escucha).start()

        while True:
            mensaje = input('Mensaje a enviar: ')
            self.enviar_mensaje(mensaje)

    # Enviar mensaje a la otra máquina
    def enviar_mensaje(self, mensaje):
        socket_pareja = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pareja.connect((self.ip_pareja, self.puerto_servidor))
        socket_pareja.send(mensaje.encode())
        socket_pareja.close()

if __name__ == '__main__':
    # Reemplazar dirección IP y número de puerto
    direccion_servidor = 'DIRECCION_SERVIDOR' 
    puerto_servidor = 12345
    nodo = NodoP2P(direccion_servidor, puerto_servidor)
    nodo.iniciar()
