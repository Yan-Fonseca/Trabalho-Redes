import matplotlib.pyplot as plt
import numpy as np
import csv

def graphic1(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)

        obj = []
        for row in reader:
            obj.append(row)
        
        print(obj[1][1])

        tempo_zero = obj[1][1]
        tempos = []
        payload_tam = []

        for i in range(1,len(obj)):
            tempos.append((int(obj[i][1]) - int(tempo_zero))/10e6)
            payload_tam.append(int(obj[i][0]))
        
        tempos = np.array(tempos)
        payload_tam = np.array(payload_tam)

        plt.figure(figsize=(8, 5))
        plt.step(tempos, payload_tam, color="b")
        plt.xlabel("t(ms)")
        plt.ylabel("número do pacote")
        plt.title("tempo de atraso para cada pacote")
        plt.legend()
        plt.grid(True)
        plt.show()
        
def graphic2(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)

        obj = []
        for row in reader:
            obj.append(row)
        
        print(obj[1][1])

        tempo_zero = obj[1][1]
        tempos = []
        payload_tam = []

        for i in range(1,len(obj)):
            tempos.append((int(obj[i][1]) - int(tempo_zero))/10e6)
            payload_tam.append(int(obj[i][3]))
        
        tempos = np.array(tempos)
        payload_tam = np.array(payload_tam)

        plt.figure(figsize=(8, 5))
        plt.plot(tempos, payload_tam, color="b", marker = 'o')
        plt.xlabel("t(ms)")
        plt.ylabel("tamanho do pacote")
        plt.title("tamanho do pacote enviado em relação ao tempo")
        plt.legend()
        plt.grid(True)
        plt.show()

graphic2("storage\packets_time_RTT.csv")