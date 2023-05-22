import os
import time
from socket import *
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from datetime import datetime

now = datetime.now()


###########--------------- GENERALES --------------###########################

def generateKeys ():
    #Genera y retorna las claves pública y privada (bytes)
    key = RSA.generate(2048)
    private_key = key.export_key('PEM')
    public_key = key.publickey().exportKey('PEM')
    return private_key, public_key

def encryptKey(public_key):
    #encripta public_key a través de cifrado simétrico
    #retorna la key cifrada, la key simétrica y el iv
    symetric_key = Random.get_random_bytes(16)
    cipher = AES.new(symetric_key, AES.MODE_CFB)
    encrypted_key = cipher.encrypt(public_key)
    iv = cipher.iv
    return encrypted_key, symetric_key, iv

def decryptKey(symetric_key, iv, encrypted_key):
    #desencripta public key a través de descifrado simétrico
    #retorna la key descifrada
    cipher = AES.new(symetric_key, AES.MODE_CFB, iv)
    decrypted_key = cipher.decrypt(encrypted_key)
    return decrypted_key

def encryptMessage (sock: socket, keys, message):
    #dado un mensaje lo encripta
    #keys: [dict] aloja las public_keys de cada usuario
    #socket: fungirá como selector para keys
    #retorna el mensaje encriptado [bytes]
    rsa_public_key = RSA.importKey(keys[sock])
    rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
    encrypted_text = rsa_public_key.encrypt(message.encode('utf-8'))
    return encrypted_text

def encryptBytes (sock: socket, keys, content):
    #dado un mensaje lo encripta
    #keys: [dict] aloja las public_keys de cada usuario
    #socket: fungirá como selector para keys
    #retorna el mensaje encriptado [bytes]
    rsa_public_key = RSA.importKey(keys[sock])
    rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
    encrypted_text = rsa_public_key.encrypt(content)
    return encrypted_text

def decryptMessage (private_key, message):
    #dado un mensaje lo desencripta
    #private_key: clave privada para desencriptado
    #retorna el mensaje desencriptado [bytes]
    rsa_private_key = RSA.importKey(private_key)
    rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
    decrypted_text = rsa_private_key.decrypt(message)
    return decrypted_text

def sendKey (sock: socket, HEADER, public_key, flag='0'):
    #Encripta y envía la clave pública al servidor especificado
    #sock: socket destino
    #flag indica al receptor está esperando una respuesta (envío de clave)
    encrypted_key, symetric_key, iv = encryptKey(public_key) #Método de encriptado de public_key
    sendmessage(sock, 'recvKey', HEADER)
    sendmessage(sock, flag, HEADER)
    sendbytes(sock, symetric_key, HEADER)
    sendbytes(sock, iv, HEADER)
    sendbytes(sock, encrypted_key, HEADER)

def recvKey (sock: socket, keys, HEADER):
    #recibe, desencripta y registra en el diccionario 'keys' la clave pública
    sock.setblocking(1) 
    flag            = recvmessages(sock, HEADER)    #flag que nos indica si el emisor espera respuesta de nuesta parte (0, 1)
    symetric_key    = recvmessages(sock, HEADER)    #clave simétrica para desencriptado
    iv              = recvmessages(sock, HEADER)    #iv del cipher 
    encrypted_key   = recvmessages(sock, HEADER)                    #recibe
    decrypted_key   = decryptKey(symetric_key, iv, encrypted_key)   #desencripta
    keys[sock] = decrypted_key  #registra
    #print('received: ', decrypted_key)
    return flag     #retorna la flag recibida para que se proceda o no con la respuesta.

def sendmessage (sock: socket, message, HEADER):
    #Dado un socket y un string se encarga enviar el string al socket especificado
    #message: mensaje a enviar
    #sock: socket destino
    messageheader = f"{len(message):<{HEADER}}".encode('utf-8') #tamaño del mensaje a enviar [bytes][b'len(message)     ']
    message = message.encode('utf-8')                           #parseo de mensaje [str -> bytes]
    sock.send(messageheader + message)                          #envío de tamaño de mensaje seguido del mensaje


def recvmessages (sock: socket, HEADER):
    #Dado un socket, recibe algún mensaje procedente de este y lo retorna.
    #sock: socket emisor
    try:
        size = sock.recv(HEADER) #tamaño del mensaje a recibir 
        message = sock.recv(int(size)) #mensaje recibido
        return message                 #retorna el mensaje [bytes] 
    except:
        return 0

def sendbytes (sock: socket, message, HEADER):
    #Dado un socket y un string se encarga enviar el string al socket especificado
    #message: mensaje a enviar
    #sock: socket destino
    messageheader = f"{len(message):<{HEADER}}".encode('utf-8')     #tamaño del mensaje a enviar
    try:
        sock.send(messageheader + message)                              #envío de tamaño de mensaje seguido del mensaje
    except:
        print(generateColorText(f'[WARNING]: Usuario no disponible', bcolors.WARNING))
    
def sendencryptedmessage(sock: socket, keys, message, HEADER):
    #dado un mensaje lo encripta y posteriormente lo envía 
    #sock: destino
    #keys: [dict] almacena las keys
    encrypted_message = encryptMessage(sock, keys, message) #metodo de encriptado
    sendbytes(sock, encrypted_message, HEADER)              #metodo de envío

