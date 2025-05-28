import random
import tkinter as tk
from socket import *
import _thread

SIZE = 1024

class TTT(tk.Tk):
    def __init__(self, target_socket, src_addr, dst_addr, client=True):
        super().__init__()
        
        self.my_turn = -1

        self.geometry('500x800')

        self.active = 'GAME ACTIVE'
        self.socket = target_socket
        
        self.send_ip = dst_addr
        self.recv_ip = src_addr
        
        self.total_cells = 9
        self.line_size = 3
        
        # Set variables for Client and Server UI
        ############## updated ###########################
        if client:
            self.myID = 1   #0: server, 1: client
            self.title('34743-01-Tic-Tac-Toe Client')
            self.user = {'value': self.line_size+1, 'bg': 'blue',
                     'win': 'Result: You Won!', 'text':'O','Name':"YOU"}
            self.computer = {'value': 1, 'bg': 'orange',
                             'win': 'Result: You Lost!', 'text':'X','Name':"ME"}   
        else:
            self.myID = 0
            self.title('34743-01-Tic-Tac-Toe Server')
            self.user = {'value': 1, 'bg': 'orange',
                         'win': 'Result: You Won!', 'text':'X','Name':"ME"}   
            self.computer = {'value': self.line_size+1, 'bg': 'blue',
                     'win': 'Result: You Lost!', 'text':'O','Name':"YOU"}
        ##################################################

        self.board_bg = 'white'
        self.all_lines = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
                          (0, 3, 6), (1, 4, 7), (2, 5, 8),
                          (0, 4, 8), (2, 4, 6))

        self.create_control_frame()

    def create_control_frame(self):
        '''
        Make Quit button to quit game 
        Click this button to exit game
        '''
        self.control_frame = tk.Frame()
        self.control_frame.pack(side=tk.TOP)

        self.b_quit = tk.Button(self.control_frame, text='Quit',
                                command=self.quit)
        self.b_quit.pack(side=tk.RIGHT)

    def create_status_frame(self):
        '''
        Status UI that shows "Hold" or "Ready"
        '''
        self.status_frame = tk.Frame()
        self.status_frame.pack(expand=True,anchor='w',padx=20)
        
        self.l_status_bullet = tk.Label(self.status_frame,text='O',font=('Helevetica',25,'bold'),justify='left')
        self.l_status_bullet.pack(side=tk.LEFT,anchor='w')
        self.l_status = tk.Label(self.status_frame,font=('Helevetica',25,'bold'),justify='left')
        self.l_status.pack(side=tk.RIGHT,anchor='w')

    def create_result_frame(self):
        '''
        UI that shows Result
        '''
        self.result_frame = tk.Frame()
        self.result_frame.pack(expand=True,anchor='w',padx=20)
        
        self.l_result = tk.Label(self.result_frame,font=('Helevetica',25,'bold'),justify='left')
        self.l_result.pack(side=tk.BOTTOM,anchor='w')

    def create_debug_frame(self):
        '''
        Debug UI that gets input from the user
        '''
        self.debug_frame = tk.Frame()
        self.debug_frame.pack(expand=True)
        
        self.t_debug = tk.Text(self.debug_frame,height=2,width=50)
        self.t_debug.pack(side=tk.LEFT)
        self.b_debug = tk.Button(self.debug_frame,text="Send",command=self.send_debug)
        self.b_debug.pack(side=tk.RIGHT)
    
    def create_board_frame(self):
        '''
        Tic-Tac-Toe Board UI
        '''
        self.board_frame = tk.Frame()
        self.board_frame.pack(expand=True)

        self.cell = [None] * self.total_cells
        self.setText=[None]*self.total_cells
        self.board = [0] * self.total_cells
        self.remaining_moves = list(range(self.total_cells))
        for i in range(self.total_cells):
            self.setText[i] = tk.StringVar()
            self.setText[i].set("  ")
            self.cell[i] = tk.Label(self.board_frame, highlightthickness=1,borderwidth=5,relief='solid',
                                    width=5, height=3,
                                    bg=self.board_bg,compound="center",
                                    textvariable=self.setText[i],font=('Helevetica',30,'bold'))
            self.cell[i].bind('<Button-1>',
                              lambda e, move=i: self.my_move(e, move))
            r, c = divmod(i, self.line_size)
            self.cell[i].grid(row=r, column=c,sticky="nsew")

    def play(self, start_user=1):
        '''
        Call this function to initiate the game
        '''
        self.last_click = 0
        self.create_board_frame()
        self.create_status_frame()
        self.create_result_frame()
        self.create_debug_frame()
        self.state = self.active
        if start_user == self.myID:
            self.my_turn = 1    
            self.user['text'] = 'X'
            self.computer['text'] = 'O'
            self.l_status_bullet.config(fg='green')
            self.l_status['text'] = ['Ready']
        else:
            self.my_turn = 0
            self.user['text'] = 'O'
            self.computer['text'] = 'X'
            self.l_status_bullet.config(fg='red')
            self.l_status['text'] = ['Hold']
            _thread.start_new_thread(self.get_move,())

    def quit(self):
        '''
        Call this function to close GUI
        '''
        self.destroy()
        
    def my_move(self, e, user_move):    
        '''
        Read button when the player clicks the button
        '''
        if self.board[user_move] != 0 or not self.my_turn:
            return
        valid = self.send_move(user_move)
        if not valid:
            self.quit()
        self.update_board(self.user, user_move)
        if self.state == self.active:    
            self.my_turn = 0
            self.l_status_bullet.config(fg='red')
            self.l_status ['text'] = ['Hold']
            _thread.start_new_thread(self.get_move,())

    def get_move(self):
        '''
        Function to get move from other peer
        '''
        ###################  Fill Out  #######################
        # receive message
        msg = self.socket.recv(SIZE).decode()
        # validate
        if not msg.startswith('SEND ETTTP/1.0') or not check_msg(msg, self.recv_ip):
            self.socket.close()
            self.quit()
            return
        # parse move
        loc = None
        for line in msg.split('\r\n'):
            if line.startswith('New-Move:'):
                r, c = map(int, line.split(': ')[1].strip('()').split(','))
                loc = r * self.line_size + c
                break
        # send ACK
        ack = msg.replace('SEND','ACK',1)
        self.socket.send(ack.encode())
        ######################################################   
        self.update_board(self.computer, loc, get=True)
        if self.state == self.active:  
            self.my_turn = 1
            self.l_status_bullet.config(fg='green')
            self.l_status ['text'] = ['Ready']
                
    def send_debug(self):
        '''
        Function to send message to peer using input from the textbox
        '''

        if not self.my_turn:
            self.t_debug.delete(1.0,"end")
            return
        d_msg = self.t_debug.get(1.0,"end").strip()
        self.t_debug.delete(1.0,"end")
        try:
            r, c = map(int, d_msg.split(','))
        except:
            return
        loc = r * self.line_size + c
        ###################  Fill Out  #######################
        # check free
        if self.board[loc] != 0:
            return
        # send message
        msg = (f"SEND ETTTP/1.0\r\n"
               f"Host: {self.send_ip}\r\n"
               f"New-Move: ({r}, {c})\r\n\r\n")
        self.socket.send(msg.encode())
        # receive ACK
        ack = self.socket.recv(SIZE).decode()
        if not ack.startswith('ACK ETTTP/1.0') or not check_msg(ack, self.recv_ip):
            return
        ######################################################  
        self.update_board(self.user, loc)
        if self.state == self.active:
            self.my_turn = 0
            self.l_status_bullet.config(fg='red')
            self.l_status ['text'] = ['Hold']
            _thread.start_new_thread(self.get_move,())
        
    def send_move(self, selection):
        '''
        Function to send message to peer using button click
        '''
        row, col = divmod(selection, self.line_size)
        ###################  Fill Out  #######################
        msg = (f"SEND ETTTP/1.0\r\n"
               f"Host: {self.send_ip}\r\n"
               f"New-Move: ({row}, {col})\r\n\r\n")
        self.socket.send(msg.encode())
        # receive ACK
        ack = self.socket.recv(SIZE).decode()
        if not ack.startswith('ACK ETTTP/1.0') or not check_msg(ack, self.recv_ip):
            return False
        return True
        ######################################################  

    def check_result(self, winner, get=False):
        '''
        Function to check if the result between peers are same
        '''
        ###################  Fill Out  #######################
        if not get:
            # send result
            msg = (f"RESULT ETTTP/1.0\r\n"
                   f"Host: {self.send_ip}\r\n"
                   f"Winner: {winner}\r\n\r\n")
            self.socket.send(msg.encode())
            # receive ACK
            ack = self.socket.recv(SIZE).decode()
            if not ack.startswith('ACK ETTTP/1.0') or not check_msg(ack, self.recv_ip):
                return False
            return True
        else:
            # receive result
            msg = self.socket.recv(SIZE).decode()
            if not msg.startswith('RESULT ETTTP/1.0') or not check_msg(msg, self.recv_ip):
                return False
            peer = None
            for line in msg.split('\r\n'):
                if line.startswith('Winner:'):
                    peer = line.split(': ')[1]
                    break
            # send ACK
            ack = msg.replace('RESULT','ACK',1)
            self.socket.send(ack.encode())
            return (peer == winner)
        ######################################################  

    def update_board(self, player, move, get=False):
        self.board[move] = player['value']
        self.remaining_moves.remove(move)
        self.cell[self.last_click]['bg'] = self.board_bg
        self.last_click = move
        self.setText[move].set(player['text'])
        self.cell[move]['bg'] = player['bg']
        self.update_status(player,get=get)

    def update_status(self, player,get=False):
        winner_sum = self.line_size * player['value']
        for line in self.all_lines:
            if sum(self.board[i] for i in line) == winner_sum:
                self.l_status_bullet.config(fg='red')
                self.l_status ['text'] = ['Hold']
                self.highlight_winning_line(player, line)
                correct = self.check_result(player['Name'],get=get)
                if correct:
                    self.state = player['win']
                    self.l_result['text'] = player['win']
                else:
                    self.l_result['text'] = "Somethings wrong..."

    def highlight_winning_line(self, player, line):
        for i in line:
            self.cell[i]['bg'] = 'red'

