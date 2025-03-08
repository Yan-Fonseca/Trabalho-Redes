from parameters import *

# classe para gerenciar a conexão do cliente
class UDPClient:
    def __init__(self, ipDest: str, portaDest: int, ISN: int):
        self.ipDest = ipDest
        self.portaDest = portaDest

        self.seqNum = ISN # seqNum inicialmente é o ISN. (por enquanto só guarda ISN)
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
    message = '11111111000000001100110000110011'
    aux = ''

    index = connection.seqNum
    count = 0
    while len(aux) != len(message):
    
        payload_send = chunk_message(message, index, chunk_size)
        print(payload_send)

        packet = create_packet(count, 0, connection.rwnd, payload_send)
        connection.send(packet)

        packet = connection.recv()
        seqNum, ack, rwnd, _ = unwrap_packet(packet)

        print("Número de sequência recebido: ", seqNum)
        
        connection.rwnd = rwnd # atualizo o rwnd

        index += chunk_size # atualizo o index
        aux += payload_send
        count += 1

        if rwnd == 0:
            # buffer está lotado, e capacidade zerou
            # diminuir velocidade de transmissão
            chunk_size /= 2
            # pensar depois em como restaurar a velocidade...