def sendencryptedBytes(sock: socket, keys, content, HEADER):
    #dado un mensaje lo encripta y posteriormente lo envía 
    #sock: destino
    #keys: [dict] almacena las keys
    encrypted_bytes = encryptBytes(sock, keys, content) #metodo de encriptado
    sendbytes(sock, encrypted_bytes, HEADER)            #metodo de envío

def recvencryptedmessage(sock: socket, private_key, HEADER):
    #dado un socket recibe y desencripta algún mensaje proveniente de él
    #sock: origen
    #keys: [dict] almacena las keys
    #retorna el mensaje desencriptado
    message = recvmessages(sock, HEADER)
    decrypted_message = decryptMessage(private_key, message)    #metodo de desencriptado
    decrypted_message = decrypted_message.decode('utf-8')       #parseo de mensaje desencriptado [bytes -> str]
    return decrypted_message    #retorna el mensaje desencriptado

def recvencryptedBytes(sock: socket, private_key, HEADER):
    #dado un socket recibe y desencripta algún mensaje proveniente de él
    #sock: origen
    #keys: [dict] almacena las keys
    #retorna el mensaje desencriptado
    message = recvmessages(sock, HEADER)
    decrypted_message = decryptMessage(private_key, message)    #metodo de desencriptado

    return decrypted_message    #retorna el mensaje desencriptado

def showContacts (contacts):
    contactlist = contacts.keys()
    if len(contactlist) == 1:
        print(generateColorText(f'[WARNING]: Lista de usuarios vacía. Prueba el comando \\request para agregar usuarios.', bcolors.WARNING))
        return 0

    print(generateColorText(f'        [CONTACTOS]', bcolors.HEADER))
    for contact in contactlist:
        if contact != 'server':
            print(generateColorText(f'        [{contact}]', bcolors.HEADER))
    return 1

#############      FOR CLIENT      ##############
#CLIENT SIDE:

def login (mainsock: socket, keys, HEADER):
    #petición de login ante el servidor
    #mainsock: socket principal
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    username = input(generateColorText(f'Ingrese su nombre de usuario: \n>', bcolors.HEADER))
    if username == '\\back':
        return 0
    password = input(generateColorText(f'Ingrese su contraseña: \n>', bcolors.HEADER))
    if password == '\\back':
        return 0
    #envío de datos al servidor
    sendencryptedmessage(mainsock, keys, 'loginRequest', HEADER)    #flag que indica al servidor la operación que se está realizando
    sendencryptedmessage(mainsock, keys, username, HEADER)          #username
    sendencryptedmessage(mainsock, keys, password, HEADER)          #contraseña
    return 1

def createUser (mainsock: socket, keys, HEADER):
    #petición de creación un usuario en el servidor 
    #mainsock:      servidor
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    username = input(generateColorText(f'Cree su nombre de usuario: \n>', bcolors.HEADER))
    if username == '\\back':
        return 0
    password = input(generateColorText(f'Cree su contraseña: \n>', bcolors.HEADER))
    if password == '\\back':
        return 0
    password_conf = input(generateColorText(f'Confirme su contraseña: \n>', bcolors.HEADER))
    if password_conf == '\\back':
        return 0
    
    if password == password_conf: #valida que la contraseña y la confirmación sean idénticas
        #envío de datos al servidor para validación para creación de usuarios
        sendencryptedmessage(mainsock, keys, 'createUser', HEADER)  #flag que indica al servidor la operación que se está realizando
        sendencryptedmessage(mainsock, keys, username, HEADER)      #username
        sendencryptedmessage(mainsock, keys, password, HEADER)      #contraseña
        return 1
    else:
        print(generateColorText(f'[ERROR]: Las contraseñas no coinciden', bcolors.FAIL))
        return 0

def requestUser(mainsock: socket, keys, contacts, requestSent, HEADER):
    #petición de requestchat
    #mainsock:      servidor
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    #contacts:      diccionario de contactos {'username' : ('host', int(port))}
    #requestSent:   ['username 1', 'username 2'] contiene las solicitudes que están a la espera de respuesta
    username = input(generateColorText(f'Con quién deseas chatear? \n >', bcolors.HEADER))  #username del usuario solicitado 
    if username == '\\back':
        return 0
    if username in requestSent: #valida que no se envíen solicitudes duplicadas a un mismo destino
        print(generateColorText(f'[WARNING]: Ya has enviado una solicitud a este usuario antes. Espera su respuesta.', bcolors.WARNING))
    else:
        try:
            contact_address = contacts[username] #valida que el usuario no exista en tu lista de contactos. Si no existe, genera exception 
            print(generateColorText(f'[CONFIRMED]: El usuario {contact_address} ya está en tu lista de contactos, prueba el comando \chat para abrir el chat con él', bcolors.OKGREEN))
            return 0    #fin
        except:
            #envío de datos al servidor
            sendencryptedmessage(mainsock, keys, 'requestUser', HEADER)     #flag que indica al servidor la operación que se está realizando
            sendencryptedmessage(mainsock, keys, username, HEADER)          #username de quién estamos solicitando la información de conexión
            requestSent.append(username)                                    #registramos que hemos envíado una solicitud a dicho usuario
            return 1

