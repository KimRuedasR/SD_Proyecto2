import socket
import threading

FIN = b'<FIN>'

class Servidor:
    def __init__(self, host="localhost", puerto=4000):
        self.clientes = {}
        self.topics = {"general": []}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, puerto))
        self.server.listen()
        self.server.setblocking(False)

        aceptar = threading.Thread(target=self.aceptar_clientes)
        procesar = threading.Thread(target=self.procesar_mensajes)

        aceptar.start()
        procesar.start()

    def dinfundir(self, mensaje, prefix=""):  # prefix es para nombre identificacion.
        for client in self.clientes:
            client.send(bytes(prefix, "utf8")+mensaje)

    def aceptar_clientes(self):
        while True:
            client, addr = self.server.accept()
            print("{addr} se ha conectado")
            self.dinfundir(f"{addr} se ha unido al chat!".encode("utf8"))

            client.send("Ingresa tu nickname y presiona enter".encode("utf8"))
            apodo = client.recv(1024).decode("utf8")
            self.clientes[client] = apodo

            print(f"Nickname de {addr} es {apodo}!")
            self.dinfundir(f"{apodo} se ha unido al chat!".encode("utf8"))
            client.send("Conectado al chat!".encode("utf8"))

            thread = threading.Thread(target=self.manejar_cliente, args=(client,))
            thread.start()

    def procesar_mensajes(self):
        print("Procesando mensajes...")
        while True:
            if len(self.clientes) > 0:
                for client in self.clientes:
                    mensaje = client.recv(1024)
                    self.dinfundir(mensaje)

    def manejar_cliente(self, client):
        apodo = self.clientes[client]

        recibiendo_archivo = False
        nombre_archivo = None
        archivo = None
        while True:
            try:
                mensaje = client.recv(1024)
                if recibiendo_archivo:
                    if mensaje[-5:] == FIN:
                        archivo.write(mensaje[:-5])  # escribe la última parte del archivo
                        archivo.close()
                        archivo = None
                        recibiendo_archivo = False
                        nombre_archivo = None
                    else:
                        archivo.write(mensaje)
                else:
                    if mensaje.decode('utf-8').startswith("FILE:"):
                        nombre_archivo = mensaje.decode('utf-8')[5:]  # obtiene el nombre del archivo
                        archivo = open(nombre_archivo, 'wb')
                        recibiendo_archivo = True
                    else:
                        self.dinfundir(mensaje, apodo+": ")

            except:
                if archivo:  # asegúrese de cerrar el archivo si se abrió
                    archivo.close()
                del self.clientes[client]
                self.dinfundir(f"{apodo} ha dejado el chat".encode("utf-8"))
                client.close()
                break

if __name__ == "__main__":
    Servidor()
