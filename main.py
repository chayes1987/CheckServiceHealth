__author__ = 'Conor'

# Config file -> https://docs.python.org/2/library/configparser.html

from configparser import ConfigParser, Error
from checkservicehealth import CheckServiceHealth
from config import Config


def read_config():
    config = ConfigParser()
    try:
        config.read_file(open('config.ini'))
        sub_topic = config.get('Topics', 'SUB_TOPIC')
        pub_topic = config.get('Topics', 'PUB_TOPIC')
        pub_addr = config.get('Pub Address', 'PUB_ADDR')
        addresses = config.items('Addresses')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return sub_topic, pub_topic, addresses, pub_addr


if __name__ == '__main__':
    configuration = read_config()
    if None != configuration:
        checker = CheckServiceHealth()
        checker.initialize_publisher(configuration[Config.PUB_ADDRESS])
        checker.initialize_subscriber(configuration[Config.ADDRESSES],
                                                   configuration[Config.SUB_TOPIC])