import socket
from threading import Thread
import time

My_IP = '127.0.0.1'
My_PORT = 50000

class User:
    def __init__(self, conn, name, port, ip):
        self.conn = conn
        self.name = name
        self.port = port
        self.ip = ip

users = []
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((My_IP, My_PORT))
print('Listening on Port ',My_PORT, ' for incoming TCP connections')

sock.listen(1)
print('Listening ...')

def broadcast(message):
    global users
    for user in users:
        print('sending message to ', user.name)
        user.conn.send(message.encode('utf-8'))

def handle_message(conn, message, addr):
    global users
    try:
        action = message.split(' ')[0]
        if action == 'BROADCAST':
            name = filter(lambda x: x.ip == addr, users).__next__().name
            broadcast(f'MESSAGE {name} {message[10:]}')
        else:
            conn.send(f'ERROR ungültige aktion {message}'.encode('utf-8'))
    except Exception as e:
        print('Error while handling message: ', e)

def handle_connection(conn, addr):
    global users
    message = conn.recv(1024).decode('utf-8')
    name = message.split(' ')[1]
    port = message.split(' ')[2]
    broadcast(f'JOIN {name} {addr} {port}')
    # conn.send(f'REGISTERED {name}'.encode('utf-8'))
    userlist = ''
    for user in users:
        userlist += f'{user.name} {user.ip} {user.port};'
    conn.send(f'USERS {userlist}'.encode('utf-8'))
    users.append(User(conn, name, port, addr))
    while True:
        try:
            data = conn.recv(1024)
            if not data: # receiving empty messages means that the socket other side closed the socket
                print('Connection closed from other side')
                print('Closing ...')
                conn.close()
            print('received message: ', data.decode('utf-8'), 'from ', addr)
            handle_message(conn, data.decode('utf-8'), addr)
        except:
            print('client disconnected')
            print(len(users))
            user = filter(lambda x: x.name == name, users).__next__()
            users = list(filter(lambda x: x.name != name, users))
            print(len(users))
            broadcast(f'LEAVE {user.name}')
            break
    
while True:
    try:
        conn, addr = sock.accept()
        addr = addr[0]
        print('Incoming connection accepted: ', addr)
        Thread(target=handle_connection, args=[conn, addr]).start()
    except socket.timeout:
        print('Socket timed out listening',time.asctime())