import socket
from threading import Thread
import time

class User:
    def __init__(self, conn, name, port, ip):
        self.conn = conn
        self.name = name
        self.port = port
        self.ip = ip

Server_IP = '127.0.0.1'
name = 'Client'
Server_PORT = 50000
My_UDB_Port = 50003
My_TCP_Port = 50004
USERS = []


def listen_to_server(socket):
    global USERS
    while True:
        msg = socket.recv(1).decode('utf-8')
        while msg[-1] != '$':
            msg += socket.recv(1).decode('utf-8')
        msg = msg[:-1]
        action = msg.split(' ')[0]
        if action == 'JOIN':
            USERS.append(User(None, msg.split(' ')[1], msg.split(' ')[3], msg.split(' ')[2]))
            print('User ', msg.split(' ')[1], ' joined')
        elif action == 'LEAVE':
            USERS.remove(filter(lambda x: x.name == msg.split(' ')[1], USERS).__next__())
            print('User ', msg.split(' ')[1], ' left')
        elif action == 'MESSAGE':
            name = msg.split(' ')[1]
            message = msg[9+len(name):]
            print(name, ' Broadcasts: ', message)
        else:
            print('Error: ', msg)

def listen_to_commandline(tcp_client):
    global USERS
    while True:
        try:
            message = input()
            message = message.append('$')
            command = message.split(' ')[0]
            if command == 'BROADCAST':
                tcp_client.send(message.encode('utf-8'))
            else:
                user = filter(lambda x: x.name == command, USERS).__next__()
                if user:
                    if (user.conn):
                        user.conn.send(f'MESSAGE {message[(len(user.name) + 1):]}'.encode('utf-8'))
                    else:
                        udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        udp_client.sendto(f'CONNECT {name} {My_TCP_Port}$'.encode('utf-8'), (user.ip, int(user.port)))
                        udp_client.close()
                        while not user.conn:
                            time.sleep(1)
                        user.conn.send(f'MESSAGE {message[(len(user.name) + 1):]}'.encode('utf-8'))
        except Exception as e:
            print('Error: ', e)

def listen_to_tcp_connection(user):
    while True:
        try:
            data = user.conn.recv(1024)
            if not data:
                print('Connection closed from other side')
                print('Closing ...')
                user.conn.close()
                user.conn = None
                break
            command = data.decode('utf-8').split(' ')[0]
            if command == 'MESSAGE':
                print(user.name + ': ' + data.decode('utf-8')[8:])
            else:
                print('Error: ', data.decode('utf-8'))
        except Exception as e:
            print('Error: ', e)
            user.conn.close()
            user.conn = None
            break

def listen_to_udp_server(udp_server):
    global USERS
    while True:
        data, addr = udp_server.recvfrom(1024)
        action = data.decode('utf-8').split(' ')[0]
        if action == 'CONNECT':
            user = filter(lambda x: x.name == data.decode('utf-8').split(' ')[1], USERS).__next__()
            port = data.decode('utf-8').split(' ')[2]
            user.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            user.conn.connect((user.ip, int(port)))
            USERS = list(filter(lambda x: x.name != user.name, USERS))
            USERS.append(user)
            Thread(target=listen_to_tcp_connection, args=[user]).start()
            print('Connected to ', user.name)
        else:
            print('Error unnknown command: ', data.decode('utf-8'))

def listen_to_tcp_server(tcp_server):
    global USERS
    while True:
        conn, addr = tcp_server.accept()
        addr = addr[0]
        user = filter(lambda x: x.ip == addr, USERS).__next__()
        user.conn = conn
        Thread(target=listen_to_tcp_connection, args=[user]).start()


udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind(('', My_UDB_Port))
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.bind(('', My_TCP_Port))
tcp_server.listen(1)

tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Connecting to TCP server with IP ', Server_IP, ' on Port ', Server_PORT)
tcp_client.connect((Server_IP, Server_PORT))
tcp_client.send(f'REGISTER {name} {My_UDB_Port}$'.encode('utf-8'))
userliste = tcp_client.recv(1024).decode('utf-8').replace('USERS ', '')
for user in userliste.split(';'):
    if len(user) > 3:
        print(user)
        user = user.split(' ')
        USERS.append(User(None, user[0], user[2], user[1]))

Thread(target=listen_to_server, args=[tcp_client]).start()
Thread(target=listen_to_commandline, args=[tcp_client]).start()
Thread(target=listen_to_tcp_server, args=[tcp_server]).start()
Thread(target=listen_to_udp_server, args=[udp_server]).start()