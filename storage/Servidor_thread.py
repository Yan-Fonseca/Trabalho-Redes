import threading
import time
from parameters_banhato import *

# Variável global para controlar a sequência esperada
expected_seq = isn

class Buffer:
    def __init__(self):
        self.buffer = []
        self.capacity = serverMaxBufferSize
    
    def get_capacity(self):
        return self.capacity
    
    def add(self, seq_num: int, value: str):
        self.buffer.append((seq_num, value))
        self.capacity -= len(value)

    def remove(self, seq_num: int):
        # Percorre a lista para encontrar o pacote com o número de sequência 'seq_num'
        for i, (s, payload) in enumerate(self.buffer):
            if s == seq_num:
                self.capacity += len(payload)
                del self.buffer[i]
                break

    def applyDiscardPolicy(self):
        # Drop head
        self.capacity += len(self.buffer[0][1])
        del self.buffer[0]

class UDPServer:
    def __init__(self, ip: str, porta: int):
        self.ip = ip
        self.porta = porta
        # Cria socket e faz o bind
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))
        print("Servidor UP!")

    def send(self, packet: bytes, address: tuple):
        self.UDPServerSocket.sendto(packet, address)

    def recv(self, currentBufferCapacity: int):
        msg, address = self.UDPServerSocket.recvfrom(currentBufferCapacity)
        return msg, address

def ack_sender(address, connection, current_capacity, seqNum):
    global expected_seq
    # Simula atraso no ACK independentemente do processamento do pacote
    if should_lose_packet(seqNum):
        time.sleep(1.1)  # atraso para simular perda/timeout
    expected_seq += 1
    payload_to_send = ""
    ack_packet = create_packet(expected_seq, 1, current_capacity, payload_to_send)
    connection.send(ack_packet, address)
    print(f"ACK enviado: próximo número de sequência {expected_seq} | Janela informada {current_capacity}")

connection = UDPServer(localIP, localPort)
buffer = Buffer()

while True:
    packet, address = connection.recv(buffer.get_capacity())
    seqNum, ack, rwnd, payload = unwrap_packet(packet)
    # Se há espaço no buffer
    if rwnd > 0:
        if seqNum == expected_seq:
            # Entrega imediata
            print(f"Entrega do pacote: {expected_seq} => {payload}")
            print(f"Número de sequência recebido: {seqNum}")

            if buffer.buffer:
                print("Status do buffer:", buffer.buffer)

        elif seqNum > expected_seq:
            # Pacote fora de ordem é armazenado para entrega futura
            print(f"Recebido pacote {seqNum} fora da ordem {expected_seq}. Armazenando-o em buffer.")
            buffer.add(seqNum, payload)
            print("Status do buffer:", buffer.buffer)
        else:
            print(f"Pacote {seqNum} duplicado ou já entregue.")
        

        t_ack = threading.Thread(target=ack_sender, args=(address, connection, buffer.get_capacity(), seqNum))
        t_ack.start()
        # Entrega acumulativa dos pacotes armazenados
        while any(item[0] == expected_seq for item in buffer.buffer):
            print(f"Entrega do pacote: {expected_seq}")
            buffer.remove(expected_seq)
            expected_seq += 1
    
    else:
        print("Buffer cheio. Aplicando política de descarte.")
        buffer.applyDiscardPolicy()
