import sys
import json
from .client import Client

def main(token=None, config=None):
    client = Client(config)
    client.run(token)

if __name__ == '__main__':
    init = {}
    with open('info.txt', 'r') as f:
        init = json.load(f)
    main(init["token"], init.get("config"))
