import socket
import threading
import os

INICIO_TRANSFERENCIA = 'INICIO_TRANSFERENCIA'
FIN_TRANSFERENCIA = 'FIN_TRANSFERENCIA'

class Cliente:
    # Constructor del Cliente
    def __init__(self, host = 'localhost', puerto = 6000):
        self.apodo = input("Ingresa tu apodo: ")
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))
        self.cliente.send(self.apodo.encode('utf-8'))

    # Método para recibir datos del servidor
    def recibir(self):
        recibiendo_archivo = False
        nombre_archivo = ''
        datos_archivo = b''
        while True:
            try:
                mensaje = self.cliente.recv(1024)
                if mensaje.decode('utf-8').startswith(INICIO_TRANSFERENCIA):
                    recibiendo_archivo = True
                    _, nombre_archivo = mensaje.decode('utf-8').split(' ')
                    datos_archivo = b''
                    continue
                elif mensaje.decode('utf-8') == FIN_TRANSFERENCIA:
                    recibiendo_archivo = False
                    with open(nombre_archivo, 'wb') as f:
                        f.write(datos_archivo)
                    print(f"\nReceived file: {nombre_archivo}")
                    continue
                elif recibiendo_archivo:
                    datos_archivo += mensaje
                    continue
                else:
                    print(mensaje.decode('utf-8'))
            except:
                print("¡Ocurrió un error!")
                self.cliente.close()
                break


    # Método para enviar datos al servidor
    def escribir(self):
        while True:
            print("\nElige una opción: ")
            print("1. Chat")
            print("2. Enviar archivo")
            print("3. Recibir archivo")
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
                self.cliente.send(INICIO_TRANSFERENCIA.encode('utf-8'))
                self.enviar_archivo(nombre_archivo, self.cliente)
                self.cliente.send(FIN_TRANSFERENCIA.encode('utf-8'))
            elif opcion == "3":
                nombre_archivo = input("\n--Ingresa el nombre del archivo a recibir: ")
                self.recibir_archivo(nombre_archivo, self.cliente)
            else:
                print("\nOpción incorrecta. Intenta de nuevo.")

    # Método para enviar un archivo al servidor
    def enviar_archivo(self, nombre_archivo, socket):
        socket.send(f"{INICIO_TRANSFERENCIA} {nombre_archivo}".encode('utf-8'))
        with open(nombre_archivo, 'rb') as f:
            while True:
                bytes_leidos = f.read(4096)
                if not bytes_leidos:
                    break
                socket.sendall(bytes_leidos)
        socket.send(FIN_TRANSFERENCIA.encode('utf-8'))

    # Método para recibir un archivo del servidor
    def recibir_archivo(self, nombre_archivo, socket):
        with open(nombre_archivo, 'wb') as f:
            while True:
                datos = socket.recv(4096)
                if not datos:
                    break
                f.write(datos)

    # Método para iniciar los threads de recibir y escribir
    def iniciar(self):
        hilo_recibir = threading.Thread(target=self.recibir)
        hilo_recibir.start()

        hilo_escribir = threading.Thread(target=self.escribir)
        hilo_escribir.start()

# Creación y inicio del cliente
cliente = Cliente()
cliente.iniciar()