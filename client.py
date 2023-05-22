import os
import time
from socket import *
from functionalities import *
from datetime import datetime
from threading import Thread
from os import system

now = datetime.now()

HEADER = 16

#main server socket
host = '148.220.208.138'
port = 10000
address = (host, port)
mainsock = socket(AF_INET, SOCK_STREAM)

#listening channel info
myhost = '148.220.208.138'
myport = 10001
myaddress = (myhost, myport)
sock = socket(AF_INET, SOCK_STREAM)

#triger
triger = 0

#user info
myusername = ''

#client control
socketslist = []                     # contiene los sockets activos para ser leídos
contacts    = {'server': address}    # {'username' : ('ip', int(port))} 
activeUsers = {}                     # {sockets : ('ip', int(port))} -----> [idPeer] {sockets : 'username'}
activeUsers2= {}                     # [idPeer] {'username' : socket}
groups      = {}                     # {'group name' : ['member1', 'member2', 'member3', ...]}
keys        = {}                     # {'sockets' : b'public key'}

#requests control
requestSent = []

#crypto
public_key = ''
private_key = ''



def listeningChannel():
    sock.bind(myaddress)
    sock.listen(1)
    sock.setblocking(0)

    while True:
        try:
            client, clientadd = sock.accept()
            print(f"::::: {clientadd}> Conexión exitosa")

            socketslist.append(client)
            activeUsers[client] = clientadd
        except:
            pass

        if len(socketslist) > 0:
            for sockets in socketslist:
                message = recvmessages(sockets, HEADER)
                if message != 0:
                    try:
                        message = message.decode('utf-8')
                    except:
                        message = decryptMessage(private_key, message).decode('utf-8')

                    if message == 'recvKey':
                        if int(recvKey(sockets, keys, HEADER)):
                            sendKey(sockets, HEADER, public_key)
                        print(f'received from{activeUsers[sockets]}: ', keys[sockets])
                        sockets.setblocking(0)

                    elif message == 'loginResponse':
                        global myusername, triger
                        myusername, triger = loginResponse(sockets, keys, private_key, myhost, myport, HEADER)
                        sockets.setblocking(0)

                    elif message == 'confirmationUserCreation':
                        triger = userCreationResponse(sockets, private_key, HEADER)
                        sockets.setblocking(0)

                    elif message == 'requestConfirmation':
                        recvReqConfirmation(sockets, private_key, requestSent, HEADER)
                        sockets.setblocking(0)

                    elif message == 'recvRequest':
                        chatRequest(sockets, keys, private_key, HEADER)
                        sockets.setblocking(0)

                    elif message == 'recvRequestResponse':
                        if recvRequestResponse(sockets, private_key, requestSent, HEADER):
                            addContact(sockets, private_key, contacts, HEADER)
                        sockets.setblocking(0)

                    elif message == 'addContact':
                        addContact(sockets, private_key, contacts, HEADER)
                        sockets.setblocking(0)

                    elif message == 'joinedGroup':
                        recvGroupInfo(sockets, private_key, groups, contacts, activeUsers, myusername, HEADER)
                        sockets.setblocking(0)

                    elif message == 'groupMessage':
                        recvGroupMessage(sockets, activeUsers, private_key, HEADER)
                        sockets.setblocking(0)
                    
                    elif message == 'groupFile':
                        recvGroupFile(sockets, activeUsers, private_key, HEADER)
                        sockets(0)

                    elif message == 'idPeer':
                        idPeer(sockets, private_key, activeUsers, activeUsers2, HEADER)
                        sockets.setblocking(0)

                    elif message == 'recvFile':
                        recvFile(sockets, private_key, activeUsers, HEADER)
                        sockets.setblocking(0)

                    else:
                        date = now.strftime('%a %d %b, %Y')
                        time = now.strftime('%H:%M:%S')
                        print(generateColorText(f'[{date}]', bcolors.OKBLUE), end='')
                        print(generateColorText(f'[{time}]', bcolors.OKBLUE), end='')
                        print(generateColorText(f' {activeUsers[sockets]}>', bcolors.WARNING), end='')
                        print(f" {message}")


