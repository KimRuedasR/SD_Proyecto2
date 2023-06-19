import socket
import threading

INICIO_TRANSFERENCIA = 'INICIO_TRANSFERENCIA'
FIN_TRANSFERENCIA = 'FIN_TRANSFERENCIA'
buff=4096

class Servidor:
    # Constructor del servidor
    def __init__(self, host = '148.220.209.110', puerto = 5000):
        self.host = host
        self.puerto = puerto
        # Inicialización del socket
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.puerto))
        self.clientes = {}

    # Método para enviar un mensaje a todos los clientes
    def difundir(self, mensaje, cliente):
        for c in self.clientes:
            if c != cliente:  # No enviar mensaje al remitente
                c.send(mensaje)

    # Método para manejar las transferencias de datos
    def manejar(self, cliente):
        while True:
            try:
                mensaje = cliente.recv(buff)
                self.difundir(mensaje, cliente)
            except:
                apodo = self.clientes[cliente]  # Guardar el apodo antes de eliminar al cliente
                del self.clientes[cliente]
                cliente.close()
                self.difundir(f"\n**{apodo} dejó el chat".encode('utf-8'), cliente=None)
                break

    # Método para aceptar nuevas conexiones
    def recibir(self):
        while True:
            cliente, direccion = self.servidor.accept()
            print(f"Conectado con {str(direccion)}")
            apodo = cliente.recv(buff).decode('utf-8')
            self.clientes[cliente] = apodo
            print(f"El apodo del cliente es {apodo}")  # Imprimir el apodo del cliente
            self.difundir(f'\n+¡@{apodo} se unió al chat!'.encode('utf-8'), cliente)
            cliente.send('*** ¡Conectado al servidor! ***'.encode('utf-8'))
            hilo = threading.Thread(target=self.manejar, args=(cliente,))
            hilo.start()

    # Método para iniciar el servidor
    def iniciar(self):
        print("*** ¡Servidor iniciado! ***")
        self.servidor.listen()
        self.recibir()

# Creación e inicio del servidor
servidor = Servidor()
servidor.iniciar()
