import socket
import threading
import os

class Cliente:
    def __init__(self, host = '127.0.0.1', port = 5000):
        self.apodo = input("Ingresa tu apodo: ")
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, port))

    def recibir(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode('utf-8')
                if mensaje == 'NICK':
                    self.cliente.send(self.apodo.encode('utf-8'))
                else:
                    print(mensaje)
            except:
                print("¡Ocurrió un error!")
                self.cliente.close()
                break

    def escribir(self):
        while True:
            print("\nElige una opción: ")
            print("1. Chat")
            print("2. Enviar archivo")
            print("3. Recibir archivo")
            opcion = input()

            if opcion == "1":
                while True:
                    mensaje = input("Enviar mensaje: ")
                    if mensaje.lower() == 'salir':
                        break
                    mensaje_completo = f'\n@{self.apodo}: {mensaje}'
                    print(mensaje_completo)
                    self.cliente.send(mensaje_completo.encode('utf-8'))

            elif opcion == "2":
                nombre_archivo = input("\n--Ingresa el nombre del archivo a enviar: ")
                self.enviar_archivo(nombre_archivo, self.cliente)

            elif opcion == "3":
                nombre_archivo = input("\n--Ingresa el nombre del archivo a recibir: ")
                self.recibir_archivo(nombre_archivo, self.cliente)

            else:
                print("\nOpción incorrecta. Intenta de nuevo.")

    def enviar_archivo(self, nombre_archivo, socket):
        with open(nombre_archivo, 'rb') as f:
            while True:
                bytes_leidos = f.read(4096)
                if not bytes_leidos:
                    break
                socket.sendall(bytes_leidos)

    def recibir_archivo(self, nombre_archivo, socket):
        with open(nombre_archivo, 'wb') as f:
            while True:
                datos = socket.recv(4096)
                if not datos:
                    break
                f.write(datos)

    def iniciar(self):
        hilo_recibir = threading.Thread(target=self.recibir)
        hilo_recibir.start()

        hilo_escribir = threading.Thread(target=self.escribir)
        hilo_escribir.start()

cliente = Cliente()
cliente.iniciar()
