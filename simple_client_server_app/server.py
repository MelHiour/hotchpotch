import modules

HOST = modules.HOST
PORT = modules.PORT

def handle_client(sock, addr):
   """ Receive data from the client via sock and echo it back """
   try:
       msg = tincanchat.recv_msg(sock)  # Blocks until received
                                        # complete message
       print('{}: {}'.format(addr, msg))
       tincanchat.send_msg(sock, msg)  # Blocks until sent
   except (ConnectionError, BrokenPipeError):
       print('Socket error')
   finally:
       print('Closed connection to {}'.format(addr))
       sock.close()

if __name__ == '__main__':
   listen_sock = modules.create_listen_socket(HOST, PORT)
   addr = listen_sock.getsockname()
   print('Listening on {}'.format(addr))
   while True:
       client_sock, addr = listen_sock.accept()
       print('Connection from {}'.format(addr))
       handle_client(client_sock, addr)
