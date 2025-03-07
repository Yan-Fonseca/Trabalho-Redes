from parameters  import *

class Buffer:
    def __init__(self, maxSize):
        self.maxSize = maxSize
        self.buffer = {}

    def add(self, index, value):
        self.buffer[index] = value

    def remove(self, index):
        del self.buffer[index]

    def available_size(self):
        return self.maxSize - len(self.buffer)

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))

ISN = 2000 # Assumiu-se que era 2000. Esse número era pra ter sido obtido a partir do 3-way-handshake
buffer = Buffer(bufferSize)

while True:
    