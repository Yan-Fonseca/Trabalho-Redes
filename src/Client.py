from parameters import *

class UDPClient:
    def __init__(self, ipDest, portDest, ISN):
        self.ipDest = ipDest # ip de destino
        self.portDest = portDest #porta de destino
        self.ISN = ISN #número de sequência inicial
        
        # AF_INET: ipv4
        # SOCK_DGRAM: udp
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
    def start_connection():
        pass # 3 way-handshake

    def end_connection():
        pass # 3 way-handshake finalize
    
    def sendto(self, packet):
        # envia o pacote
        self.UDPClientSocket.sendto(packet, (self.ipDest, self.portDest))

    def recvfrom(self):
        # recebe o pacote do servidor
        msgFromServer, _ = self.UDPClientSocket.revfrom(bufferSize)
        return msgFromServer

generated_numbers = set()
ISN = 2000

seq_numbers = [i for i in range(ISN, ISN+10)]
random.shuffle(seq_numbers)

udpClient = UDPClient(localIP, localPort, ISN)

messages = [f"{i}" for i in range(0, 10)]

for i in range(ISN, ISN+10):
    payload = messages[i].encode()
    
    # seq_num, ack, length, rwnd, payload
    packet = struct.pack("!I I I I", seq_numbers[i], 0, len(payload), 0) + payload
    udpClient.sendto(packet)

    msg = udpClient.recvfrom()

    print(f"{msg}")




    