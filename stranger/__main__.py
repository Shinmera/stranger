from .client import Client

def main(token=None, config=None):
    client = Client(config)
    client.run(token)

if __name__ == '__main__':
    main(*sys.argv[1:])
