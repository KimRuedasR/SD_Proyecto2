import socket
import threading

# Definición de la clase Servidor
class Servidor:
    # El constructor de la clase Servidor
    def __init__(self, host = '148.220.208.133', port = 5000):
        self.host = host
        self.port = port
        # Inicialización del socket
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.port))
        self.clientes = {}

    # Método para enviar un mensaje a todos los clientes excepto a uno
    def difundir(self, mensaje, cliente):
        for c in self.clientes:
            if c != cliente:
                c.send(mensaje)

    # Método para manejar la comunicación con un cliente
    def manejar(self, cliente):
        while True:
            try:
                # Recepción del mensaje del cliente
                mensaje = cliente.recv(1024)
                # Envío del mensaje a todos los demás clientes
                self.difundir(mensaje, cliente)
            except:
                # Si hay un error, eliminar el cliente de la lista de clientes
                del self.clientes[cliente]
                # Cerrar la conexión con el cliente
                cliente.close()
                self.difundir(f"\n**{self.clientes[cliente]} dejo el chat".encode('utf-8'))
                break

    # Método para aceptar nuevas conexiones
    def recibir(self):
        while True:
            # Aceptar una nueva conexión
            cliente, direccion = self.servidor.accept()
            print(f"Conectado con {str(direccion)}")
            
            # Solicitar y recibir el apodo del cliente
            cliente.send('NICK'.encode('utf-8'))
            apodo = cliente.recv(1024).decode('utf-8')
            self.clientes[cliente] = apodo
            
            print(f"El apodo del cliente es {apodo}!")
            self.difundir(f'\n+¡@{apodo} se unió al chat!'.encode('utf-8'), cliente)
            cliente.send('*** ¡Conectado al servidor! ***'.encode('utf-8'))

            # Iniciar un nuevo thread para manejar la comunicación con el cliente
            hilo = threading.Thread(target=self.manejar, args=(cliente,))
            hilo.start()

    # Método para iniciar el servidor
    def iniciar(self):
        print("*** ¡Servidor iniciado! ***")
        # Comenzar a escuchar conexiones entrantes
        self.servidor.listen()
        # Iniciar el método de recibir
        self.recibir()

# Creación e inicio del servidor
servidor = Servidor()
servidor.iniciar()
