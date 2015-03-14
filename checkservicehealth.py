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
services = ['ScheduleAuction', 'StartAuction', 'NotifyBidders', 'RunAuction', 'InitializeAuctionUI',
            'UpdateBid', 'AnnounceResult']


class CheckServiceHealth:

    @staticmethod
    def parse_message(message, start_tag, end_tag):
        start_index = message.index(start_tag) + len(start_tag)
        substring = message[start_index:]
        end_index = substring.index(end_tag)
        return substring[:end_index]

    def initialize_subscriber(self, addresses, sub_topic, time_out):
        thread = threading.Thread(target=self.subscribe,
                                  kwargs={'addresses': addresses, 'sub_topic': str(sub_topic), 'time_out': time_out},
                                  name='subscribe')
        thread.daemon = True
        thread.start()

    def subscribe(self, addresses, sub_topic, time_out):
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
                                          kwargs={'time_out': time_out}, name='set_timeout')
                thread.daemon = True
                thread.start()

    @staticmethod
    def notify():
        username = 'online.dutch.auctions@gmail.com'
        password = 'online.auctions'
        recipients = ['ch1987@live.ie']
        subject = 'Service failure...'
        msg = 'Oh No! The following services are not responding:\n'
        list_services = '\n'.join(set(services) - set(received_services))
        body = msg + '\n' + list_services

        message = '''\From: %s\nTo: %s\nSubject: %s\n\n%s
            ''' % (username, ', '.join(recipients), subject, body)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
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

    def set_timeout(self, time_out):
        self.test_webservice()
        time.sleep(time_out)
        if len(received_services) < len(services):
            self.notify()
        else:
            print('All Ok...')
        received_services[:] = []
        return

    @staticmethod
    def test_webservice():
        try:
            response = requests.get('http://54.171.120.118:8080/placebidservice/bidder/services/checkservice')
            if not 'true' == response.content:
                received_services.append('PlaceBid')
        except:
            received_services.append('PlaceBid')
            pass