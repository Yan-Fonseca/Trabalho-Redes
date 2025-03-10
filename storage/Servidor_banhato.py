from parameters import *

class Buffer:
    def __init__(self):
        self.buffer = []
        self.capacity = serverMaxBufferSize
    
    def get_capacity(self):
        return self.capacity
    
    def add(self, idx:int, value:int):
        self.buffer.append((idx, value))
        self.capacity -= len(value)

    def remove(self, idx:int):
        self.capacity += len(self.buffer[idx])
        for tuple in self.buffer:
            if tuple[0] == idx:
                self.buffer.remove(tuple)
                break

    def applyDiscardPolicy(self):
        # drop head
        self.capacity += len(self.buffer[0][1])
        del self.buffer[0]


class UDPServer:
    def __init__(self, ip: str, porta: int):
        self.ip = ip
        self.porta = porta
        
        # cria socket e dá bind
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))
        print("Servidor UP!")

    def send(self, packet: struct.pack, address: tuple):
        self.UDPServerSocket.sendto(packet, address)

    def recv(self, currentBufferCapacity: int):
        msg, address = self.UDPServerSocket.recvfrom(currentBufferCapacity)
        return msg, address
    
# por simplicidade, assumiu-se isn. Mas, o servidor era para descobrir
# usando o 3 way-hanshake
expected_seq = isn

connection = UDPServer(localIP, localPort)
buffer = Buffer()

while True:
    packet, address = connection.recv(buffer.get_capacity())
    seqNum, ack, rwnd, payload = unwrap_packet(packet)
    
    if rwnd > 0:
        if seqNum == expected_seq:
            # entrega imediata
            print(f"Entrega do pacote: {expected_seq} => {payload}")
            expected_seq += 1

            # se buffer não estiver vazio
            if buffer.buffer:
                print("Status do buffer: ", buffer.buffer)

            # entrega acumulativa
            while any(item[0] == expected_seq for item in buffer.buffer):
                print(f"Entrega do pacote: {expected_seq}")
                buffer.remove(expected_seq)
                expected_seq += 1
        elif seqNum > expected_seq:
            # armazena no buffer para futura entrega
            print(f"Recebido pacote {seqNum} fora da ordem. Armazenando-o em buffer.")
            buffer.add(seqNum, payload)
            print("Status do buffer: ", buffer.buffer)
        else:
            print(f"Pacote {seqNum} duplicado ou já entregue.")
        
        # envia ack pedindo a partir de qual lugar ele deve continuar enviando
        payload_to_send = f""
        packet = create_packet(expected_seq, 1, buffer.get_capacity(), payload_to_send)
        connection.send(packet, address)
    
    else:
        print("Buffer cheio. Aplicando política de descarte.")
        buffer.applyDiscardPolicy()