def idMe(sock:socket, keys, myusername, HEADER):
    #Envía los datos para que el cliente peer identifique a qué usuario pertenece la conexión
    sendencryptedmessage(sock, keys, 'idPeer', HEADER)      #flag que indica la operación
    sendencryptedmessage(sock, keys, myusername, HEADER)    #nombre de usuario de a quién pertenece la conexión

def broadcastGroupInfo(myusername, groups, groupname, contacts, activeUsers, activeUsers2, socketslist, public_key, keys, HEADER):
    members = groups[groupname]
    for destiny in members:
        try:
            sock = activeUsers2[destiny]
        except KeyError:
            sock = initializeChat(destiny, public_key, activeUsers, activeUsers2, socketslist, contacts, HEADER, keys, myusername)
        sendencryptedmessage(sock, keys, 'joinedGroup', HEADER)
        sendencryptedmessage(sock, keys, groupname, HEADER)
        sendencryptedmessage(sock, keys, myusername, HEADER)

        for member in members:
            if member != activeUsers[sock]:
                sendencryptedmessage(sock, keys, member, HEADER)
        sendencryptedmessage(sock, keys, 'done', HEADER)

def createGroup (myusername, contacts, groups, socketslist, activeUsers, activeUsers2, public_key, keys, HEADER):
    members = []
    print(generateColorText(f'Ingrese un nuevo nombre para crear el grupo:', bcolors.HEADER))
    groupname = input(generateColorText(f'> ', bcolors.HEADER))
    response = showContacts(contacts)
    if not response:
        return 0
    print(generateColorText(f'Ingrese el comando \'\done\' para indicar que no hay más miembros para el grupo', bcolors.HEADER))
    while True:
        member = input(generateColorText(f'Ingrese un nuevo miembro para crear el grupo.\n>', bcolors.HEADER))
        if member != '\done':
            try:
                data = contacts[member]
            except:
                print(generateColorText(f'[WARNING]: El usuario no se encuentra en tu lista de contactos. Prueba mandarle una request para poder agregarlo.', bcolors.WARNING))
                continue
            print(generateColorText(f'[CONFIRMED]: El usuario {member} ha sido agregado al grupo.', bcolors.OKGREEN))
            members.append(member)
        else:
            break
    groups[groupname] = members
    broadcastGroupInfo(myusername, groups, groupname, contacts, activeUsers, activeUsers2, socketslist, public_key, keys, HEADER)
    members.append('me')
    groups[groupname] = members
    print(generateColorText(f'[NOTIFICATION]: Grupo {groupname} creado con éxito.', bcolors.OKCYAN))

def openChatGroup(groups, myusername, socketslist, contacts, activeUsers, activeUsers2, public_key, keys, HEADER):
    grouplist = groups.keys()
    print(generateColorText(f'[GROUPLIST]', bcolors.HEADER))
    if len(grouplist) > 0:
        for group in grouplist:
            members = groups[group]
            print(generateColorText(f'***************************************', bcolors.FAIL))
            print(generateColorText(f'[{group}]', bcolors.HEADER))
            for member in members:
                print(generateColorText(f'     -{member}', bcolors.HEADER))
        while True:
            selectedgroup = input(generateColorText(f'Selecciona el grupo en el que deseas chatear \n>', bcolors.HEADER))
            if selectedgroup != r'\back':
                try:
                    members = groups[selectedgroup]
                except KeyError:
                    print(generateColorText(f'[ERROR]: El grupo que con el que deseas chatear no existe en tu lista de grupos', bcolors.FAIL))
                    continue
            else:
                return 0
            break

        print(generateColorText(f'[NOTIFICATION]: Chat inicializado con el usuario: {selectedgroup}', bcolors.OKCYAN))
        while True:
            message = input(generateColorText(f'{myusername}>', bcolors.OKGREEN))
            if message == '\close':
                return 0
            elif message == '\sendfile':
                filepath = input(generateColorText(f'ingrese la ruta del archivo: ', bcolors.HEADER))
                for member in members:
                    try:
                        contacts[member]
                    except KeyError:
                        continue

                    try:
                        sock = activeUsers2[member]
                    except KeyError:
                        initializeChat(member, public_key, activeUsers, activeUsers2, socketslist, contacts, HEADER, keys, myusername)

                    sendencryptedmessage(sock, keys, 'groupFile', HEADER)
                    sendencryptedmessage(sock, keys, selectedgroup, HEADER)
                    sendFile(sock, keys, message, HEADER, filepath)
                print(generateColorText(f'[CONFIRMED]: Archivo enviado con éxito', bcolors.OKGREEN))

            else:
                for member in members:
                    try:
                        contacts[member]
                    except KeyError:
                        continue

                    try:
                        sock = activeUsers2[member]
                    except KeyError:
                        initializeChat(member, public_key, activeUsers, activeUsers2, socketslist, contacts, HEADER, keys, myusername)

                    sendencryptedmessage(sock, keys, 'groupMessage', HEADER)
                    sendencryptedmessage(sock, keys, selectedgroup, HEADER)
                    sendencryptedmessage(sock, keys, message, HEADER)

    else:
        print(generateColorText(f'[WARNING]: Tu lista de grupos está vacía, prueba el comando \group para crear uno.', bcolors.WARNING))

    
