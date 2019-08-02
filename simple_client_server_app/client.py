import sys, socket
import modules

HOST = sys.argv[-1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = modules.PORT

if __name__ == '__main__':
   while True:
       try:
           sock = socket.socket(socket.AF_INET,
                                socket.SOCK_STREAM)
           print('\nConnected to {}:{}'.format(HOST, PORT))
           print("Type message, enter to send, 'q' to quit")
           msg = input()
           if msg == 'q': break
           sock.connect((HOST, PORT))
           modules.send_msg(sock, msg)  # Blocks until sent
           print('Sent message: {}'.format(msg))
           msg = modules.recv_msg(sock)  # Block until
                                 # received complete
           print('Received echo: ' + msg)
       except ConnectionError:
           print('Socket error')
           break
       finally:
           sock.close()
           print('Closed connection to server\n')
