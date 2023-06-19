import socket
import threading

INICIO_TRANSFERENCIA = 'INICIO_TRANSFERENCIA'
FIN_TRANSFERENCIA = 'FIN_TRANSFERENCIA'
buff=1024

class Cliente:
    # Constructor del Cliente
    def __init__(self, host='localhost', puerto=6000):
        self.apodo = input("Ingresa tu apodo: ")
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))
        self.cliente.send(self.apodo.encode('utf-8'))

    # Método para recibir datos del servidor
    def recibir(self):
        while True:
            mensaje = self.cliente.recv(buff)
            # Comprobar si el mensaje es el indicador de inicio de transferencia de archivo
            if mensaje.decode('utf-8') == INICIO_TRANSFERENCIA:
                self.recibir_archivo(mensaje)
            else:
                # Si el mensaje no es un indicador de transferencia, imprimir el mensaje
                print(mensaje.decode('utf-8'))

    # Método para enviar un archivo al servidor
    def enviar_archivo(self, nombre_archivo):
        # Enviar el indicador de inicio de transferencia al servidor
        self.cliente.send(INICIO_TRANSFERENCIA.encode('utf-8'))
        # Leer el archivo y enviar los datos al servidor
        with open(nombre_archivo, 'rb') as f:
            while True:
                data = f.read(buff)
                if not data:
                    break
                self.cliente.send(data)
        # Enviar el indicador de fin de transferencia al servidor
        self.cliente.send(FIN_TRANSFERENCIA.encode('utf-8'))

    # Método para recibir un archivo del servidor
    def recibir_archivo(self, mensaje):
        # Crear y abrir un nuevo archivo y escribir los datos recibidos en él
        with open('archivo_recibido', 'wb') as f:
            while True:
                data = self.cliente.recv(buff)
                # Comprobar si los datos recibidos son el indicador de fin de transferencia
                if data.endswith(FIN_TRANSFERENCIA.encode('utf-8')):
                    # Escribir los datos restantes y terminar el bucle
                    f.write(data[:-len(FIN_TRANSFERENCIA)])
                    break
                # Escribir los datos en el archivo
                f.write(data)
        # Imprimir un mensaje indicando que el archivo ha sido recibido
        print("\n** Archivo recibido con éxito. **")

    # Método para enviar datos al servidor
    def escribir(self):
        while True:
            print("\nElige una opción: ")
            print("1. Chat")
            print("2. Enviar archivo")
            opcion = input()
            if opcion == "1":
                while True:
                    mensaje = input("--Enviar mensaje: ")
                    if mensaje.lower() == 'salir':
                        break
                    mensaje_completo = f'\n@{self.apodo}: {mensaje}'
                    self.cliente.send(mensaje_completo.encode('utf-8'))
            elif opcion == "2":
                nombre_archivo = input("\n--Ingresa el nombre del archivo a enviar: ")
                self.enviar_archivo(nombre_archivo)
            else:
                print("\nOpción incorrecta. Intenta de nuevo.")

    # Método para iniciar los threads de recibir y escribir
    def iniciar(self):
        hilo_recibir = threading.Thread(target=self.recibir)
        hilo_recibir.start()

        hilo_escribir = threading.Thread(target=self.escribir)
        hilo_escribir.start()

# Creación e inicio del cliente
cliente = Cliente()
cliente.iniciar()