def initializeChat(username, public_key, activeUsers, activeUsers2, socketslist, contacts, HEADER, keys='', myusername=''):
    #Crea la conexión con el usuario indicado
    #username:      usuario con quien se desea contactar
    #activeUser:    {sockets : ('ip', int(port))}
    #activeUser2:   {'username' : socket}
    #contacts:      {'username' : ('ip', int(port))} 
    #socketslist:   list de sockets para ser leídos
    #keys:          {socket : b'public key'}
    #retorna objeto socket o 0
    try:
        data = contacts[username]   #valida si el usuario existe en la lista de contactos. Si no, genera exception
    except:
        print(generateColorText(f'[WARNING]: El usuario no se encuentra en tu lista de contactos. Prueba mandarle una request para poder agregarlo.', bcolors.WARNING))
        return 0
    # data = ('ip', int(port))
    sock = socket(AF_INET, SOCK_STREAM) #creación de socket 
    sock.connect(data)                  #conexión            

    activeUsers[sock]  = username   #registo de usuario  
    activeUsers2[username] = sock   #registo de socket

    sendKey(sock, HEADER, public_key, flag='1') #envío de clave pública con espera de respuesta

    socketslist.append(sock)        #registra un nuevo socket en la lista de escucha

    time.sleep(1)                   #espera de 1 segundo para terminar de recibir la respuesta del sendkey()

    if username != 'server':                    #en caso de que la conexión no sea hacia el server
        idMe(sock, keys, myusername, HEADER)    #nos identificamos con el cliente hacia el que hicimos la conexión  

    return sock #retorna el socket 

def sendFile (sock, keys, HEADER, filepath = 0):
    #encripta y envia un archivo seleccionado hacia un el usuario con el qu ese está chateando 
    #sock:          destino
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    givenfilepath = filepath
    if not filepath:
        filepath = input(generateColorText(f'ingrese la ruta del archivo: ', bcolors.HEADER))

    filepathsplited = os.path.splitext(filepath)            #['ruta', '.extensión de archivo']
    file_ext = filepathsplited[1]                           # '.extensión de archivo'
    sendencryptedmessage(sock, keys, 'recvFile', HEADER)    #envío de flag que le indica la destino que va a recibir un archivo   
    sendencryptedmessage(sock, keys, file_ext, HEADER)      #envío de la extensión (tipo) de archivo que se está enviando
    with open(filepath, 'rb') as f:
        content = f.read(200)                               #lectura del primer bloque de bytes del archivo a enviar 
        while content:
            sendencryptedBytes(sock, keys, content, HEADER) #envío de bloque de bytes encriptados
            content = f.read(200)                           #lectura del sigiente bloque de bytes del archivo a enviar 
        sendencryptedmessage(sock, keys, 'done', HEADER)
    if not givenfilepath:
        print(generateColorText(f'[CONFIRMED]: Archivo enviado con éxito', bcolors.OKGREEN))


def logout (socketslist: list,  activeUsers, activeUsers2, keys, HEADER):
    #socketlist:    lista de sockets para ser leídos en el canal de escucha
    #activeUsers:   diccionario de usuarios con los que se tieen una conexión activa {'socket': 'username'}
    #activeUsers2:  diccionario de usuarios con los que se tieen una conexión activa {'username': 'socket'}
    #keys:          diccionario de claves públicas {socket: b'public_key'}

    for sockets in socketslist:
        sendencryptedmessage(sockets, keys, 'logout', HEADER)
        username = activeUsers[sockets]
        del activeUsers[sockets]
        del activeUsers2[username]
        del keys[sockets]
        sockets.close()

def openChat(contacts, activeUsers, activeUsers2, socketslist, public_key, keys, myusername, HEADER):
    #evalúa si existe la manera de chatear con un usuario indicado por el usuario 
    #contacts:      diccionario de contactos {'username' : ('host', int(port))}
    #activeUsers:   diccionario de usuarios con los que se tieen una conexión activa {'socket': 'username'}
    #activeUsers2:  diccionario de usuarios con los que se tieen una conexión activa {'username': 'socket'}
    #socketlist:    lista de sockets para ser leídos en el canal de escucha
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    #public_keys:   clave public key para encriptado

    while True:

        response = showContacts(contacts)

        if not response:
            return 0
        
        username = input(generateColorText(f'Con quién deseas chatear? \n>', bcolors.HEADER))
        try:
            sock = activeUsers2[username]   #valida si ya existe una conexión con el usuario, si no genera exception
        except:
            #crea la conexión si el usuario está en tu diccionario de contactos, si no retorna 0
            sock = initializeChat(username, public_key, activeUsers, activeUsers2, socketslist, contacts, HEADER, keys, myusername)
            time.sleep(1)   #espera para ser identificado por el usuario a quién nos conectamos
        if sock == 0:
            return 0
        else:
            #loop de chat 
            print(generateColorText(f'[NOTIFICATION]: Chat inicializado con el usuario: {username}', bcolors.OKCYAN))
            while True:
                message = input(generateColorText(f'{myusername}> ', bcolors.OKGREEN))
                if message != '\\close':
                    if message == '\\sendfile':
                        sendFile(sock, keys, HEADER)    #método de envío de archivos
                    elif message == r'\chat':
                        break
                            
                    else:
                        sendencryptedmessage(sock, keys, message, HEADER)   #envía mensaje ingresado
                else:
                    print(generateColorText(f'[NOTIFICATION]: Chat cerrado con el usuario: {username}', bcolors.OKCYAN))
                    return 0


        
