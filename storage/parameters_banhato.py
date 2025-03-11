import socket
import struct
import time
import random
import threading

# constantes
localIP = '127.0.0.1'
localPort = 5005
clientMaxBufferSize  = 1024 
# chunk_size = 8 # tamanho da janela default
mss = 8
serverMaxBufferSize = 4 * mss # a conta para dar o chunk size é chunk size * 4 (4 bytes cada char)
isn = 0

# funções auxiliares

def create_packet(seqNum:int, ack:int, rwnd:int, payload:str):
    # ! => big endian
    # I => inteiro
    # s => string
    format = "!III{}s".format(len(payload))
    packet = struct.pack(format, seqNum, ack, rwnd, payload.encode())
    return packet

def unwrap_packet(packet: struct.pack):
    payloadSize = len(packet) - struct.calcsize("!III")
    format = "!III{}s".format(payloadSize)
    seqNum, ack, rwnd, payload = struct.unpack(format, packet)
    return seqNum, ack, rwnd, payload.decode() if isinstance(payload, bytes) else payload

# retorna o chunk especificado a partir de begin
def chunk_message(message, begin, chunksize):
    return message[begin:(begin+chunksize)]

# a cada 3 pacotes, força a perda do próximo
def should_lose_packet(success_count: int) -> bool:
    # Evita simular perda no primeiro pacote (quando success_count é 0)
    if success_count > 0 and success_count % 3   == 0:
        return True
    return False