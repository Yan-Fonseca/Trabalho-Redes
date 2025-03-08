import socket
import struct
import time
import random
import threading

# constantes
localIP = '127.0.0.1'
localPort = 5005
clientMaxBufferSize  = 1024 
serverMaxBufferSize = 100
isn = 0
window_size = 8

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