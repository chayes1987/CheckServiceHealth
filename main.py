__author__ = 'Conor'

# Config file -> https://docs.python.org/2/library/configparser.html

from configparser import ConfigParser, Error


def read_config():
    config = ConfigParser()
    try:
        config.read_file(open('config.ini'))
        topic = config.get('Topics', 'TOPIC')
        addresses = config.items('Addresses')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return topic, addresses


if __name__ == '__main__':
    configuration = read_config()
    if None != configuration:
        print(configuration[0])
        print(configuration[1])