#SERVER SIDE

def loginResponse (mainsock: socket, keys, private_key, myip, myport, HEADER):
    #recibe la respuesta del servidor a una solicitud de login enviada previamente 
    #mainsock:      servidor
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    #private_key:   clave privada para desencriptar mensajes recibidos    
    #retorna el username con el que está logeado ante el server

    mainsock.setblocking(1)

    response = recvencryptedmessage(mainsock, private_key, HEADER)      #Recibe la respuesta a la validación de datos de inicio de sesión (0, 1)

    if int(response):   #datos de inicio de sesión correctos
        username = recvencryptedmessage(mainsock, private_key, HEADER)  #Recibe el username con el que está logeó
        sendencryptedmessage(mainsock, keys, 'login', HEADER)           #envío de flag que le indica al servidor la operación que va a realizar
        sendencryptedmessage(mainsock, keys, myip, HEADER)              #envía la ip     del canal de escucha para que el server la registre y pueda proporcionarla a quién la solicite en el futuro para establecer conexiones.
        sendencryptedmessage(mainsock, keys, str(myport), HEADER)       #envía el puerto del canal de escucha para que el server la registre y pueda proporcionarla a quién la solicite en el futuro para establecer conexiones.
        sendencryptedmessage(mainsock, keys, username, HEADER)          #envía el username con el que quedará registrada la información anterior

        return username, 1  #retorno de username con el que esamos logeados ante el servidor.
    else:               #datos de inicio de sesión incorrectos           
        #negación
        print(generateColorText(f'\n   [ERROR]: DATOS DE INICIO DE SESIÓN INCORRECTOS', bcolors.FAIL))
        return '', 1



def userCreationResponse (mainsock: socket, private_key, HEADER):
    #recibe la respuesta del servidor a la operación de createUser 
    #mainsock:      servidor
    #private_key:   clave privada para desencriptar mensajes recibidos 
    
    mainsock.setblocking(1)
    confirmation = recvencryptedmessage(mainsock, private_key, HEADER)  #recibe la respuesta del servidor

    #notificación en consola
    if int(confirmation):
        print(generateColorText(f'\n   [CONFIRMED]: Usuario creado con éxito', bcolors.OKGREEN))
        return 1
    else:
        print(generateColorText(f'\n   [ERROR]: El username elegido no está disponible', bcolors.FAIL))
        return 1



def recvReqConfirmation(mainsock: socket, private_key, requestSent, HEADER):
    #recibe la confirmación por parte del servidor de una chat request
    #mainsock:      servidor
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #requestSent:   ['username 1', 'username 2'] contiene las solicitudes que están a la espera de respuesta

    mainsock.setblocking(1)

    username = recvencryptedmessage(mainsock, private_key, HEADER)          #recibe el username del destino de la request realizada
    confirmation = recvencryptedmessage(mainsock, private_key, HEADER)      #recibe la confirmación de la request enviada de esta (0, 1)
    
    #notificación en consola
    if int(confirmation):
        print (generateColorText(f'[CONFIRMED]: Solicitud enviada al usuario {username}.', bcolors.OKGREEN))
    else:
        print (generateColorText(f'[ERROR]: El usuario {username} no existe o se encuentra desconectado.', bcolors.FAIL))
        requestSent.remove(username)    #elimina la solicitud de la lista de solicitudes realizadas


def chatRequest (mainsock:socket, keys, private_key, HEADER):
    #recibe una chat request y solicita la respuesta 
    #mainsock:      servidor
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    #private_key:   clave privada para desencriptar mensajes recibidos 

    mainsock.setblocking(1)

    username = recvencryptedmessage(mainsock, private_key, HEADER)  #recibe el username del creador de la solicitud
    print(generateColorText(f'[NOTIFICATION]: El usuario {username} quiere chatear contigo.', bcolors.OKCYAN))         #notifica que llegó la solicitud
    response = input(generateColorText(f'Aceptar [1] | Rechazar [0] \n> ', bcolors.OKCYAN))                            #solicita la respuesta a la solicitud

    sendencryptedmessage(mainsock, keys, 'responseRequest', HEADER) #envío de flag que le indica al servidor que se enviará la respuesta a una chat request
    sendencryptedmessage(mainsock, keys, response, HEADER)          #envío de la respuesta
    sendencryptedmessage(mainsock, keys, username, HEADER)          #envío del username a quién va dirigida la respuesta

def recvRequestResponse (mainsock: socket, private_key, requestSent, HEADER):
    #recibe la respuesta a una chat request enviada anteriormente
    #mainsock:      servidor
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #requestSent:   ['username 1', 'username 2'] contiene las solicitudes que están a la espera de respuesta
    mainsock.setblocking(1)
    username = recvencryptedmessage(mainsock, private_key, HEADER)  #recibe el username que corresponde la solicitud
    response = recvencryptedmessage(mainsock, private_key, HEADER)  #recibe la respuesta a la solicitud (0, 1)
    if int(response):
        print(generateColorText(f'[CONFIRMED]: El usuario {username} aceptó tu solicitud de chat.', bcolors.OKGREEN))
        requestSent.remove(username)     #elimina la solicitud de la lista de solicitudes realizadas
        return 1
    else:
        print(generateColorText(f'[DENIED]: El usuario {username} rechazó tu solicitud de chat.', bcolors.FAIL))
        requestSent.remove(username)     #elimina la solicitud de la lista de solicitudes realizadas
        return 0


