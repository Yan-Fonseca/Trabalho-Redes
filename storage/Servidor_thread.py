import threading
import time
import socket
from parameters_banhato import *

# Variável global para controlar a sequência esperada
expected_seq = isn
seq_lock = threading.Lock()  # Lock para atualizações de expected_seq

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

def ack_sender(address, connection, current_capacity, ack_num):
    # Envia o ACK com o ack_num recebido sem modificar o expected_seq
    # if should_lose_packet(ack_num):
    #     time.sleep(3)  # atraso para simular perda/timeout
    payload_to_send = ""
    ack_packet = create_packet(ack_num, 1, current_capacity, payload_to_send)
    connection.send(ack_packet, address)
    print(f"ACK enviado: próximo número de sequência {ack_num} | Janela informada {current_capacity}")

def delayed_update():
    global expected_seq
    # Atrasa a atualização para simular perda/timeout
    print("Simulando atraso na atualização do expected_seq...")
    time.sleep(0.5)  # atraso (só funciona para valores mais baixos ou igual a 0.5)
    with seq_lock:
        expected_seq += 1
        print(f"expected_seq atualizado para {expected_seq} após atraso.")
        # Verifica se há pacotes armazenados para entrega acumulativa
        while any(item[0] == expected_seq for item in buffer.buffer):
            print(f"Entrega do pacote (buffer): {expected_seq}")
            buffer.remove(expected_seq)
            expected_seq += 1

connection = UDPServer(localIP, localPort)
buffer = Buffer()

while True:
    packet, address = connection.recv(buffer.get_capacity())
    seqNum, ack, rwnd, payload = unwrap_packet(packet)
    print(payload)

    # Se há espaço no buffer
    if rwnd > 0:
        # Pacote esperado (in order)
        if seqNum == expected_seq:
            print(f"Entrega do pacote: {expected_seq} => {payload}")
            print(f"Número de sequência recebido: {seqNum}")
            # Decide se a atualização será adiada
            # if should_lose_packet(expected_seq):
            #     # Envia o ACK com o valor atual e atrasa a atualização
            #     t_delay = threading.Thread(target=delayed_update)
            #     t_delay.start()
            # else:
            with seq_lock:
                expected_seq += 1
                print(f"expected_seq atualizado para {expected_seq}.")
                # Entrega acumulativa dos pacotes armazenados em buffer
                while any(item[0] == expected_seq for item in buffer.buffer):
                    print(f"Entrega do pacote (buffer): {expected_seq}")
                    buffer.remove(expected_seq)
                    expected_seq += 1

            # Envia ACK cumulativo com o (possivelmente ainda antigo) valor de expected_seq
            t_ack = threading.Thread(target=ack_sender, args=(address, connection, buffer.get_capacity(), expected_seq))
            t_ack.start()

        # Pacote fora de ordem: armazena e envia ACK com o mesmo número esperado
        elif seqNum > expected_seq:
            print(f"Recebido pacote {seqNum} com payload {payload} fora da ordem {expected_seq}. Armazenando-o em buffer.")
            buffer.add(seqNum, payload)
            print("Status do buffer:", buffer.buffer)
            t_ack = threading.Thread(target=ack_sender, args=(address, connection, buffer.get_capacity(), expected_seq))
            t_ack.start()
        else:
            # Pacote duplicado ou já entregue; não envia ACK desnecessário
            print(f"Pacote {seqNum} duplicado ou já entregue.")
    
    else:
        print("Buffer cheio. Aplicando política de descarte.")
        buffer.applyDiscardPolicy()