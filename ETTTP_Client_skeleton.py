import random
import tkinter as tk
from socket import *
import _thread

from ETTTP_TicTacToe_skeleton import TTT, check_msg
    

if __name__ == '__main__':

    SERVER_IP   = '127.0.0.1'
    MY_IP       = '127.0.0.1'
    SERVER_PORT = 12000
    SIZE        = 1024
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)

    with socket(AF_INET, SOCK_STREAM) as client_socket:
        client_socket.connect(SERVER_ADDR)  
        
        ###################################################################
        # Receive who will start first from the server
        init_msg = client_socket.recv(SIZE).decode()
        # validate protocol and host
        if not init_msg.startswith('SEND ETTTP/1.0') or not check_msg(init_msg, SERVER_IP):
            raise RuntimeError("Invalid initial handshake from server")
        # parse 'First-User' header
        start = None
        for line in init_msg.split('\r\n'):
            if line.startswith('First-User:'):
                start = int(line.split(': ')[1])
                break
        # if server didn't specify, pick randomly
        if start is None:
            start = random.choice([0, 1])

        # Send ACK
        ack_msg = init_msg.replace('SEND', 'ACK', 1)
        client_socket.send(ack_msg.encode())
        ###################################################################
        
        # Start game
        root = TTT(target_socket=client_socket, src_addr=MY_IP, dst_addr=SERVER_IP)
        root.play(start_user=start)
        root.mainloop()
        client_socket.close()
