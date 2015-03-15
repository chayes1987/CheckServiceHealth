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
        interval = config.get('Intervals', 'PUB_INTERVAL')
        time_out = config.get('Intervals', 'TIME_OUT')
        addresses = config.items('Addresses')
        services = config.items('Services')
        web_service_url = config.get('Web Service', 'URL')
        smtp_address = config.get('Email', 'SMTP_ADDRESS')
        smtp_port = config.get('Email', 'SMTP_PORT')
        username = config.get('Email', 'USERNAME')
        password = config.get('Email', 'PASSWORD')
        recipients = config.get('Email', 'RECIPIENTS')
        subject = config.get('Email', 'SUBJECT')
        message = config.get('Email', 'MESSAGE')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return pub_topic, sub_topic, addresses, pub_addr, interval, time_out, services, web_service_url, smtp_address, \
        smtp_port, username, password, recipients, subject, message


if __name__ == '__main__':
    conf = read_config()
    if None != conf:
        checker = CheckServiceHealth(conf[Config.SERVICES])
        checker.initialize_publisher(conf[Config.PUB_ADDRESS])
        print('Publisher initialized...')
        checker.initialize_subscriber(conf[Config.ADDRESSES], str(conf[Config.SUB_TOPIC]), int(conf[Config.TIME_OUT]),
                                      conf[Config.WEB_SERVICE_URL], conf[Config.SMTP_ADDRESS], conf[Config.SMTP_PORT],
                                      conf[Config.USERNAME], conf[Config.PASSWORD], conf[Config.RECIPIENTS],
                                      conf[Config.SUBJECT], conf[Config.MESSAGE])
        print('Subscriber initialized...')
        checker.initialize_scheduler(conf[Config.PUB_TOPIC], conf[Config.PUB_INTERVAL])