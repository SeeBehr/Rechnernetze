import socket
import time

Server_IP = '127.0.0.1'
Server_PORT = 50002

i = 0
def message_builder(op, numbers):
    global i
    
    id = '{0:016b}'.format(i)
    i+=1
    number_count = '{0:04b}'.format(len(numbers))
    
    message = id + op + number_count
    
    for number in numbers:
        message += '{0:016b}'.format(number)
    
    return message
    

MESSAGE = message_builder("MIN", [1,3,5])
print('Message to send: ', MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
print('Connecting to TCP server with IP ', Server_IP, ' on Port ', Server_PORT)
sock.connect((Server_IP, Server_PORT))
print('Sending message', MESSAGE)
sock.send(MESSAGE.encode('utf-8'))
try:
    msg=sock.recv(1024).decode('utf-8')
    print('Message received; ', msg)
except socket.timeout:
    print('Socket timed out at',time.asctime())
time.sleep(10)
sock.send(MESSAGE.encode('utf-8'))
try:
    msg=sock.recv(1024).decode('utf-8')
    print('Message received; ', msg)
except socket.timeout:
    print('Socket timed out at',time.asctime())
while True:
    time.sleep(1)