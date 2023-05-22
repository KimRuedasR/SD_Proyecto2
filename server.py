from socket import *
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP

keys = {}
public_key = ''
private_key = ''

def generateKeys ():
    key = RSA.generate(2048)
    private_key = key.export_key('PEM')
    public_key = key.publickey().exportKey('PEM')
    return private_key, public_key

def sendKey (sock):
    cipher = AES.new(b'1234567812345678', AES.MODE_CFB)
    message = cipher.encrypt(public_key)
    messageheader = f"{len(message):<{HEADER}}".encode('utf-8')
    sock.send(messageheader + message)
    messageheader = f"{len(cipher.iv):<{HEADER}}".encode('utf-8')
    sock.send(messageheader + cipher.iv)

def recvKey(sockets):
    try:
        sockets.setblocking(1)
        size = sockets.recv(HEADER).decode('utf-8') 
        message = sockets.recv(int(size))
        #print(message)
        size = sockets.recv(HEADER).decode('utf-8') 
        iv = sockets.recv(int(size))
        cipher = AES.new(b'1234567812345678', AES.MODE_CFB, iv)
        message = cipher.decrypt(message)
        #print(message)
        keys[sockets] = message
        sockets.setblocking(0)
        return 1
    except:
        sockets.setblocking(0)
        return 0

def encryptMessage (message, sock):
    rsa_public_key = RSA.importKey(keys[sock])
    rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
    encrypted_text = rsa_public_key.encrypt(message.encode('utf-8'))
    return encrypted_text

def decryptMessage (message):
    rsa_private_key = RSA.importKey(private_key)
    rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
    decrypted_text = rsa_private_key.decrypt(message)
    return decrypted_text

def recvmessage (sockets, HEADER):
    try:
        size = sockets.recv(HEADER).decode('utf-8') 
        message = sockets.recv(int(size))
        message = decryptMessage(message)
        return message.decode('utf-8')
    except:
        return 0

def sendmessage (message, sock):
    '''message = message.encode('utf-8')'''
    message = encryptMessage(message, sock)
    messageheader = f"{len(message):<{HEADER}}".encode('utf-8')
    sock.send(messageheader + message)

def login(sockets, HEADER):

    sockets.setblocking(1)

    response = 0

    username = recvmessage(sockets, HEADER)
    password = recvmessage(sockets, HEADER)

    try:
        data = users[username]
        if password == data:
            sendmessage('1', sockets)
            ip = recvmessage(sockets, HEADER)
            port = recvmessage(sockets, HEADER)
            response = 1
            

        else:
            sendmessage('0', sockets)
    except:
        sendmessage('0', sockets)

    if response:
        activeUsers[username] = [ip, int(port)]
        oldData = clients[sockets]
        print(f"{oldData} ----> {username}")
        clients[sockets] = username



def createUser (sockets):

    sockets.setblocking(1)

    username = recvmessage(sockets, HEADER)
    password = recvmessage(sockets, HEADER)
    try:
        data = users[username]
        sendmessage('0', sockets)
    except:
        users[username] = password
        sendmessage('1', sockets)

def requestAddress (sockets):

    sockets.setblocking(1)

    username = recvmessage(sockets, HEADER)
    
    try:
        data = activeUsers[username]

    except:
        sendmessage('0', sockets)
        return 0
    
    ip = data[0]
    host = data[1]
    origin = clients[sockets]

    print(f'Solicitante: {origin}')
    print(f'Conexión solicitada: {ip, host}')

    requestedSckt = socket(AF_INET, SOCK_STREAM)
    requestedAdd = (ip, host)

    requestedSckt.connect(requestedAdd)
    sendKey(requestedSckt)
    recvKey(requestedSckt)
    sendmessage('requestAdd', requestedSckt)
    sendmessage(origin, requestedSckt)

    sendmessage('1', sockets)

    requestedSckt.close()

def getResponse(sockets):

    sockets.setblocking(1)

    response = recvmessage(sockets, HEADER)

    if int(response):
        host = recvmessage(sockets, HEADER)
        port = recvmessage(sockets, HEADER)
        origin = recvmessage(sockets, HEADER)

        for clave, valor in clients.items():
            if valor == origin:
                origin = clave
                break
        
        sendmessage(str(response), origin)
        sendmessage(host, origin)
        sendmessage(str(port), origin)
        sendmessage(clients[origin], origin)

        return 1
        
    else:
        origin =recvmessage(sockets, HEADER)
        for clave, valor in clients.iteritems():
            if valor == origin:
                origin = clave
                break

        sendmessage(str(response), origin)
        return 0
        





def disconectClient(sockets):
    socketslist.remove(sockets)
    sockets.close()
    username = clients[sockets]
    print(f'{username}> conexión finalizada')
    del(clients[sockets])
    del(activeUsers[username])



HEADER = 10

host = '127.0.0.1'
port = 10000
socketslist = []
server = (host, port)
sock = socket(AF_INET, SOCK_STREAM)
clients = {}
users = {'user1':'12345', 'user2':'12345'}
activeUsers = {}

count = 0

sock.bind(server)
private_key, public_key = generateKeys()
sock.setblocking(0)


print('Esperando...')

sock.listen(5)

while True:
    try: 
        client, clientadd = sock.accept()
        recvKey(client)
        sendKey(client)
        print(f'Conexión exitosa {clientadd}')
        socketslist.append(client)
        clients[client] = clientadd
    except:
        pass

    if len(socketslist) != 0:
        for sockets in socketslist:

            message = recvmessage(sockets, HEADER)

            if message != 0:
                if message == 'login':
                    login(sockets, HEADER)
                    sockets.setblocking(0)

                elif message == 'create user':
                    createUser(sockets)
                    sockets.setblocking(0)

                elif message == 'request':
                    requestAddress(sockets)
                    sockets.setblocking(0)

                elif message == 'responseRequest':
                    getResponse(sockets)
                    sockets.setblocking(0)

                elif message == 'disconect':
                    disconectClient(sockets)

                else:
                    print(f'{clients[sockets]}> {message}')


            '''if message == 'disconect':
                socketslist.remove(sockets)
                sockets.close()
                print(f'{clients[sockets]}> conexión finalizada')
                del(clients[sockets])

            elif message == 'login':
                size = sockets.recv(HEADER).decode('utf-8')
                username = sockets.recv(int(size)).decode('utf-8')

                size = sockets.recv(HEADER).decode('utf-8')
                password = sockets.recv(int(size)).decode('utf-8')'''


    

