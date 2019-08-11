# Learning Python Network Programming
import socket

HOST = ''
PORT = 4041

def create_listen_socket(host, port):
    """ Setup the sockets our server will receive connection
    requests on """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    return sock


def parse_recvd_data(data):
   """ Break up raw received data into messages, delimited
       by null byte """
   parts = data.split(b'\0')
   msgs = parts[:-1]
   rest = parts[-1]
   return (msgs, rest)


def recv_msgs(sock, data=bytes()):
   """ Receive data and break into complete messages on null byte
      delimiter. Block until at least one message received, then
      return received messages """
   msgs = []
   while not msgs:
       recvd = sock.recv(4096)
       if not recvd:
           raise ConnectionError()
       data = data + recvd
       (msgs, rest) = parse_recvd_data(data)
   msgs = [msg.decode('utf-8') for msg in msgs]
   return (msgs, rest)


def prep_msg(msg):
   """ Prepare a string to be sent as a message """
   msg += '\0'
   return msg.encode('utf-8')

def send_msg(sock, msg):
   """ Send a string over a socket, preparing it first """
   data = prep_msg(msg)
   sock.sendall(data)
