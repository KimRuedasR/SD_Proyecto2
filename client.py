import socket
import threading

FIN = b'<FIN>'

class Cliente:
    def __init__(self, host="localhost", puerto=4000):
        self.apodo = input("Escoge un nickname: ")

        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))

        thread_recibir = threading.Thread(target=self.recibir)
        thread_escribir = threading.Thread(target=self.escribir)

        thread_recibir.start()
        thread_escribir.start()

    def recibir(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode('utf-8')
                if mensaje == 'Escribe tu nickname y presiona Enter':
                    self.cliente.send(self.apodo.encode('utf-8'))
                else:
                    print(mensaje)
            except:
                print("Error!")
                self.cliente.close()
                break

    def escribir(self):
        while True:
            mensaje = f'{self.apodo}: {input("")}'
            if mensaje.lower() == "salir":
                self.cliente.send('Se ha desconectado del servidor.'.encode('utf-8'))
                break
            elif mensaje.startswith("FILE:"):
                self.enviar_archivo(mensaje[5:], self.cliente)
            else:
                self.cliente.send(mensaje.encode('utf-8'))

    def enviar_archivo(self, nombre_archivo, socket):
        socket.sendall(f"FILE:{nombre_archivo}".encode('utf-8'))  # envía el nombre del archivo primero
        with open(nombre_archivo, 'rb') as f:
            while True:
                bytes_leidos = f.read(1024)
                if not bytes_leidos:
                    break
                socket.sendall(bytes_leidos)
            socket.sendall(FIN)

if __name__ == "__main__":
    Cliente()
