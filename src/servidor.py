from parameters import *

# Buffer para arm. pacotes e recuperar ordem
buffer = {}

# ISN
expected_seq = 0

# lock para não ter data race
lock = threading.Lock()

def receive_data():
    global expected_seq

    # declara socket e dá bind
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST_IP, HOST_PORT))
    
    print(f"Servidor UP em {HOST_IP}:{HOST_PORT}...")

    while True:
        data, addr = sock.recvfrom(1024)
        seq_num, payload = struct.unpack("!I", data[:4])[0], data[4:]

        with lock:
            buffer[seq_num] = payload # armazena no buffer

            while expected_seq in buffer: # quando chegar o correto cai aqui
                print(f"Recebido (Seq {expected_seq}): {buffer[expected_seq].decode()}")
                del buffer[expected_seq]
                expected_seq += 1

receive_data()