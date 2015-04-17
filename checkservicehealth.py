__author__ = 'Conor'

# The official documentation was consulted for all three 3rd party libraries used
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples
# REST -> http://stackoverflow.com/questions/18865666/how-to-query-a-restful-webservice-using-python

from apscheduler.schedulers.background import BlockingScheduler
import zmq
import time
import threading
import requests

publisher = None
context = zmq.Context()
received_service_names = []
expected_service_names = []
my_firebase = None


class CheckServiceHealth:

    def __init__(self, list_services, firebase):
        global expected_service_names
        # Set list of service names that are expected to reply
        for key, service in list_services:
            expected_service_names.append(service)
        global my_firebase
        my_firebase = firebase

    @staticmethod
    def parse_message(message, start_tag, end_tag):
        start_index = message.index(start_tag) + len(start_tag)
        substring = message[start_index:]
        end_index = substring.index(end_tag)
        return substring[:end_index]

    def initialize_subscriber(self, addresses, sub_topic, time_out, web_service_url):
        thread = threading.Thread(target=self.subscribe,
                                  kwargs={'addresses': addresses, 'sub_topic': str(sub_topic), 'time_out': time_out,
                                          'web_service_url': web_service_url}, name='subscribe')
        thread.daemon = True
        thread.start()

    def subscribe(self, addresses, sub_topic, time_out, web_service_url):
        subscriber = context.socket(zmq.SUB)

        for key, address in addresses:
            subscriber.connect(address)

        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(sub_topic))
        print('SUB: ' + sub_topic)

        while True:
            message = subscriber.recv().decode()
            print('REC: ' + message)
            service = self.parse_message(message, '<params>', '</params>')
            received_service_names.append(service)

            # When the first service replies, set a timeout for the rest
            if 1 == len(received_service_names):
                thread = threading.Thread(target=self.set_timeout,
                                          kwargs={'time_out': time_out, 'web_service_url': web_service_url},
                                          name='set_timeout')
                thread.daemon = True
                thread.start()

    @staticmethod
    def update_dashboard():
        if len(received_service_names) < len(expected_service_names):
            list_services = ' '.join(set(expected_service_names) - set(received_service_names))
            print('Potential issue, dashboard alerted...')
        else:
            list_services = ''
            print('All Ok...')

        try:
            my_firebase.put('/dashboard', 'message', list_services)
        except:
            print('Notification failed...')

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

    def set_timeout(self, time_out, web_service_url):
        self.test_web_service(web_service_url)
        time.sleep(time_out)
        self.update_dashboard()
        received_service_names[:] = []
        return

    @staticmethod
    def test_web_service(web_service_url):
        try:
            response = requests.get(web_service_url)
            if not 'true' == response.content:
                raise Exception
        except:
            received_service_names.append('PlaceBid')
            pass