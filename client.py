# client.py
import socket
import threading
import os

class Cliente:
    def __init__(self, host = 'localhost', port = 5000):
        self.apodo = input("\nIngresa tu apodo: ")
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, port))

    def recibir(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode('utf-8')
                if mensaje == 'Nombre':
                    self.cliente.send(self.apodo.encode('utf-8'))
                else:
                    print(mensaje)
            except:
                print("Error")
                self.cliente.close()
                break

    def escribir(self):
        while True:
            print("\n1. Enviar mensaje")
            print("2. Enviar archivo")
            print("3. Recibir archivo")
            print("4. Salir")
            opcion = input("Elige una opción: ")

            if opcion == "1":
                mensaje = f'{self.apodo}: {input("Escribe tu mensaje: ")}'
                self.cliente.send(mensaje.encode('utf-8'))

            elif opcion == "2":
                nombre_archivo = input("\nIngresa el nombre del archivo a enviar: ")
                self.enviar_archivo(nombre_archivo, self.cliente)

            elif opcion == "3":
                nombre_archivo = input("\nIngresa el nombre del archivo a recibir: ")
                self.recibir_archivo(nombre_archivo, self.cliente)

            elif opcion == "4":
                print("\nSaliendo...")
                self.cliente.close()
                break

            else:
                print("\nOpción no reconocida. Intenta de nuevo.")

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