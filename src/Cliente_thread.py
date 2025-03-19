import threading
import time
import socket
from parameters import *
import csv
import base64
import random
import os

# Constante de timeout (em segundos)
TIMEOUT_THRESHOLD = 2

# Variáveis compartilhadas
cwnd = mss
sstresh = 4 * mss
ultimo_ack = None
num_duplicados = 0
finished = False  # Indica quando toda a mensagem foi enviada
aux_global = ""   # Armazena os dados enviados

packets_send = []
packets_enviados = {}
lock = threading.Lock()
# Dicionário para controlar os pacotes pendentes (ainda sem ACK)
packets_pending = {}

# Lock exclusivo para escrita no CSV
csv_lock = threading.Lock()
path_csv_file = os.path.join("storage", "packets_log.csv")
CSV_FILENAME = path_csv_file

def init_csv_log(filename):
    """Inicializa o arquivo CSV escrevendo o cabeçalho."""
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["seq_number", "t0", "tf", "tam"])

def log_packet_info(*args):
    if len(args) == 1:
        packet = args[0]
        log_msg = f"LOG: {packet.seq_number}"
    elif len(args) == 3:
        source, event, packet = args
        log_msg = f"LOG: {packet.seq_number} | Source: {source}, Event: {event}"
    else:
        raise ValueError("Número inválido de argumentos para log_packet_info")
    
    # Exibe o log para depuração
    print(f"\n{log_msg}\n")
    
    with csv_lock:
        with open(CSV_FILENAME, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([packet.seq_number, packet.t0, packet.tf, packet.tam])


class PacketData:
    def __init__(self, seq_number, t0, tam):
        self.seq_number = seq_number
        self.t0 = t0
        self.tf = None
        self.tam = tam
        self.ack = False
    
    def update(self, tf):
        self.tf = tf
    
    def get_seq_number(self):
        return self.seq_number
    
    def __repr__(self):
        return f'{self.seq_number} : t0 = {self.t0}, tf = {self.tf}, tam = {self.tam}, ack = {self.ack}\n'

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
    global cwnd, finished, aux_global, packets_pending
    index = 0
    count = 0
    while len(aux_global) < len(message):
        with lock:
            if connection.rwnd == 0:
                print("Rwnd zero. Aguardando atualização...")
                continue

            # Define o tamanho do chunk que pode ser enviado
            chunk_cabivel = min(connection.rwnd, int(cwnd))
            payload_send = chunk_message(message, index, chunk_cabivel)
            packet = create_packet(count, 0, connection.rwnd, payload_send)
            packets_enviados[count] = (packet, time.time(), payload_send)

            t0 = time.time_ns()
            pkt_data = PacketData(count, t0, len(payload_send))
            if random.random() >= 0.05:
                print(f"Enviando pacote {count} | Payload: '{payload_send}' | Tamanho: {len(payload_send)}")
                connection.send(packet)
            else:
                print("Pacote perdido!")
            
            # Adiciona o pacote na lista de pendentes e registra no CSV
            packets_pending[count] = pkt_data
            #log_packet_info("envio", "enviado", pkt_data)

            index += chunk_cabivel
            aux_global += payload_send
            count += 1

        time.sleep(0.001)  # Pequeno delay para simular envio contínuo

    print("Envio completo. Encerrando thread de envio.")

def verify_end(packets_pending):
    # Verifica se não há pacotes pendentes (todos receberam ACK)
    return len(packets_pending) == 0

# Função da thread de recebimento com tratamento de timeout no socket
def thread_recebimento(connection: UDPClient, message: str):
    global cwnd, sstresh, ultimo_ack, num_duplicados, finished, aux_global, packets_pending
    while True:
        if len(aux_global) >= len(message):
            finished = verify_end(packets_pending)

        if finished:
            print("Todos os pacotes enviados e ACKs processados. Encerrando thread de recebimento.")
            break

        if num_duplicados >= 3 and ultimo_ack is not None:
            print("ACKs duplicados no último pacote. Reenviando o último pacote.")
            chunk_cabivel = min(connection.rwnd, int(cwnd))
            payload_send = chunk_message(message, ultimo_ack, chunk_cabivel)
            packet = create_packet(ultimo_ack, 0, connection.rwnd, payload_send)
            connection.send(packet)
        try:
            connection.UDPClientSocket.settimeout(TIMEOUT_THRESHOLD)
            packet = connection.recv()
        except socket.timeout:
            print("Timeout no recebimento de ACK.")
            with lock:
                if ultimo_ack is not None:
                    sstresh = max(cwnd // 2, 1)
                    cwnd = mss
                    print(f"Reenviando pacote {ultimo_ack} devido a timeout. Novo cwnd: {cwnd}, sstresh: {sstresh}")
                    chunk_cabivel = min(connection.rwnd, int(cwnd))
                    payload_send = chunk_message(message, ultimo_ack, chunk_cabivel)
                    packet = create_packet(ultimo_ack, 0, connection.rwnd, payload_send)
                    connection.send(packet)
                    # Atualiza o t0 do pacote retransmitido e registra o evento
                    if ultimo_ack in packets_pending:
                        # packets_pending[ultimo_ack].t0 = time.time_ns()
                        log_packet_info("recebimento", "timeout/retransmitido", packets_pending[ultimo_ack])
            continue
        finally:
            connection.UDPClientSocket.settimeout(None)

        seqNum, ack, rwnd, _ = unwrap_packet(packet)
        with lock:
            tf = time.time_ns()
            print(f"ACK recebido: próximo número de sequência {seqNum} | Janela informada {rwnd}")
            connection.rwnd = rwnd

            # Remover todos os pacotes cujo número de sequência seja menor que o ack recebido
            keys_to_remove = [k for k in packets_pending if k < seqNum]
            if keys_to_remove:
                for k in keys_to_remove:
                    # Antes de remover, atualiza o tempo final e registra no log
                    packets_pending[k].tf = tf
                    log_packet_info(packets_pending[k])
                    del packets_pending[k]
            else:
                print(f"Nenhum pacote para remover com seq < {seqNum}")

            if ultimo_ack is not None and ultimo_ack == seqNum:
                num_duplicados += 1
                print(f"ACK duplicado! num: {num_duplicados}")
                if num_duplicados == 3:
                    print("Três ACK duplicados! Reenviando pacote.")
                    sstresh = max(cwnd // 2, 1)
                    cwnd = mss
                    num_duplicados = 0
                    chunk_cabivel = min(connection.rwnd, int(cwnd))
                    payload_send = chunk_message(message, ultimo_ack, chunk_cabivel)
                    packet = create_packet(ultimo_ack, 0, connection.rwnd, payload_send)
                    connection.send(packet)
                    # Atualiza o tempo de envio do pacote retransmitido e registra no log
                    if ultimo_ack in packets_pending:
                        packets_pending[ultimo_ack].t0 = time.time_ns()
                        log_packet_info(packets_pending[ultimo_ack])
            else:
                num_duplicados = 0

            ultimo_ack = seqNum
            # Ajuste simples do cwnd
            if cwnd < sstresh:
                cwnd *= 2
                print(f"Slow Start: novo cwnd {cwnd}")
            else:
                cwnd += mss
                print(f"Congestion Avoidance: novo cwnd {int(cwnd)}")
    print("Envio concluído. Encerrando thread de recebimento.")

# Thread para monitorar timeouts dos pacotes já enviados
def thread_timeout(connection: UDPClient, message: str):
    global cwnd, sstresh, packets_enviados, packets_pending, finished
    while not finished:
        time.sleep(0.5)  # Verifica a cada 0.5s
        current_time = time.time_ns()
        with lock:
            for seq, pkt_data in list(packets_pending.items()):
                elapsed = (current_time - pkt_data.t0) / 1e9  # Converte para segundos
                if elapsed > TIMEOUT_THRESHOLD:
                    print(f"Timeout detectado para o pacote {seq} (elapsed: {elapsed:.2f}s). Reenviando...")
                    sstresh = max(cwnd // 2, 1)
                    cwnd = mss
                    if seq in packets_enviados:
                        packet, orig_time, payload_send = packets_enviados[seq]
                        # Atualiza o tempo de envio para reiniciar o contador de timeout
                        pkt_data.t0 = time.time_ns()
                        connection.send(packet)
                        log_packet_info(pkt_data)
                    else:
                        print(f"Pacote {seq} não encontrado em packets_enviados.")
    print("Thread de timeout encerrada.")

if __name__ == "__main__":
    # Inicializa o arquivo CSV com cabeçalho
    init_csv_log(CSV_FILENAME)
    path = os.path.join("storage", "img.jpg")

    connection = UDPClient(localIP, localPort, isn)
    # Exemplo com mensagem codificada; descomente para usar arquivo
    with open(path, "rb") as img:
        message = base64.b64encode(img.read())
        message = str(message)
    # message = '1111111100000000110011000011001111000110101010101111100000111011010110011110100001010101010101101'
    print(f"Mensagem: {message} | Tamanho: {len(message)}")

    t_envio = threading.Thread(target=thread_envio, args=(connection, message))
    t_recebimento = threading.Thread(target=thread_recebimento, args=(connection, message))
    t_timeout = threading.Thread(target=thread_timeout, args=(connection, message))

    t_envio.start()
    t_recebimento.start()
    t_timeout.start()

    t_envio.join()
    t_recebimento.join()
    t_timeout.join()

    print("Processo encerrado.")
