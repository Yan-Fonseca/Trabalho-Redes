from parameters import *

# classe para gerenciar a conexão do cliente
class UDPClient:
    def __init__(self, ipDest: str, portaDest: int, ISN: int):
        self.ipDest = ipDest
        self.portaDest = portaDest

        self.seqNum = ISN # seqNum inicialmente é o ISN.
        self.rwnd = serverMaxBufferSize # inicialmente supõe-se buffer vazio.

        # abre uma conexão com IPv4 e usando UDP
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, packet: struct.pack):
        self.UDPClientSocket.sendto(packet, (self.ipDest, self.portaDest))

    def recv(self):
        msg, _ = self.UDPClientSocket.recvfrom(clientMaxBufferSize)
        return msg
    
    def start_connection(self):
        pass

    def end_connection(self):
        pass


if __name__ == "__main__":
    connection = UDPClient(localIP, localPort, isn)

    # 32 bits
    messages = ['11111111', '00000000', '11001100', '00110011']
    indexes = [3, 2, 1, 0]
    # random.shuffle(indexes)

    for index in indexes :
    
        payload = messages[index]
        print(payload)

        packet = create_packet(index, 0, connection.rwnd, payload)
        connection.send(packet)

        packet = connection.recv()
        seqNum, ack, rwnd, _ = unwrap_packet(packet)

        print("Número de sequência recebido: ", seqNum)
        connection.seqNum = seqNum # mando de onde recebi o ack...