def mainChannel():
    global triger
    mainsock = initializeChat('server', public_key, activeUsers, activeUsers2, socketslist, contacts, HEADER)
    system("cls")
    while True:
        print(generateColorText(f'    [0] login\n    [1] create user', bcolors.HEADER))
        message = input(generateColorText(f'{myusername}> ', bcolors.HEADER))
        #login
        if message == '0':
            wait = login(mainsock, keys, HEADER)
            system("cls")
            if wait:
                #espera la respuesta del servidor
                while True:
                    print(generateColorText('#', bcolors.HEADER), end='')
                    time.sleep(0.02)
                    if triger:
                        triger = 0
                        break
                #comprueba si el login fue exitoso o no
                #para pasar a la siguiente pantalla
                if myusername != '':
                    break
            

        elif message == '1':
            wait = createUser(mainsock, keys, HEADER)
            system("cls")
            #espera la respuesta del servidor
            if wait:
                while True:
                    time.sleep(0.02)
                    print(generateColorText('#', bcolors.HEADER), end='')
                    if triger:
                        triger = 0
                        break

        time.sleep(1)
        system("cls")

    
    system("cls")
    for i in range(1, 15):
        print(generateColorText('#', bcolors.HEADER), end='')
        time.sleep(0.01)

    print(generateColorText(f"    Bienvenido {myusername}    ###############", bcolors.HEADER))
    print(generateColorText(f'\n\n  [MENÚ]', bcolors.HEADER))
    print(generateColorText(f'        # \'\chat\'       ---->   Abrir chat con alguien de tu lista de contactos.', bcolors.HEADER))
    print(generateColorText(f'        # \'\\request\'   ---->   Envíar una solicitud de chat.', bcolors.HEADER))
    print(generateColorText(f'        # \'\\group\'     ---->   Crea un grupo con tus amigos.', bcolors.HEADER))
    print(generateColorText(f'        # \'\\groupChat\' ---->   Abre el chat con un grupo.', bcolors.HEADER))
    print(generateColorText(f'        # \'\\logout\'    ---->   Cerrar sesión.', bcolors.HEADER))

    print(generateColorText(f'\n\n  [COMANDOS DE CHAT]', bcolors.HEADER))
    print(generateColorText(f'        # \'\chat\'       ---->   Abrir chat con otro contacto.', bcolors.HEADER))
    print(generateColorText(f'        # \'\\back\'      ---->   Volver', bcolors.HEADER))
    print(generateColorText(f'        # \'\\close\'     ---->   Cerrar chat', bcolors.HEADER))

    while True:
        message = input(generateColorText(f'{myusername}> ', bcolors.OKGREEN))

        if message == r'\request':
            requestUser(mainsock, keys, contacts, requestSent, HEADER)

        elif message == '\chat':
            openChat(contacts, activeUsers, activeUsers2, socketslist, public_key, keys, myusername, HEADER)

        elif message == '\group':
            createGroup(myusername, contacts, groups, socketslist, activeUsers, activeUsers2, public_key, keys, HEADER)
                    
        elif message == '\groupChat':
            openChatGroup(groups, myusername, socketslist, contacts, activeUsers, activeUsers2, public_key, keys, HEADER)

        elif message == '\logout':
            logout(socketslist, activeUsers, activeUsers2, keys, HEADER)

        else:
            sendencryptedmessage(mainsock, keys, message, HEADER)

if __name__ == '__main__':

    private_key, public_key = generateKeys()
    #print ('my key:', public_key)

    t1 = Thread(target=listeningChannel)
    t2 = Thread(target=mainChannel)

    t1.start()
    t2.start()

    t2.join()  # interpreter will wait until your process get completed or terminated
    os._exit(0)