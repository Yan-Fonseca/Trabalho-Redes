from parameters_banhato import *

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
    print(f"Mensagem: {message} | Tamanho da mensagem: {len(message)}")
    aux = ''

    index = connection.seqNum
    count = 0

    # Controle Congestionamento:
    cwnd = 1
    sstresh = 5
    ultimo_ack = None
    num_duplicados = 0

    while len(aux) != len(message):
    
        if connection.rwnd == 0:
            print("Rwnd zero. Aguardando atualização...")
            
            # Tenta receber um pacote para atualizar rwnd
            try:
                connection.UDPClientSocket.settimeout(2)  # Aguarda por uma atualização da janela
                packet = connection.recv()
                seqNum, ack, rwnd, _ = unwrap_packet(packet)
                connection.rwnd = rwnd  # Atualiza a janela com o novo valor enviado pelo servidor
                print(f"Novo rwnd: {connection.rwnd}")

            except socket.timeout:
                print("espera por atualizacao de rwnd...")

            continue  # Volta para a checagem de rwnd atualizado
        
        chunk_cabivel = min(connection.rwnd, int(cwnd))
        chunk_cabivel = min(chunk_cabivel, mss)
        payload_send = chunk_message(message, index, chunk_cabivel)
        print(f"\nEnviando {payload_send} | Tamanho do payload: {len(payload_send)}")

        packet = create_packet(count, 0, connection.rwnd, payload_send)

        retransmissoes = 0
        while True:
            connection.send(packet)
            # Time out pra perda de pacote:
            connection.UDPClientSocket.settimeout(1)
            
            try:
                packet = connection.recv()
            except socket.timeout:
                print("Timeout! Pacote perdido.")
                sstresh = max (cwnd // 2, 1)
                cwnd = 1
                # FAZER RETRANSMISSAO
                retransmissoes += 1
                if retransmissoes >= 3: # perda elevada de pacotes
                    print("Perda de pacote ocorreu 3 vezes. Reiniciando cwnd para 1.")
                    sstresh = max(cwnd // 2, 1)
                    cwnd = 1
                continue
            finally:
                connection.UDPClientSocket.settimeout(None)

            seqNum, ack, rwnd, _ = unwrap_packet(packet)
            print(f"ACK recebido: proximo numero de sequencia {seqNum} | Janela informada {rwnd}")
            
            # Buscar repeticao de ACK:
            if ultimo_ack != None and ultimo_ack == seqNum:
                num_duplicados += 1
                print(f"ACK duplicado! num: {num_duplicados}")
                if num_duplicados == 3:
                    print("Três ACK duplicados!")
                    sstresh = max(cwnd // 2, 1)
                    cwnd = 1
                    num_duplicados = 0
                    # FAZER RETRANSMISSAO
                    retransmissoes += 1
                    continue
            else:
                num_duplicados = 0

            ultimo_ack = seqNum
            connection.rwnd = rwnd # atualizo o rwnd
            break

        index += chunk_cabivel # atualizo o index
        aux += payload_send
        count += 1

        if cwnd < sstresh:
            # Slow Start:
            cwnd += 1
            print(f"Slow Start: novo cwnd {cwnd}")
        else:
            # Congestion Avoidance:
            cwnd += 1 / cwnd
            print(f"Congestion Avoidance: novo cwnd {int(cwnd)}")