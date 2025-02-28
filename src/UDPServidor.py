import socket

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

msgFromServer       = "Oi UDP Cliente"
bytesToSend         = str.encode(msgFromServer)

# Cria socket datagram (UDP)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind entre endereco e IP
UDPServerSocket.bind((localIP, localPort))
 
print("Servidor UDP up e escutando...")

# Escutando datagramas que chegam
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    clientMsg = "Mensagem do Cliente:{}".format(message)
    clientIP  = "Endereco IP do Cliente:{}".format(address)
    
    print(clientMsg)
    print(clientIP)

    # Enviando msg de reply ao client
    UDPServerSocket.sendto(bytesToSend, address)