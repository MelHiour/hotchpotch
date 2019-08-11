import select
import modules


from pprint import pprint

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
                   send_queue=deque())                              # list-like container with fast appends and pops on either end

def broadcast_msg(msg):
   """ Add message to all connected clients' queues """
   data = modules.prep_msg(msg)

   for client in clients.values():
       client.send_queue.append(data)
       poll.register(client.sock, select.POLLOUT)

if __name__ == '__main__':
   listen_sock = modules.create_listen_socket(HOST, PORT)
   poll = select.poll()                                             # Create a poll object. Interface to kernel poll service
   poll.register(listen_sock, select.POLLIN)                        # Register a socket a monitor if it can receive (pollin) data
   addr = listen_sock.getsockname()
   print('Listening on {}'.format(addr))
   # This is the event loop. Loop indefinitely, processing events
   # on all sockets when they occur
   while True:
       # Iterate over all sockets with events
       for fd, event in poll.poll():                                # Poll the poll object. Returns [(3, 1)]. See at the very bottom
           # clear-up a closed socket
            if event & (select.POLLHUP |                            # If event and it equals to 8,16... Look below
                       select.POLLERR |
                       select.POLLNVAL):
               poll.unregister(fd)                                  # Unregister and delete fd from dictionary
               del clients[fd]

           # Accept new connection, add client to clients dict
            elif fd == listen_sock.fileno():                        # if fd in poll is equal to listened fd
               client_sock,addr = listen_sock.accept()
               client_sock.setblocking(False)
               fd = client_sock.fileno()
               clients[fd] = create_client(client_sock)             # Add to the dictionary the fd:client object pair
               poll.register(fd, select.POLLIN)                     # Register Clients Socket
               print('Connection from {}'.format(addr))

           # Handle received data on socket
            elif event & select.POLLIN:                                 # If we have a ready socket with some data to be processed
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
                   broadcast_msg(msg)                                   # Actually appending data to the send_queue's dqueue

            # Send message to ready client
            elif event & select.POLLOUT:                                # If there is some data to send for POLLOUT socket
               client = clients[fd]                                     # Get client's socket
               data = client.send_queue.popleft()                       # Get the send_queue for the client (psb)
               sent = client.sock.send(data)                            # Returns the number of bytes sent
               if sent < len(data):
                   client.sends.appendleft(data[sent:])                 # sent is equal to lenth of bytes (say 30). Appending to sends?
               if not client.send_queue:
                   poll.modify(client.sock, select.POLLIN)

"""
<select.poll object at 0x107c94fc0>
(Pdb) poll.poll()
[(3, 1)]
(Pdb) select.POLLHUP
16
(Pdb) select.POLLERR
8
(Pdb) select.POLLIN
1

(Pdb) print(clients)
{4:
    namespace(rest=b'',
            send_queue=deque([]),
            sock=<socket.socket
                fd=4,
                family=AddressFamily.AF_INET,
                type=SocketKind.SOCK_STREAM,
                proto=0,
                laddr=('127.0.0.1', 4041),
                raddr=('127.0.0.1', 54992)>
                )
}

(Pdb) print(data)
b"('127.0.0.1', 55235): b'BLAH'\x00"

"""
