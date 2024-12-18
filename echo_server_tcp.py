import socket
from threading import Thread
import time

My_IP = '127.0.0.1'
My_PORT = 50002

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((My_IP, My_PORT))
print('Listening on Port ',My_PORT, ' for incoming TCP connections');

sock.listen(1)
print('Listening ...')

def create_answer(message):
    id = message[0:16]
    op = message[16:19]
    number_count = int(message[19:23],2)
    
    numbers = []
    for i in range(number_count):
        number = int(message[23+(i*16):23+(i*16)+16],2)
        numbers.append(number)
        
    result = 0
    if op == "SUM":
        result = sum(numbers)
    elif op == "PRO":
        result = 1
        for number in numbers:
            result *= number
    elif op == "MIN":
        result = min(numbers)
    elif op == "MAX":
        result = max(numbers)
    
    return str(id) + str(result)

def handle_connection(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data: # receiving empty messages means that the socket other side closed the socket
                print('Connection closed from other side')
                print('Closing ...')
                conn.close()
            print('received message: ', data.decode('utf-8'), 'from ', addr)
            answer = create_answer(data.decode('utf-8'))
            conn.send(answer.encode('utf-8'))
        except socket.timeout:
            print('Socket timed out at',time.asctime())
    
     

while True:
    try:
        conn, addr = sock.accept()
        print('Incoming connection accepted: ', addr)
        Thread(target=handle_connection, args=[conn]).start()
    except socket.timeout:
        print('Socket timed out listening',time.asctime())