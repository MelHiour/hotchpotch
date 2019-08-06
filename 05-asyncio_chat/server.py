import asyncio
import modules

HOST = modules.HOST
PORT = modules.PORT

clients = []

class ChatServerProtocol(asyncio.Protocol):
    """ Each instance of class represents a client and the socket
      connection to it. """

    def connection_made(self, transport):                                 # is called when new client connetc (same as socket.accept())
        """ Called on instantiation, when new client connects """
        self.transport = transport                                        # asyncio transport object used fo writing data to the socket
        self.addr = transport.get_extra_info('peername')
        self._rest = b''
        clients.append(self)
        print('Connection from {}'.format(self.addr))

    def data_received(self, data):                                        # is called when asyncio.Protocol receives data
        """ Handle data as it's received. Broadcast complete              # an equivalent of poll.poll() with POLLIN
        messages to all other clients """
        data = self._rest + data
        (msgs, rest) = modules.parse_recvd_data(data)
        self._rest = rest
        for msg in msgs:
            msg = msg.decode('utf-8')
            msg = '{}: {}'.format(self.addr, msg)
            print(msg)
            msg = modules.prep_msg(msg)
        for client in clients:
           client.transport.write(msg)  # <-- non-blocking              # where the data is sending. Submit data to event loop

    def connection_lost(self, ex):
       """ Called on client disconnect. Clean up client state """
       print('Client {} disconnected'.format(self.addr))
       clients.remove(self)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()                         # create a loop
    # Create server and initialize on the event loop
    coroutine = loop.create_server(ChatServerProtocol,      # Instantiate a object from class asyncio.Protocol
                                host=HOST,
                                port=PORT)
    server = loop.run_until_complete(coroutine)             # Run loop. Now clients are allowed to connect
    # print listening socket info
    for socket in server.sockets:                           # Just for printing. All real processing is under Class
        addr = socket.getsockname()
        print('Listening on {}'.format(addr))
    # Run the loop to process client connections
    loop.run_forever()                                      # Run forever