def addContact (mainsock: socket, private_key, contacts, HEADER):
    #recibe los datos de conexión para el registro de un usuario en la lista de contactos
    #mainsock:      servidor
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #contacts:      diccionario de contactos {'username' : ('host', int(port))}
    mainsock.setblocking(1)
    username = recvencryptedmessage(mainsock, private_key, HEADER)  #recepción del username del usuario a registrar
    host = recvencryptedmessage(mainsock, private_key, HEADER)      #recepción del ip del canal de escucha corresponiente al usuario a registrar
    port = recvencryptedmessage(mainsock, private_key, HEADER)      #recepción del puerto del canal de escucha corresponiente al usuario a registrar

    contacts[username] = (host, int(port))  #regisro de datos de conexión 

    print(generateColorText(f'''[CONFIRMED]: El usuario {username} ha sido agregado a tu lista de contactos.
    Ahora pueden comenzar a chatear''', bcolors.OKGREEN))     #notificación

def idPeer (sock: socket, private_key, activeUsers, activeUsers2, HEADER):
    #una vez realizada la conexión con algún usuario se identifica 
    #socket:        socket que se está identificando a sí mismo
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #activeUsers:   diccionario de usuarios con los que se tieen una conexión activa {'socket': 'username'}
    #activeUsers2:  diccionario de usuarios con los que se tieen una conexión activa {'username': 'socket'}

    sock.setblocking(1)
    username = recvencryptedmessage(sock, private_key, HEADER)
    oldData = activeUsers[sock]
    activeUsers [sock] = username
    activeUsers2[username] = sock
    print(generateColorText(f'[ID]: {oldData} ----> {username}', bcolors.OKCYAN))

def recvFile (sock: socket, private_key, activeUsers, HEADER, groupname = 0):
    sock.setblocking(1)
    file_ext = recvencryptedmessage(sock, private_key, HEADER)
    origin = activeUsers[sock]
    formatdate = now.strftime('%d.%m.%Y_%H.%M.%S')
    filepath = f'C:\\Users\\Isaac\\Downloads\\receivedfiles\\{origin}{formatdate}{file_ext}'

    with open(filepath, 'w+b') as f:
        content = recvencryptedBytes(sock, private_key, HEADER)
        while content != b'done':
            f.write(content)
            content = recvencryptedBytes(sock, private_key, HEADER)
    if not groupname:
        date = now.strftime("%a %d %b, %Y")
        print(generateColorText(f'[{date}] ', bcolors.OKBLUE), end='')
        print(generateColorText(f'{origin}>', bcolors.WARNING), end='')
        print(f' envío un archivo: ', end='')
        print(f'{filepath}')
    else:
        date = now.strftime("%a %d %b, %Y")
        print(generateColorText(f'[{date}] ', bcolors.OKBLUE), end='')
        print(generateColorText(f'[{groupname}] ', bcolors.OKGREEN), end='')
        print(generateColorText(f'{origin}>', bcolors.WARNING), end='')
        print(f' envío un archivo: ', end='')
        print(f'{filepath}')

def recvGroupInfo(sock: socket, private_key, groups, contacts, activeUsers, myusername, HEADER):
    members = []
    unknownusers = 0
    admin = activeUsers[sock]
    sock.setblocking(1)
    groupname = recvencryptedmessage(sock, private_key, HEADER)
    member = recvencryptedmessage(sock, private_key, HEADER)
    while member != 'done':
        try:
            contacts[member]
        except KeyError:
            unknownusers = 1
        if member != myusername:
            members.append(member)
        member = recvencryptedmessage(sock, private_key, HEADER)
    members.append('me')
    groups[groupname] = members
    print(generateColorText(f'[NOTIFICATION]: El usuario {admin} te agregó al grupo {groupname}', bcolors.OKCYAN))
    if unknownusers:
        print(generateColorText(f'[WARNING]: En el grupo {groupname} hay miembros quienes no están en tu lista de contactos. Prueba agregarlos con el comando \\request para poder ver los mensajes que envíen al grupo y que puedan ver los tuyos.', bcolors.WARNING))

def recvGroupMessage(sock: socket, activeUsers, private_key, HEADER):
    sock.setblocking(1)
    date = now.strftime('%a %d %b, %Y')
    time = now.strftime('%H:%M:%S')
    origin = activeUsers[sock]
    groupname = recvencryptedmessage(sock, private_key, HEADER)
    message = recvencryptedmessage(sock, private_key, HEADER)
    print(generateColorText(f'[{date}]', bcolors.OKBLUE), end='')
    print(generateColorText(f'[{time}]', bcolors.OKBLUE), end='')
    print(generateColorText(f'[{groupname}]', bcolors.OKGREEN), end='')
    print(generateColorText(f' {origin}> ', bcolors.WARNING), end='')
    print(message)

