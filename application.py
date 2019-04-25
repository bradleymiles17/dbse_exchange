import argparse
import time

import quickfix as fix

from fix.FixApplication import FixApplication


def start_fix(file_name):
    try:
        settings = fix.SessionSettings(file_name)
        application = FixApplication()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        print('Creating FIX Acceptor')
        acceptor = fix.SocketAcceptor(application, storeFactory, settings, logFactory)

        print('Starting FIX Acceptor')
        acceptor.start()

        while 1:
            time.sleep(1)

        acceptor.stop()
    except (fix.ConfigError, fix.RuntimeError) as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FIX Server')
    parser.add_argument('file_name', type=str, help='Name of configuration file')
    args = parser.parse_args()
    start_fix(args.file_name)
