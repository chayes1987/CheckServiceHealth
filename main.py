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
        interval = config.get('Interval', 'INTERVAL')
        addresses = config.items('Addresses')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return sub_topic, pub_topic, addresses, pub_addr, interval


if __name__ == '__main__':
    conf = read_config()
    if None != conf:
        checker = CheckServiceHealth()
        checker.initialize_publisher(conf[Config.PUB_ADDRESS])
        print('Publisher initialized...')
        checker.initialize_subscriber(conf[Config.ADDRESSES], conf[Config.SUB_TOPIC])
        print('Subscriber initialized...')
        checker.initialize_scheduler(conf[Config.PUB_TOPIC], conf[Config.PUB_INTERVAL])