def recvGroupFile(sock: socket, private_key, activeUsers, HEADER):
    sock.setblocking(1)
    groupname = recvencryptedmessage(sock, private_key, HEADER)
    recvFile(sock, private_key, activeUsers, HEADER, groupname)


def logoutpeer(sockets: socket, activeUsers, activeUsers2, keys):
    #sock:          socket que está cerrando sesión
    #activeUsers:   diccionario de usuarios con los que se tieen una conexión activa {'socket': 'username'}
    #activeUsers2:  diccionario de usuarios con los que se tieen una conexión activa {'username': 'socket'}
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    username = activeUsers[sockets]
    del activeUsers[sockets]
    del activeUsers2[username]
    del keys[sockets]
    print (generateColorText(f'[NOTIFICATION]: El usuario {username} de ha desconectado.', bcolors.WARNING))

#############      FOR SERVER      ##############

def loginRequest (sock: socket, private_key, users, keys, HEADER):
    #recibe y valida los datos de inicio de sesión enviados mediante el método login por el cliente
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #users:         diccionario de datos de inicio de sesión de los usuarios registrados {'username' : 'password'}
    #keys:          diccionario de claves públicas {socket: b'public_key'}

    sock.setblocking(1)

    #recepción de datos de inicio de sesión
    username = recvencryptedmessage(sock, private_key, HEADER)  #nombre de usuario 
    print('received username: ', username)
    password = recvencryptedmessage(sock, private_key, HEADER)  #contraseña
    print('received pass: ', password)

    try:
        data = users[username] #valida que el usuario exista en los registros almacenando la contraseña en la variable data, de lo contrario lanza exception
    except:
        #envío de datos
        sendencryptedmessage(sock, keys, 'loginResponse', HEADER)   #flag que indica al cliente que recibirá la respuesta a su solicitud de inicio de sesión
        sendencryptedmessage(sock, keys, '0', HEADER)               #respuesta negativa
        return 0    #fin

    if password == data: #en caso de que exista el usuario, se valida que la contraseña se correspondiente 
        #envío de datos
        sendencryptedmessage(sock, keys, 'loginResponse', HEADER)   #flag que indica al cliente que recibirá la respuesta a su solicitud de inicio de sesión
        sendencryptedmessage(sock, keys, '1', HEADER)               #envío de respuesta positiva   
        sendencryptedmessage(sock, keys, username, HEADER)          #envío del username que el cliente va a almacenar en su variable global myusername       
        return 1                                                    

    else:
        sendencryptedmessage(sock, keys, 'loginResponse', HEADER)
        sendencryptedmessage(sock, keys, '0', HEADER)               #envío de respuesta negativa
        return 0

def loginUser (sock: socket, private_key, activeUsers, clients, clients2, HEADER):
    #una vez que se validan los datos de inicio de sesión correctamente [login request],
    #recibe los datos de conexión del usuario logeado para registrarlos. 
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #activeUsers:   diccionario de usuarios con los que se tieen una conexión activa {'socket': 'username'}
    #clients:       diccionario de sockets conectados {socket : (ip, int(port))}
    #clients2:      diccionario de usuarios logeados {'username' : 'socket'}
    #socketlist:    lista de sockets para ser leídos en el canal de escucha

    sock.setblocking(1)

    ip = recvencryptedmessage(sock, private_key, HEADER)        #recibe ip del usuario logeado   
    print('ip recibida: ', ip)
    port = recvencryptedmessage(sock, private_key, HEADER)      #recibe el puerto del canal de eschucha del usuario logueado    
    print('puerto recibido: ', port)
    username = recvencryptedmessage(sock, private_key, HEADER)  #recibe el username del usuario logeado
    print('username recibido: ', username)

    activeUsers[username] = (ip, port)      #registro de información de conexión
    oldData = clients[sock]                 #extración de data 
    print(f"{oldData} ----> {username}")    #notificación de actualizacón de data (identificación de conexión) en consola
    clients[sock] = username                #actualización del diccionario clients {socket : (ip, int(port))} -------> [login] {socket: 'username'}
    clients2[username] = sock               #registro nuevo en clients 2

def registerUser (sock: socket, private_key, keys, users, HEADER):
    #creación/registro de nuevo usuario
    #sock:          quién envía la petición de registro
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    #users:         diccionario de datos de inicio de sesión de los usuarios registrados {'username' : 'password'}

    sock.setblocking(1)

    username = recvencryptedmessage(sock, private_key, HEADER)  #recibe el username a registrar
    password = recvencryptedmessage(sock, private_key, HEADER)  #recibe la contraseña a registrar

    sendencryptedmessage(sock, keys, 'confirmationUserCreation', HEADER)    #envío de flag que indica al cliente la recepción de la repuesta a su petición de regisro

    try:
        data = users[username]  #valida que el username esté disponible, si no genera una exception
        sendencryptedmessage(sock, keys, '0', HEADER)   #envío de respuesta negativa
    except:
        users[username] = password  #registro de nuevo usuario 
        sendencryptedmessage(sock, keys, '1', HEADER)   #envío de repuesta positiva

