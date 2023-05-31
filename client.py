import socket
import threading
import os

INICIO_TRANSFERENCIA = 'INICIO_TRANSFERENCIA'
FIN_TRANSFERENCIA = 'FIN_TRANSFERENCIA'

class Cliente:
    # Constructor del Cliente
    def __init__(self, host = 'localhost', puerto = 3001):
        self.apodo = input("Ingresa tu apodo: ")
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))
        self.cliente.send(self.apodo.encode('utf-8'))

    # Método para recibir datos del servidor
    def recibir(self):
        recibiendo_archivo = False
        datos_archivo = b''
        while True:
            # Recepción del mensaje del servidor
            mensaje = self.cliente.recv(4096)
            # Verificar el inicio y final de la transferencia
            if mensaje.decode('utf-8') == INICIO_TRANSFERENCIA:
                recibiendo_archivo = True
                datos_archivo = b''
                continue
            elif mensaje.decode('utf-8') == FIN_TRANSFERENCIA:
                recibiendo_archivo = False
                # Escribir los datos en un archivo
                with open('archivo_recibido', 'wb') as f:
                    f.write(datos_archivo)
                continue
            # Si se está recibiendo un archivo, agregar los datos
            elif recibiendo_archivo:
                datos_archivo += mensaje
                continue
            elif mensaje == 'Apodo':
                print('chingadamadre')
            else:
                # Imprimir el mensaje
                print(mensaje.decode('utf-8'))


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
        with open(nombre_archivo, 'rb') as f:
            while True:
                bytes_leidos = f.read(4096)
                if not bytes_leidos:
                    break
                socket.sendall(bytes_leidos)

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