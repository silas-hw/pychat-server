import logging
logging.basicConfig(level=logging.INFO)

import socket 
import threading
import pickle

from classes import User, Message

server_user = User('SERVER', '#0d006e')

HEADER = 64
PORT = 5000
#IP = socket.gethostbyname(socket.gethostname()) # prevents hard coding ip address
IP = '192.168.0.11'
ADDR = (IP, PORT)
FORMAT = 'utf-8'
DISCONNET_MESSAGE = "!close"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

clients = []

def send(msg, conn=None):
    message = pickle.dumps(msg)
    msgLength = len(message)
    sendLength = str(msgLength).encode(FORMAT)
    sendLength += b' ' * (HEADER-len(sendLength))
    
    if conn == None:
        for client in clients:
            client.send(sendLength)
            client.send(message)
    else:
        conn.send(sendLength)
        conn.send(message)

def handle_client(conn, addr):
    logging.info(f"[NEW CONNECTION] {addr} connected.")

    clients.append(conn)
    infoMsg = Message(f"[b]{addr[0]}[/b] connected", server_user)
    send(infoMsg)

    connected = True
    while connected:
        msgHeader = conn.recv(HEADER).decode(FORMAT)
        if msgHeader:
            msgLength = int(msgHeader)
            msg = conn.recv(msgLength)
            
            msg = pickle.loads(msg)

            if msg.content == DISCONNET_MESSAGE:
                logging.info(f"[CONNECTION ENDED] {addr} disconnected")
                send(msg, conn)
                break
            
            send(msg)
    
    clients.remove(conn)
    conn.close()

    send(f"[b]{addr[0]}[/b] disconnected")

def start():
    server.listen()
    logging.info(f"[LISTENING] Server is listening on {IP}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        logging.info(f"[CONN COUNT] {threading.activeCount()-1}")


if __name__ == '__main__':
    logging.info('[STARTING]')
    start()