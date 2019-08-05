import threading, queue
import modules

HOST = modules.HOST
PORT = modules.PORT

send_queues = {}                                                # Define a dict(send_queues)  
lock = threading.Lock()                                         # Define a LOCK. Will be used for queues precessing

def handle_client_recv(sock, addr):
   """ Receive messages from client and broadcast them to
       other clients until client disconnects """
   rest = bytes()                                               # Define rest because it's used later
   while True:
       try:
           (msgs, rest) = modules.recv_msgs(sock, rest)         # list(msgs) and rest are returned
       except (EOFError, ConnectionError):
           handle_disconnect(sock, addr)
           break
       for msg in msgs:
           msg = '{}: {}'.format(addr, msg)
           print(msg)
           broadcast_msg(msg)                                   # See func below

def handle_client_send(sock, q, addr):
   """ Monitor queue for new messages, send them to client as
       they arrive """
   while True:
       msg = q.get()                                            # Get a message from particular queue
       if msg == None: break
       try:
           modules.send_msg(sock, msg)                          # Transmit a message
       except (ConnectionError, BrokenPipe):
           handle_disconnect(sock, addr)
           break

def broadcast_msg(msg):
   """ Add message to each connected client's send queue """
   with lock:                                                  # LOCK 
       for q in send_queues.values():                          # for every queue add a message for transfer
           q.put(msg)

def handle_disconnect(sock, addr):
   """ Ensure queue is cleaned up and socket closed when a client
       disconnects """
   fd = sock.fileno()
   with lock:
       # Get send queue for this client
       q = send_queues.get(fd, None)                           # Get a queue from message_queues with LOCK
   # If we find a queue then this disconnect has not yet
   # been handled
   if q:
       q.put(None)                                             # ?
       del send_queues[fd]                                     # Delete a queue from dictionary
       addr = sock.getpeername()
       print('Client {} disconnected'.format(addr))
       sock.close()

if __name__ == '__main__':
    listen_sock = modules.create_listen_socket(HOST, PORT)
    addr = listen_sock.getsockname()
    print('Listening on {}'.format(addr))
    while True:
        client_sock,addr = listen_sock.accept()
        q = queue.Queue()
        with lock:
            send_queues[client_sock.fileno()] = q
            recv_thread = threading.Thread(target=handle_client_recv,
                                              args=[client_sock, addr],
                                              daemon=True)
            send_thread = threading.Thread(target=handle_client_send,
                                              args=[client_sock, q,
                                                    addr],
                                              daemon=True)
            recv_thread.start()
            send_thread.start()
            print('Connection from {}'.format(addr))
