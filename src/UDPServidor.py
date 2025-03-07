from parameters import *

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))

print("Servidor UDP up e escutando...")

expected_seq = 2000  # Sequência inicial, de acordo com o cliente
buffer = {}         # Buffer para armazenar pacotes fora de ordem

while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    try:
        decoded = message.decode()
        seq_str, payload = decoded.split(":", 1)
        seq = int(seq_str)
    except Exception as e:
        print("Erro ao decodificar o pacote:", e)
        continue

    if seq == expected_seq:
        # Entrega imediata para a aplicação
        print(f"Entregando pacote {seq}: {payload}")
        expected_seq += 1

        # Se houver pacotes no buffer, mostra o estado 
        if buffer:
            print("\nEstado atual do buffer:")
            buffer = dict(sorted(buffer.items()))
            print(buffer)
        
        # Verifica se o próximo(s) pacote(s) já chegou(ram) e estão armazenados no buffer
        while expected_seq in buffer:
            print(f"Entregando pacote {expected_seq}: {buffer.pop(expected_seq)}")
            expected_seq += 1
    
        # Envia ACK de volta para o cliente
        ack = f"ACK:{seq}"
        UDPServerSocket.sendto(ack.encode(), address)

    elif seq > expected_seq:
        # Armazena no buffer para entrega futura
        print(f"Recebido pacote {seq} fora de ordem, armazenando no buffer")
        buffer[seq] = payload
        # Ordena o buffer para visualização e mostra o estado ordenado
        buffer = dict(sorted(buffer.items()))
        # Imprime o estado do buffer desordenado
        print(f"Estado atual do buffer: {buffer}")
        # print(f"Próximo pacote esperado: {expected_seq}")

    else:
        # Pacote duplicado ou já entregue
        print(f"Pacote {seq} duplicado ou já entregue, descartado")
