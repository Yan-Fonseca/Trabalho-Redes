import matplotlib.pyplot as plt
import numpy as np
import csv

def interpolate_missing_tf(filename):
    data = []
    
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            data.append(row)
    
    # Converter para dicionário para facilitar manipulação
    packets = {}
    for row in data:
        seq_number = int(row[0])
        t0 = int(row[1])
        tf = int(row[2]) if row[2] else None
        tam = int(row[3])
        
        if seq_number not in packets:
            packets[seq_number] = []
        packets[seq_number].append([t0, tf, tam])
    
    # Interpolar valores ausentes de tf
    for seq, values in packets.items():
        last_valid_tf = None
        for i in range(len(values)):
            if values[i][1] is not None:
                last_valid_tf = values[i][1]
            else:
                # Se não há tf válido anterior, tentamos prever com um próximo
                if last_valid_tf is not None:
                    values[i][1] = last_valid_tf
    
    # Reconstruir lista interpolada
    interpolated_data = []
    for seq, values in packets.items():
        for t0, tf, tam in values:
            interpolated_data.append([seq, t0, tf, tam])
    
    # Escrever os dados corrigidos
    output_file = filename.replace(".csv", "_interpolated.csv")
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(interpolated_data)
    
    print(f"Arquivo interpolado salvo como {output_file}")
    return output_file

def plot_graphics(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        obj = list(reader)
    
    tempo_zero = int(obj[1][1])
    tempos = []
    payload_tam = []

    for i in range(1, len(obj)):
        if obj[i][2]:
            tempos.append((int(obj[i][2]) - tempo_zero) / 1e6)
            payload_tam.append(int(obj[i][0]))
    
    tempos = np.array(tempos)
    payload_tam = np.array(payload_tam)

    plt.figure(figsize=(8, 5))
    plt.step(tempos, payload_tam, color="b")
    plt.xlabel("t (ms)")
    plt.ylabel("Número do pacote")
    plt.title("Tempo de atraso para cada pacote")
    plt.grid(True)
    plt.show()

def graphic2(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)

        obj = []
        for row in reader:
            obj.append(row)

        tempo_zero = obj[1][1]
        tempos = []
        payload_tam = []

        for i in range(1,len(obj)-1):
            if obj[i][2] != '':
                tempos.append((int(obj[i][2]) - int(tempo_zero))/10e6)
                payload_tam.append(int(obj[i][3]))
        
        tempos = np.array(tempos)
        payload_tam = np.array(payload_tam)

        plt.figure(figsize=(8, 5))
        plt.step(tempos, payload_tam, color="b")
        plt.xlabel("t(ms)")
        plt.ylabel("tamanho do pacote (bits)")
        plt.title("tamanho do pacote enviado em relação ao tempo")
        plt.legend()
        plt.grid(True)
        plt.show()

filename = "packets_log.csv"
interpolated_filename = interpolate_missing_tf(filename)
plot_graphics(interpolated_filename)
graphic2(interpolated_filename)