import socket
import threading

class Servidor:
    def __init__(self, host = 'localhost', port = 5000):
        self.host = host
        self.port = port
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.port))
        self.clientes = {}

    def difundir(self, mensaje, cliente):
        for c in self.clientes:
            if c != cliente:
                c.send(mensaje)

    def manejar(self, cliente):
        while True:
            try:
                mensaje = cliente.recv(1024)
                self.difundir(mensaje, cliente)
            except:
                del self.clientes[cliente]
                cliente.close()
                self.difundir(f"\n**{self.clientes[cliente]} dejo el chat".encode('utf-8'))
                break

    def recibir(self):
        while True:
            cliente, direccion = self.servidor.accept()
            print(f"Conectado con {str(direccion)}")
            
            cliente.send('NICK'.encode('utf-8'))
            apodo = cliente.recv(1024).decode('utf-8')
            self.clientes[cliente] = apodo
            
            print(f"El apodo del cliente es {apodo}!")
            self.difundir(f'\n+¡@{apodo} se unió al chat!'.encode('utf-8'), cliente)
            cliente.send('*** ¡Conectado al servidor! ***'.encode('utf-8'))

            hilo = threading.Thread(target=self.manejar, args=(cliente,))
            hilo.start()

    def iniciar(self):
        print("*** ¡Servidor iniciado! ***")
        self.servidor.listen()
        self.recibir()

servidor = Servidor()
servidor.iniciar()
