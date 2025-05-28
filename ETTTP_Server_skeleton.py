import random
import tkinter as tk
from socket import *
import _thread

from ETTTP_TicTacToe_skeleton import TTT, check_msg
    
    
if __name__ == '__main__':
    
    global send_header, recv_header
    SERVER_PORT = 12000
    SIZE = 1024
    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.bind(('',SERVER_PORT))
    server_socket.listen()
    MY_IP = '127.0.0.1'
    
    while True:
        client_socket, client_addr = server_socket.accept()
        
        start = random.randrange(0,2)   # select random to start
        
        ###################################################################
        # Send start move information to peer
        init_msg = (
            f"SEND ETTTP/1.0\r\n"
            f"Host: {MY_IP}\r\n"
            f"First-User: {start}\r\n"
            f"\r\n"
        )
        client_socket.send(init_msg.encode())
        
        # Receive ack - if ack is correct, start game
        ack = client_socket.recv(SIZE).decode()
        if not ack.startswith('ACK ETTTP/1.0'):
            raise RuntimeError("ACK not received for initial handshake")
        ###################################################################
        
        root = TTT(client=False,
                   target_socket=client_socket,
                   src_addr=MY_IP,
                   dst_addr=client_addr[0])
        root.play(start_user=start)
        root.mainloop()
        
        client_socket.close()
        break

    server_socket.close()
