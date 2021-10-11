import socket
import selectors
import types


sel = selectors.DefaultSelector()


def accept_wrapper(sock: socket.socket):
    connectionSocket, addr = sock.accept()
    connectionSocket.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(connectionSocket, events, data=data)


def service_connection(key: selectors.SelectorKey, mask):
    connectionSocket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = connectionSocket.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print("closing connection to ", data.addr)
            sel.unregister(connectionSocket)
            connectionSocket.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("echoing", repr(data.outb), 'to', data.addr)
            sent = connectionSocket.send(data.outb)
            data.outb = data.outb[sent:]


serverName = "127.0.0.1"
serverPort = 9527
serverSocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName, serverPort))
serverSocket.listen()
print(f"Listening on {serverName}:{serverPort}")
# set to non-blocking so we can listen to the event without blocking
serverSocket.setblocking(False)
# listen on READ EVENT of serverSocket
sel.register(serverSocket, selectors.EVENT_READ, data=None)

# event loop
while True:
    # block until there are socket ready for I/O
    # events is a (key, events) tuples
    events = sel.select(timeout=None)
    print("events: ")
    # key is a SelectorKey (namedtuple)
    # ("key", "fileobj fd events data")
    for key, mask in events:
        if key.data is None: # It's from the listening socket and we need to accept()
            accept_wrapper(key.fileobj) # key.fileobj is a socket object
        else:  # key.data not None. This is a client socket already been accepted
            service_connection(key, mask) # mask is an event mask of operations that are ready
