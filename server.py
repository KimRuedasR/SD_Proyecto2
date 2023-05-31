import socket
import threading

INICIO_TRANSFERENCIA = 'INICIO_TRANSFERENCIA'
FIN_TRANSFERENCIA = 'FIN_TRANSFERENCIA'

class Servidor:
    # Constructor del servidor
    def __init__(self, host = 'localhost', puerto = 3001):
        self.host = host
        self.puerto = puerto
        # Inicialización del socket
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.puerto))
        self.clientes = {}

    # Método para enviar un mensaje a todos los clientes
    def difundir(self, mensaje, cliente):
        for c in self.clientes:
            # No enviar el mensaje al cliente emisor
             if c != cliente:
                try:
                    c.send(mensaje)
                except BrokenPipeError:
                    # Manejo de errores
                    print(f"No se pudo enviar mensaje a {self.clientes[c]}. Cliente desconectado.")
                    c.close()
                    del self.clientes[c]
                    
    # Método para transferencia de datos
    def manejar(self, cliente):
        try:
            apodo = self.clientes[cliente]
        except KeyError:
            print("Cliente desconocido.")
            return
        recibiendo_archivo = False
        datos_archivo = b''
        while True:
            try:
                # Recepción del mensaje del cliente
                mensaje = cliente.recv(4096)
                # Verificar el inicio y final de la transferencia
                if mensaje.decode('utf-8') == INICIO_TRANSFERENCIA:
                    recibiendo_archivo = True
                    datos_archivo = b''
                    continue
                elif mensaje.decode('utf-8') == FIN_TRANSFERENCIA:
                    recibiendo_archivo = False
                    continue
                # Si se está recibiendo un archivo, agregar los datos
                elif recibiendo_archivo:
                    datos_archivo += mensaje
                    continue
                # Enviar el mensaje a todos los demás clientes
                self.difundir(mensaje, cliente)
            except:
                # Si hay un error, eliminar el cliente de la lista de clientes
                del self.clientes[cliente]
                # Cerrar la conexión con el cliente
                cliente.close()
                # Notificar a todos los clientes que este cliente ha dejado el chat
                self.difundir(f"\n**{apodo} dejó el chat".encode('utf-8'), cliente=None)
                break

    # Método para aceptar nuevas conexiones
    def recibir(self):
        while True:
            # Aceptar una nueva conexión
            cliente, direccion = self.servidor.accept()
            print(f"Conectado con {str(direccion)}")
            
            # Solicitar y recibir el apodo del cliente
            apodo = cliente.recv(4096).decode('utf-8')
            self.clientes[cliente] = apodo
            
            print(f"El apodo del cliente es {apodo}")
            self.difundir(f'\n+¡@{apodo} se unió al chat!'.encode('utf-8'), cliente)
            cliente.send('*** ¡Conectado al servidor! ***'.encode('utf-8'))

            #Iniciar un nuevo hilo para manejar la comunicación con el cliente
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