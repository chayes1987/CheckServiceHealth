__author__ = 'Conor'

# Firebase -> https://pypi.python.org/pypi/python-firebase/1.2
# Config file -> https://docs.python.org/2/library/configparser.html
# Coding Standards -> https://www.python.org/dev/peps/pep-0008/

from configparser import ConfigParser, Error
from checkservicehealth import CheckServiceHealth
from firebase import firebase
from config import Config


def read_config():
    """
    Reads the configuration file
    :return: A tuple with the entries from the file, None if exception
    """
    config = ConfigParser()
    try:
        # Open the file and extract the contents
        config.read_file(open('config.ini'))
        sub_topic = config.get('Topics', 'SUB_TOPIC')
        pub_topic = config.get('Topics', 'PUB_TOPIC')
        pub_addr = config.get('Pub Address', 'PUB_ADDR')
        interval = config.get('Intervals', 'PUB_INTERVAL')
        time_out = config.get('Intervals', 'TIME_OUT')
        addresses = config.items('Addresses')
        services = config.items('Services')
        web_service_url = config.get('Web Service', 'URL')
        firebase_url = config.get('Firebase', 'FIREBASE_URL')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return pub_topic, sub_topic, addresses, pub_addr, interval, time_out, services, web_service_url, firebase_url


if __name__ == '__main__':
    conf = read_config()
    # Check configuration
    if None != conf:
        my_firebase = firebase.FirebaseApplication(conf[Config.FIREBASE_URL], authentication=None)
        checker = CheckServiceHealth(conf[Config.SERVICES], my_firebase)
        checker.initialize_publisher(conf[Config.PUB_ADDRESS])
        print('Publisher initialized...')
        checker.initialize_subscriber(conf[Config.ADDRESSES], str(conf[Config.SUB_TOPIC]), int(conf[Config.TIME_OUT]),
                                      conf[Config.WEB_SERVICE_URL])
        print('Subscriber initialized...')
        checker.initialize_scheduler(conf[Config.PUB_TOPIC], conf[Config.PUB_INTERVAL])