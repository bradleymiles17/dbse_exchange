import quickfix as fix
import time, sys, argparse

from FixApplication import FixApplication


def start_fix(file_name):
    try:
        settings = fix.SessionSettings(file_name)
        application = FixApplication()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        print('creating acceptor')
        acceptor = fix.SocketAcceptor(application, storeFactory, settings, logFactory)

        print('starting acceptor')
        acceptor.start()

        while 1:
            time.sleep(1)
    except (fix.ConfigError, fix.RuntimeError) as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FIX Server')
    parser.add_argument('file_name', type=str, help='Name of configuration file')
    args = parser.parse_args()
    start_fix(args.file_name)
