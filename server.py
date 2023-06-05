import socket
import threading

INICIO_TRANSFERENCIA = 'INICIO_TRANSFERENCIA'
FIN_TRANSFERENCIA = 'FIN_TRANSFERENCIA'

class Servidor:
    # Constructor del servidor
    def __init__(self, host = 'localhost', puerto = 6000):
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
            print("Cliente desconectado.")
            return
        recibiendo_archivo = False
        nombre_archivo = ''
        datos_archivo = b''
        while True:
            try:
                # Recepción del mensaje del cliente
                mensaje = cliente.recv(1024)
                if mensaje.decode('utf-8').startswith(INICIO_TRANSFERENCIA):
                    recibiendo_archivo = True
                    _, nombre_archivo = mensaje.decode('utf-8').split(' ')
                    datos_archivo = b''
                    continue
                elif mensaje.decode('utf-8') == FIN_TRANSFERENCIA:
                    recibiendo_archivo = False
                    # Escribir los datos en un archivo
                    with open(nombre_archivo, 'wb') as f:
                        f.write(datos_archivo)
                    self.difundir(f"{apodo} has shared a file: {nombre_archivo}".encode('utf-8'), cliente)
                    continue
                elif recibiendo_archivo:
                    datos_archivo += mensaje
                    continue
                else:
                    # Enviar el mensaje a todos los demás clientes
                    self.difundir(mensaje, cliente)
            except:
                # Si hay un error, eliminar el cliente de la lista de clientes
                del self.clientes[cliente]
            cliente.close()
            self.difundir(f"\n**{apodo} dejó el chat".encode('utf-8'), cliente=None)
            break

    # Método para aceptar nuevas conexiones
    def recibir(self):
        while True:
            # Aceptar una nueva conexión
            cliente, direccion = self.servidor.accept()
            print(f"Conectado con {str(direccion)}")
            
            # Solicitar y recibir el apodo del cliente
            apodo = cliente.recv(1024).decode('utf-8')
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