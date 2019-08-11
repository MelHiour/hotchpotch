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
       msg = q.get()                                            # Get LAST message from queue
       if msg == None: break
       try:
           modules.send_msg(sock, msg)                          # Transmit a message
       except (ConnectionError, BrokenPipe):
           handle_disconnect(sock, addr)
           break

def broadcast_msg(msg):
   """ Add message to each connected client's send queue """
   with lock:                                                  # LOCK
       for q in send_queues.values():                          # for every queue (client, actually) add a message for transfer
           q.put(msg)

def handle_disconnect(sock, addr):
   """ Ensure queue is cleaned up and socket closed when a client
       disconnects """
   fd = sock.fileno()                                          # Get fd (say, queue id)
   with lock:
       # Get send queue for this client
       q = send_queues.get(fd, None)                           # Get the particular queue from message_queues with LOCK
   # If we find a queue then this disconnect has not yet
   # been handled
   if q:
       q.put(None)                                             # Put a NONE to queue for some reason
       del send_queues[fd]                                     # Delete a queue for particular client from dictionary
       addr = sock.getpeername()
       print('Client {} disconnected'.format(addr))
       sock.close()

if __name__ == '__main__':
    ''' Very lamerish  explanation
    AFter infinite loop has started the socket get expected for neew connection.
    1. User A has Connected
    2. Connection got accepted
    3. Queue is created and added to the dictionary with Lock
    4. Recv and Send threads have created and started
    5. End of round 1
    6. User B has connected
    7. Connection got accepted , queue created and added to dict
    8. Both threads recreated and rerun
    9. End of round 2
    10. No clients are about to join. We are stuck at listen_sock.accept() state. But both threads are still runing.
    '''
    listen_sock = modules.create_listen_socket(HOST, PORT)
    addr = listen_sock.getsockname()
    print('Listening on {}'.format(addr))
    while True:
        client_sock,addr = listen_sock.accept()
        q = queue.Queue()
        with lock:
            send_queues[client_sock.fileno()] = q              # Add a key-value to send_queues disctionary. See example at the very bottom
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

'''
Socket object:
 print(client_sock)
 <socket.socket
    fd=4,
    family=AddressFamily.AF_INET,
    type=SocketKind.SOCK_STREAM,
    proto=0,
    laddr=('127.0.0.1', 4041),
    addr=('127.0.0.1', 54823)>

send_queues dict:
(Pdb) print(send_queues)
{4: <queue.Queue object at 0x109a0ad50>}
'''