def recvRequest(sock: socket, private_key, clients, clients2, keys, HEADER):
    #recibe las solicitudes de chat, las valida y las direcciona hacia los usuarios solicitados
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #clients:       diccionario de sockets conectados {socket : (ip, int(port))}
    #clients2:      diccionario de usuarios logeados {'username' : 'socket'}
    #keys:          diccionario de claves públicas {socket: b'public_key'}

    sock.setblocking(1)

    username = recvencryptedmessage(sock, private_key, HEADER) #'username' del usuario solicitado
    applicant = clients[sock]                                  #'username' del usuario solicitante
    try:
        requestedUser = clients2[username] #valida que el usuario solicitado exita, guardando su socket en la variable o regresa una exception si este no existe
        #envío de datos al usuario solicitado
        sendencryptedmessage(requestedUser, keys, 'recvRequest', HEADER) #flag notifica que tiene una solicitud entrante
        sendencryptedmessage(requestedUser, keys, applicant, HEADER)     #envío del username del usuario solicitante
        #envío de datos al usuario solicitante
        sendencryptedmessage(sock, keys, 'requestConfirmation', HEADER)  #flag que notifica que recibirá la situación de su solicitud
        sendencryptedmessage(sock, keys, username, HEADER)               #envío del username del usuario solicitado
        sendencryptedmessage(sock, keys, '1', HEADER)                    #confirmación positiva
    except:
        sendencryptedmessage(sock, keys, 'requestConfirmation', HEADER)  #flag que notifica que recibirá la situación de su solicitud
        sendencryptedmessage(sock, keys, username, HEADER)               #envío del username del usuario solicitado
        sendencryptedmessage(sock, keys, '0', HEADER)                    #confirmación positiva

def sendConnectionData (sock: socket, username, activeUsers, keys, HEADER):
    #comparte los datos de conexión de un usuario especificado
    #username:      es el usuario de quien se van a compartir los datos (host y port)
    #sock:          es quien va a recibir los datos
    #activeUsers:   diccionario que contiene la información del canal de escucha 
    #               de los clientes conectados {socket : ('ip', 'port')}
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    data = activeUsers[username] #(host, port)
    print(data)
    host = data[0] 
    port = data[1]
    #envío de datos
    sendencryptedmessage(sock, keys, username, HEADER)  #username del usuario de quién provienen los datos
    sendencryptedmessage(sock, keys, host, HEADER)      #host/ip del usuario (username)
    sendencryptedmessage(sock, keys, port, HEADER)      #puerto del usuario (username)


def responseChatRequest (sockets: socket, keys, private_key, clients, clients2, activeUsers, HEADER):
    #recibe la repuesta a una solicitud de chat. 
    #notifica al usuario que hizo la solicitud sobre la respuesta 
    #en caso que sea positivo, el servidor envía los dato necesarios para que se establezca la conexión 
    #entre ambas partes. (host, port)
    #sockets:       socket que responde a la solicitad
    #keys:          diccionario de claves públicas {socket: b'public_key'}
    #private_key:   clave privada para desencriptar mensajes recibidos 
    #clients:       diccionario de sockets conectados {socket : (ip, int(port))}
    #clients2:      diccionario de usuarios logeados {'username' : 'socket'}
    #activeUsers:   diccionario que contiene la información del canal de escucha 
    #               de los clientes conectados {socket : ('ip', 'port')}
    sockets.setblocking(1)

    response = recvencryptedmessage(sockets, private_key, HEADER) #respuesta a solicitud de chat
    username = recvencryptedmessage(sockets, private_key, HEADER) #'username' para quién va dirigida la respuesta

    origin = clients[sockets]       #'username' de quién emite la respuesta
    destiny = clients2[username]    #socket de quién va a recibir la respuesta

    #envío de contexto al usurio que realizó la solicitud originalmente
    sendencryptedmessage(destiny, keys, 'recvRequestResponse', HEADER) #bandera para avisar para avisar que se recibirá la respuesta a una solicitud realizada previamente
    sendencryptedmessage(destiny, keys, origin, HEADER)                #usuario a quién se le envió dicha solicitud

    if int(response):
        #envío de datos a la parte emisora de la solicitud original
        sendencryptedmessage(destiny, keys, response, HEADER)           # respuesta a la solicitud
        sendConnectionData(destiny, origin, activeUsers, keys, HEADER)  # envío de datos

        #envío de datos a la parte emisora de la respuesta
        sendencryptedmessage(sockets, keys, 'addContact', HEADER)        #bandera para invocar el método que guarda la data del usuario a quién se le aceptó la solicitud
        sendConnectionData(sockets, username, activeUsers, keys, HEADER) # envío de datos 

def logoutclient(sockets: socket, clients, clients2, activeUsers):
    #sockets:       socket que responde a la solicitad
    #clients:       diccionario de sockets conectados {socket : (ip, int(port))}
    #clients2:      diccionario de usuarios logeados {'username' : 'socket'}
    #activeUsers:   diccionario de usuarios con los que se tieen una conexión activa {'socket': 'username'}
    username = activeUsers[sockets]
    del clients[sockets]
    del clients2[username]
    del activeUsers[sockets]
    print (f':::::{username} se ha desconectado.')

###################-------------UI------------------#######################


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BOLD = '\033[2m'
    UNDERLINE = '\033[4m'

def generateColorText(text, color:bcolors):
    return f'{color}{text}{bcolors.ENDC}'