import json
import socket
from multiprocessing import Pipe
from threading import Thread

# TARGET_IPS = ["192.168.0.17"]
TARGET_IPS = ["172.31.22.59", "172.31.31.101", "172.32.0.13", "172.33.0.4"]
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# UDP Broadcast of MarketData
class MarketDataPublisher:

    def __init__(self, verbose):
        print("Initialising Market Data Publisher")
        print("Target IPs: " + str(TARGET_IPS))
        self.c1_r, self.c1_w = Pipe(duplex=False)

        self.verbose = verbose
        Thread(target=self.__broadcast).start()

    def broadcast(self, lob):
        self.c1_w.send(lob)

    def __broadcast(self):
        print("Start Broadcaster...")

        while True:
            lob = self.c1_r.recv()
            message = json.dumps(lob)

            try:
                # Send data to tall target ips by unicast
                print('MARKET UPDATE "%s"' % message)
                for IP in TARGET_IPS:
                    sock.sendto(
                        message.encode('utf-8'),
                        (IP, UDP_PORT)
                    )
            except socket.timeout:
                print("socket timeout")
