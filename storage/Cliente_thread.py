import threading
import time
import socket
from parameters_banhato import *

# Variáveis compartilhadas
cwnd = 1
sstresh = 5
ultimo_ack = None
num_duplicados = 0
finished = False  # Indica quando toda a mensagem foi enviada
aux_global = ""   # Armazena os dados enviados

packets_enviados = {}
lock = threading.Lock()

class UDPClient:
    def __init__(self, ipDest: str, portaDest: int, ISN: int):
        self.ipDest = ipDest
        self.portaDest = portaDest
        self.seqNum = ISN  # seqNum inicialmente é o ISN
        self.rwnd = serverMaxBufferSize  # inicialmente supõe-se buffer vazio
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, packet: bytes):
        self.UDPClientSocket.sendto(packet, (self.ipDest, self.portaDest))

    def recv(self):
        msg, _ = self.UDPClientSocket.recvfrom(clientMaxBufferSize)
        return msg

# Função da thread de envio
def thread_envio(connection: UDPClient, message: str):
    global cwnd, finished, aux_global
    index = 0
    count = 0
    while len(aux_global) < len(message):
        with lock:
            if connection.rwnd == 0:
                print("Rwnd zero. Aguardando atualização...")
                continue

            # Define o tamanho do chunk que pode ser enviado
            chunk_cabivel = min(connection.rwnd, int(cwnd))
            chunk_cabivel = min(chunk_cabivel, mss)
            # Obtém o pedaço da mensagem a ser enviado
            payload_send = chunk_message(message, index, chunk_cabivel)
            print(f"Enviando pacote {count} | Payload: '{payload_send}' | Tamanho: {len(payload_send)}")
            packet = create_packet(count, 0, connection.rwnd, payload_send)
            packets_enviados[count] = (packet, time.time(), payload_send)
            connection.send(packet)
            # Atualiza os índices e a variável global com os dados enviados
            index += chunk_cabivel
            aux_global += payload_send
            count += 1

        time.sleep(0.1)  # Pequeno delay para simular envio contínuo

    with lock:
        finished = True
    print("Envio completo. Encerrando thread de envio.")

# Função da thread de recebimento com verificação de conclusão do envio
def thread_recebimento(connection: UDPClient, message: str):
    global cwnd, sstresh, ultimo_ack, num_duplicados, finished, aux_global
    last_ack_time = time.time()
    while True:
        # Se toda a mensagem foi enviada e a variável aux_global está completa, encerra a thread
        if finished and len(aux_global) >= len(message):
            print("Todos os pacotes enviados e ACKs processados. Encerrando thread de recebimento.")
            break
        try:
            connection.UDPClientSocket.settimeout(2)
            packet = connection.recv()
            last_ack_time = time.time()  # Atualiza a última vez que recebeu um ACK
        except socket.timeout:
            if finished and len(aux_global) >= len(message):
                continue
            else:
                print("Timeout no recebimento de ACK.")
                continue
        finally:
            connection.UDPClientSocket.settimeout(None)
        seqNum, ack, rwnd, _ = unwrap_packet(packet)
        with lock:
            print(f"ACK recebido: próximo número de sequência {seqNum} | Janela informada {rwnd}")
            connection.rwnd = rwnd
            if ultimo_ack is not None and ultimo_ack == seqNum:
                num_duplicados += 1
                print(f"ACK duplicado! num: {num_duplicados}")
                if num_duplicados == 3:
                    print("Três ACK duplicados!")
                    sstresh = max(cwnd // 2, 1)
                    cwnd = 1
                    num_duplicados = 0
            else:
                num_duplicados = 0
            ultimo_ack = seqNum
            # Ajuste simples do cwnd
            if cwnd < sstresh:
                cwnd += 1
                print(f"Slow Start: novo cwnd {cwnd}")
            else:
                cwnd += 1 / cwnd
                print(f"Congestion Avoidance: novo cwnd {int(cwnd)}")
            # Opcional: remover pacotes confirmados do dicionário packets_enviados
    print("Envio concluído. Encerrando thread de recebimento.")

if __name__ == "__main__":
    connection = UDPClient(localIP, localPort, isn)
    message = '11111111000000001100110000110011'
    print(f"Mensagem: {message} | Tamanho: {len(message)}")

    t_envio = threading.Thread(target=thread_envio, args=(connection, message))
    t_recebimento = threading.Thread(target=thread_recebimento, args=(connection, message))

    t_envio.start()
    t_recebimento.start()

    t_envio.join()
    t_recebimento.join()
    print("Processo encerrado.")
