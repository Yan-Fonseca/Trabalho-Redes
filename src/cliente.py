from parameters import *

# abre um socket UDP
# AF_INET: socket usará IPv4
# SOCK_DGRAM: define que o socket usará UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

messages = [
    "1 - Banhato",
    "2 - Bheringol",
    "3 - Ervilha",
    "4 - Gustavo Rabbit",
    "5 - Lucas Slot",
    "6 - Yan Azedo"
]

# Gerando packets com seq. num. embaralhados
packets = [(i, msg.encode()) for i, msg in enumerate(messages)]
random.shuffle(packets) 

# Envia fora de ordem
for seq_num, payload in packets:
    print("# Enviado: ", payload)
    data = struct.pack("!I", seq_num) + payload
    sock.sendto(data, (HOST_IP, HOST_PORT))
    time.sleep(random.uniform(0, 0.1)) # atraso variável entre 0 e .1 segundo

sock.close()
