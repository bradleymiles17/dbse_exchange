import socket, struct, json
from multiprocessing import Pipe
from threading import Thread

# UDP GROUP IP
multicast_group = ('224.3.29.71', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(0.2)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


# UDP Broadcast of MarketData
class MarketDataPublisher:

    c1_r, c1_w = Pipe(duplex=False)

    def __init__(self):
        print("Initialising Market Data Publisher")
        Thread(target=self.broadcast).start()

    def add_lob_update_event(self, lob):
        self.c1_w.send(lob)

    def broadcast(self):
        print("Start Broadcaster...")

        while True:
            lob = self.c1_r.recv()
            message = json.dumps(lob)

            try:
                # Send data to the multicast group
                print('MARKET UPDATE "%s"' % message)
                sent = sock.sendto(message.encode('utf-8'), multicast_group)
            except socket.timeout:
                print("socket timeout")

