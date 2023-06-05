import socket
import threading

FIN = b'<FIN>'

class Cliente:
    def __init__(self, host="localhost", puerto=4000):
        self.nickname = input("Elige un nickname: ")

        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((host, puerto))

        thread_recibir = threading.Thread(target=self.recibir)
        thread_enviar = threading.Thread(target=self.enviar)

        thread_recibir.start()
        thread_enviar.start()

    def recibir(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode('utf8')
                if mensaje == 'Ingresa tu nickname y presiona enter':
                    self.cliente.send(self.nickname.encode('utf8'))
                else:
                    print(mensaje)
            except:
                print("Ha ocurrido un error!")
                self.cliente.close()
                break

    def enviar(self):
        while True:
            mensaje = f'{self.nickname}: {input("")}'
            if mensaje.lower() == "salir":
                self.cliente.send('Se ha desconectado del servidor.'.encode('utf8'))
                break
            elif mensaje.startswith("FILE:"):
                self.enviar_archivo(mensaje[5:], self.cliente)
            else:
                self.cliente.send(mensaje.encode('utf8'))

    def enviar_archivo(self, nombre_archivo, socket):
        # Añadido para manejar el envío de archivos
        # Envía el nombre del archivo primero
        socket.sendall(f"FILE:{nombre_archivo}".encode('utf8')) 
        with open(nombre_archivo, 'rb') as f:
            while True:
                bytes_leidos = f.read(1024)
                if not bytes_leidos:
                    break
                socket.sendall(bytes_leidos)
            socket.sendall(FIN)

if __name__ == "__main__":
    Cliente()
