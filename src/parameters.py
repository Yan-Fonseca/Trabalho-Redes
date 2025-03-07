import socket
import struct
import time
import random
import threading

localIP = '127.0.0.1'
localPort = 5005
bufferSize  = 1024 # max size of the buffer
ISN = 2000