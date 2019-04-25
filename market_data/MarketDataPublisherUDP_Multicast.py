import json
import socket
import struct
from multiprocessing import Pipe
from threading import Thread

# UDP GROUP IP
multicast_group = ('224.3.30.33', 10000)

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

    def __init__(self):
        print("Initialising Market Data Publisher")
        self.c1_r, self.c1_w = Pipe(duplex=False)

        Thread(target=self.__broadcast).start()

    def broadcast(self, lob):
        self.c1_w.send(lob)

    def __broadcast(self):
        print("Start Broadcaster...")

        while True:
            lob = self.c1_r.recv()
            message = json.dumps(lob)

            try:
                # Send data to the multicast group
                print('MARKET UPDATE "%s"' % message)
                sent = sock.sendto(message.encode('utf-8'), multicast_group)
                print('SEND %s' % sent)
            except socket.timeout:
                print("socket timeout")
