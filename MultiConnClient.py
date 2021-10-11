import socket
import selectors
import types


sel = selectors.DefaultSelector()
messages = [b"Message 1 from client", b"Message 2 from client"]


def start_connections(host, port, num_conns):
    pass
