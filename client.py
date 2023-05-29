import socket
import threading
import os

FILE_TRANSFER_START = 'FILE_TRANSFER_START'
FILE_TRANSFER_END = 'FILE_TRANSFER_END'
# Definición de la clase Cliente
class Cliente:
    # El constructor de la clase Cliente
    def __init__(self, host = '148.220.208.133', port = 5000):
        self.apodo = input("Ingresa tu apodo: ")
        # Inicialización del socket
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Conexión al servidor
        self.cliente.connect((host, port))

    # Método para recibir datos del servidor
    def recibir(self):
        receiving_file = False
        file_data = b''
        while True:
            try:
                # Recepción del mensaje del servidor
                mensaje = self.cliente.recv(1024)
                # Check for start of file transfer
                if mensaje.decode('utf-8') == FILE_TRANSFER_START:
                    receiving_file = True
                    file_data = b''
                    continue
                # Check for end of file transfer
                elif mensaje.decode('utf-8') == FILE_TRANSFER_END:
                    receiving_file = False
                    # TODO: Handle the received file data
                    # For now, we'll just write it to a file
                    with open('received_file', 'wb') as f:
                        f.write(file_data)
                    continue
                # If currently receiving a file, append the data
                elif receiving_file:
                    file_data += mensaje
                    continue
                else:
                    # Imprimir el mensaje
                    print(mensaje.decode('utf-8'))
            except:
                # Si hay un error, cerrar la conexión y salir del bucle
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
                self.cliente.send(FILE_TRANSFER_START.encode('utf-8'))
                self.enviar_archivo(nombre_archivo, self.cliente)
                self.cliente.send(FILE_TRANSFER_END.encode('utf-8'))

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
