from parameters import *

class Buffer:
    def __init__(self):
        self.buffer = {}
        self.capacity = serverMaxBufferSize
    
    def get_capacity(self):
        return self.capacity
    
    def add(self, idx:int, value:int):
        self.buffer[idx] = value
        self.capacity -= len(value)

    def remove(self, idx:int):
        self.capacity += len(self.buffer[idx])
        del self.buffer[idx]  


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

lock = threading.Lock()

while True:
    packet, address = connection.recv(buffer.get_capacity())
    seqNum, ack, rwnd, payload = unwrap_packet(packet)
    
    print( f"Número de seq. recebido: {seqNum}, o qual está associado ao seguinte conteúdo => {payload.decode()}"
    )
    print("# Capacidade do buffer: ", buffer.get_capacity())

    with lock:
        buffer.add(seqNum, payload)
        while expected_seq in buffer.buffer:
                print(f"Processou {expected_seq}")
                print("status do buffer: ", buffer.buffer)

                buffer.remove(expected_seq)
                expected_seq += 1

    # payload_to_send = f""
    # packet = create_packet(seqNum + 1, 1, buffer.get_capacity(), payload_to_send)
    # connection.send(packet, address)