# End of Root class

def check_msg(msg, recv_ip):
    """
    Function that checks if received message is valid ETTTP format, including initial handshake
    """
    # Split by CRLF
    lines = msg.split('\r\n')
    if len(lines) < 3:
        return False
    parts = lines[0].split(' ')
    if len(parts) != 2:
        return False
    cmd, ver = parts
    # Must be correct version and command
    if ver != 'ETTTP/1.0' or cmd not in ('SEND','ACK','RESULT'):
        return False
    # Parse headers
    headers = {}
    i = 1
    while i < len(lines) and lines[i]:
        if ': ' not in lines[i]:
            return False
        k, v = lines[i].split(': ', 1)
        headers[k] = v
        i += 1
    # Host validation
    if headers.get('Host') != recv_ip:
        return False
    # Handle SEND or ACK
    if cmd in ('SEND','ACK'):
        # Accept either New-Move or First-User headers
        if 'New-Move' in headers:
            try:
                r, c = map(int, headers['New-Move'].strip('()').split(','))
                if not (0 <= r < 3 and 0 <= c < 3):
                    return False
            except:
                return False
        elif 'First-User' in headers:
            if headers['First-User'] not in ('0', '1'):
                return False
        else:
            return False
    else:
        # RESULT
        if headers.get('Winner') not in ('ME','YOU'):
            return False
    return True
