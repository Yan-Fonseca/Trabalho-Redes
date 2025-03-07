from parameters import *

class UDP_pacote:
    def __init__(self, msgFromClient, serverAddressPort, bufferSize, seqNum):
        self.msgFromClient = msgFromClient
        self.serverAddressPort = serverAddressPort
        self.bufferSize = bufferSize
        self.SeqNum = seqNum

    def UDPClientSocket(self):
        # Cria um socket UDP do lado cliente
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        return UDPClientSocket

    def bytesToSend(self):
        bytesToSend = str.encode(f"{self.SeqNum}:{self.msgFromClient}")
        return bytesToSend

    def sendto(self, UDPClientSocket, bytesToSend):
        # Envia msg ao servidor usando o socket UDP criado
        UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
        return UDPClientSocket

    def recvfrom(self, UDPClientSocket):
        msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)
        return msgFromServer

serverAddressPort   = (localIP, localPort)

seq_numbers = [i for i in range(ISN, ISN+10)]
random.shuffle(seq_numbers)

for seq in seq_numbers:

    msgFromClient       = "Este é o "+ str(seq) +"º pacote enviado"
    print("Mensagem enviada para o Servidor {}".format(msgFromClient) + " com sequência {}".format(seq))

    pacote = UDP_pacote(msgFromClient, serverAddressPort, bufferSize, seq)
    UDPClientSocket = pacote.UDPClientSocket()
    bytesToSend = pacote.bytesToSend()
    pacote.sendto(UDPClientSocket, bytesToSend)
    msgFromServer = pacote.recvfrom(UDPClientSocket)

    print("Mensagem vinda do Servidor {}".format(msgFromServer[0]))
