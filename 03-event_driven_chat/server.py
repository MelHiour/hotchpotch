import select
import modules

from types import SimpleNamespace
from collections import deque

HOST = modules.HOST
PORT = modules.PORT
clients = {}

def create_client(sock):
   """ Return an object representing a client """
   return SimpleNamespace(
                   sock=sock,
                   rest=bytes(),
                   send_queue=deque())

def broadcast_msg(msg):
   """ Add message to all connected clients' queues """
   data = modules.prep_msg(msg)

   for client in clients.values():
       client.send_queue.append(data)
       poll.register(client.sock, select.POLLOUT)

if __name__ == '__main__':
   listen_sock = modules.create_listen_socket(HOST, PORT)
   poll = select.poll()
   poll.register(listen_sock, select.POLLIN)
   addr = listen_sock.getsockname()
   print('Listening on {}'.format(addr))
   # This is the event loop. Loop indefinitely, processing events
   # on all sockets when they occur
   while True:
       # Iterate over all sockets with events
       for fd, event in poll.poll():
           # clear-up a closed socket
            if event & (select.POLLHUP |
                       select.POLLERR |
                       select.POLLNVAL):
               poll.unregister(fd)
               del clients[fd]

           # Accept new connection, add client to clients dict
            elif fd == listen_sock.fileno():
               client_sock,addr = listen_sock.accept()
               client_sock.setblocking(False)
               fd = client_sock.fileno()
               clients[fd] = create_client(client_sock)
               poll.register(fd, select.POLLIN)
               print('Connection from {}'.format(addr))

           # Handle received data on socket
            elif event & select.POLLIN:
               client = clients[fd]
               addr = client.sock.getpeername()
               recvd = client.sock.recv(4096)
               if not recvd:
                   # the client state will get cleaned up in the
                   # next iteration of the event loop, as close()
                   # sets the socket to POLLNVAL
                   client.sock.close()
                   print('Client {} disconnected'.format(addr))
                   continue
               data = client.rest + recvd
               (msgs, client.rest) = modules.parse_recvd_data(data)
               # If we have any messages, broadcast them to all
               # clients
               for msg in msgs:
                   msg = '{}: {}'.format(addr, msg)
                   print(msg)
                   broadcast_msg(msg)

            # Send message to ready client
            elif event & select.POLLOUT:
               client = clients[fd]
               data = client.send_queue.popleft()
               sent = client.sock.send(data)
               if sent < len(data):
                   client.sends.appendleft(data[sent:])
               if not client.send_queue:
                   poll.modify(client.sock, select.POLLIN)
