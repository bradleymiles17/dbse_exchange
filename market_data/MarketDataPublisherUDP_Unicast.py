import socket, struct, json
from multiprocessing import Pipe
from threading import Thread

# TARGET_IPS = ["192.168.0.17"]
TARGET_IPS = ["172.31.19.249", "172.31.16.218", "172.32.12.58"]
UDP_PORT = 5005


# UDP Broadcast of MarketData
class MarketDataPublisher:

    def __init__(self, verbose):
        print("Initialising Market Data Publisher")
        self.c1_r, self.c1_w = Pipe(duplex=False)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
                    self.sock.sendto(
                        message.encode('utf-8'),
                        (IP, UDP_PORT)
                    )
            except socket.timeout:
                print("socket timeout")
