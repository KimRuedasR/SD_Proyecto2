import socket
import threading

class NodoP2P:
    def __init__(self, direccion_servidor):
        self.direccion_servidor = direccion_servidor
        self.ip_host = None
        self.ip_par = None

    # Conectarse al servidor y obtener la dirección IP asignada
    def login(self):
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect(self.direccion_servidor)
        self.ip_host = socket_cliente.recv(1024).decode()
        socket_cliente.close()
    
    # Conectarse con el otro host y enviar/recibir direcciones IP
    def intercambiar_ips(self):
        socket_par = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_par.connect((self.ip_par, 12345))
        socket_par.send(self.ip_host.encode())
        self.ip_par = socket_par.recv(1024).decode()
        socket_par.close()
    
    # Manejar la conexión con el otro host
    def manejar_conexion(self, socket_cliente, direccion):
        self.ip_par = socket_cliente.recv(1024).decode()
        socket_cliente.send(self.ip_host.encode())
        socket_cliente.close()

    
    # Iniciar un socket en espera de conexiones entrantes
    def iniciar_escucha(self):
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.bind(('0.0.0.0', 12345))
        socket_servidor.listen(1)

        while True:
            socket_cliente, direccion = socket_servidor.accept()
            threading.Thread(target=self.manejar_conexion, args=(socket_cliente, direccion)).start()

    # Iniciar el proceso P2P
    def iniciar(self):
        self.login()
        print(f'IP asignada: {self.ip_host}')

        self.ip_par = input('Introduce la dirección IP del otro host: ')

        self.intercambiar_ips()
        print(f'Conectado con el otro host. Su IP es: {self.ip_par}')

        threading.Thread(target=self.iniciar_escucha).start()

        while True:
            mensaje = input('Mensaje a enviar: ')
            self.enviar_mensaje(mensaje)

    # Enviar mensaje al otro host
    def enviar_mensaje(self, mensaje):
        socket_par = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_par.connect((self.ip_par, 12345))
        socket_par.send(mensaje.encode())
        socket_par.close()

if __name__ == '__main__':
    # Reemplaza con la dirección IP del servidor
    direccion_servidor = ('DIRECCION_IP_SERVIDOR', 12345)
    nodo = NodoP2P(direccion_servidor)
    nodo.iniciar()
