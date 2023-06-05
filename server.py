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

    def broadcast(self, mensaje, prefix=""):  # prefix es para nombre identificacion.
        for client in self.clientes:
            client.send(bytes(prefix, "utf8")+mensaje)

    def aceptar_clientes(self):
        print("El servidor está aceptando conexiones...")
        while True:
            client, addr = self.server.accept()
            print(f"\nConexión establecida con {addr}.")

            client.send(bytes("Escribe tu nickname y presiona Enter", "utf8"))
            apodo = client.recv(1024).decode("utf8")
            self.clientes[client] = apodo

            print(f"\nNickname del cliente es {apodo}!")
            broadcast(bytes(f"\n{apodo} se ha unido al chat!", "utf8"))
            client.send(bytes("Te has unido al chat!", "utf8"))

            atender_cliente = threading.Thread(target=self.manejar, args=(client,))
            atender_cliente.start()

    def procesar_mensajes(self):
        print("El servidor está procesando mensajes...")
        while True:
            if len(self.clientes) > 0:
                for client in self.clientes:
                    mensaje = client.recv(1024).decode("utf8")
                    self.broadcast(mensaje)

    def manejar(self, cliente):
        try:
            apodo = self.clientes[cliente]
        except KeyError:
            print("Cliente desconocido.")
            return

        recibiendo_archivo = False
        nombre_archivo = None
        archivo = None
        while True:
            try:
                mensaje = cliente.recv(1024)
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
                        self.broadcast(mensaje, apodo+": ")

            except:
                if archivo:  # asegúrese de cerrar el archivo si se abrió
                    archivo.close()
                del self.clientes[cliente]
                cliente.close()
                self.broadcast(f"\n**{apodo} dejó el chat".encode('utf-8'))
                break

if __name__ == "__main__":
    Servidor()
