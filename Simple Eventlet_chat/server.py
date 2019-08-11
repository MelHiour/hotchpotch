import eventlet
import eventlet.queue as queue
import modules

HOST = modules.HOST
PORT = modules.PORT
send_queues = {}

def handle_client_recv(sock, addr):
   """ Receive messages from client and broadcast them to
       other clients until client disconnects """
   rest = bytes()
   while True:
       try:
           (msgs, rest) = modules.recv_msgs(sock)
       except (EOFError, ConnectionError):
           handle_disconnect(sock, addr)
           break
       for msg in msgs:
           msg = '{}: {}'.format(addr, msg)
           print(msg)
           broadcast_msg(msg)

def handle_client_send(sock, q, addr):
   """ Monitor queue for new messages, send them to client as
       they arrive """
   while True:
       msg = q.get()
       if msg == None: break
       try:
           modules.send_msg(sock, msg)
       except (ConnectionError, BrokenPipe):
           handle_disconnect(sock, addr)
           break

def broadcast_msg(msg):
   """ Add message to each connected client's send queue """
   for q in send_queues.values():
       q.put(msg)

def handle_disconnect(sock, addr):
   """ Ensure queue is cleaned up and socket closed when a client
       disconnects """
   fd = sock.fileno()
   # Get send queue for this client
   q = send_queues.get(fd, None)
   # If we find a queue then this disconnect has not yet
   # been handled
   if q:
       q.put(None)
       del send_queues[fd]
       addr = sock.getpeername()
       print('Client {} disconnected'.format(addr))
       sock.close()

if __name__ == '__main__':
    server = eventlet.listen((HOST, PORT))          # not socket function from modules
    addr = server.getsockname()
    print('Listening on {}'.format(addr))
    while True:
        client_sock,addr = server.accept()
        q = queue.Queue()
        send_queues[client_sock.fileno()] = q       # changed with no LOCK
        eventlet.spawn_n(handle_client_recv,        # smilar to threads, but actually an nonblocking structures
                        client_sock,
                        addr)
        eventlet.spawn_n(handle_client_send,
                 client_sock,
                 q,
                 addr)
        print('Connection from {}'.format(addr))
