__author__ = 'Conor'

# The official documentation was consulted for all three 3rd party libraries used
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples
# SMTP -> http://stackoverflow.com/questions/10147455/trying-to-send-email-gmail-as-mail-provider-using-python
# REST -> http://stackoverflow.com/questions/18865666/how-to-query-a-restful-webservice-using-python

from apscheduler.schedulers.background import BlockingScheduler
import zmq
import smtplib
import time
import threading
import requests

publisher = None
context = zmq.Context()
received_services = []
services = []


class CheckServiceHealth:

    def __init__(self, list_services):
        global services
        for key, service in list_services:
            services.append(service)

    @staticmethod
    def parse_message(message, start_tag, end_tag):
        start_index = message.index(start_tag) + len(start_tag)
        substring = message[start_index:]
        end_index = substring.index(end_tag)
        return substring[:end_index]

    def initialize_subscriber(self, addresses, sub_topic, time_out, web_service_url, smtp_address, smtp_port, username,
                              password, recipients, subject, msg):
        thread = threading.Thread(target=self.subscribe,
                                  kwargs={'addresses': addresses, 'sub_topic': str(sub_topic), 'time_out': time_out,
                                          'web_service_url': web_service_url, 'smtp_address': smtp_address,
                                          'smtp_port': smtp_port, 'username': username, 'password': password,
                                          'recipients': recipients, 'subject': subject, 'msg': msg}, name='subscribe')
        thread.daemon = True
        thread.start()

    def subscribe(self, addresses, sub_topic, time_out, web_service_url, smtp_address, smtp_port, username, password,
                  recipients, subject, msg):
        subscriber = context.socket(zmq.SUB)

        for key, address in addresses:
            subscriber.connect(address)

        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(sub_topic))
        print('SUB: ' + sub_topic)

        while True:
            message = subscriber.recv().decode()
            print('REC: ' + message)
            service = self.parse_message(message, '<params>', '</params>')
            received_services.append(service)

            if 1 == len(received_services):
                thread = threading.Thread(target=self.set_timeout,
                                          kwargs={'time_out': time_out, 'web_service_url': web_service_url,
                                                  'smtp_address': smtp_address, 'smtp_port': smtp_port,
                                                  'username': username, 'password': password, 'recipients': recipients,
                                                  'subject': subject, 'msg': msg}, name='set_timeout')
                thread.daemon = True
                thread.start()

    @staticmethod
    def notify(smtp_address, smtp_port, username, password, recipients, subject, msg):
        m = msg + '\n'
        list_services = '\n'.join(set(services) - set(received_services))
        body = m + '\n' + list_services
        message = '''\From: %s\nTo: %s\nSubject: %s\n\n%s
            ''' % (username, ', '.join(recipients), subject, body)

        try:
            server = smtplib.SMTP(smtp_address, smtp_port)
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(username, recipients, message)
            server.close()
            print('Message Sent...')
        except:
            print('Sending failed...')

    @staticmethod
    def initialize_publisher(pub_addr):
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(pub_addr)

    def initialize_scheduler(self, topic, interval):
        scheduler = BlockingScheduler()
        print('Scheduler initialized...')
        scheduler.add_job(self.publish_check_service_health_command,
                          'interval', minutes=int(interval), args=[topic])

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print('Scheduler Stopped...')
            pass

    @staticmethod
    def publish_check_service_health_command(topic):
        if None != publisher:
            publisher.send_string(topic)
            print('PUB: ' + topic)

    def set_timeout(self, time_out, web_service_url, smtp_address, smtp_port, username, password,
                    recipients, subject, msg):
        self.test_web_service(web_service_url)
        time.sleep(time_out)
        if len(received_services) < len(services):
            self.notify(smtp_address, int(smtp_port), username, password, recipients, subject, msg)
        else:
            print('All Ok...')
        received_services[:] = []
        return

    @staticmethod
    def test_web_service(web_service_url):
        try:
            response = requests.get(web_service_url)
            if not 'true' == response.content:
                raise Exception
        except:
            received_services.append('PlaceBid')
            pass