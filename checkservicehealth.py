__author__ = 'Conor'

# The official documentation was consulted for all 3rd party libraries used
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples
# REST -> http://stackoverflow.com/questions/18865666/how-to-query-a-restful-webservice-using-python
# Coding Standards -> https://www.python.org/dev/peps/pep-0008/

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
    """
    This class is responsible for monitoring services health status

    Attributes:
      publisher (0mq publisher): A 0mq publisher.
      context (0mq context): A 0mq context.
      received_service_names (List of String): Services received.
      expected_service_names (List of String): Services expected.
      my_firebase (Firebase): The firebase reference URL.
    """

    def __init__(self, list_services, firebase):
        """
        Constructor
        :param list_services: Expected services to be received as per configuration
        :param firebase: The firebase reference URL
        :return: Nothing
        """
        global expected_service_names
        # Set list of service names that are expected to reply, loaded from configuration
        for key, service in list_services:
            expected_service_names.append(service)
        global my_firebase
        my_firebase = firebase

    @staticmethod
    def parse_message(message, start_tag, end_tag):
        """
        Parses received messages
        :param message: The message to parse
        :param start_tag: The starting delimiter
        :param end_tag: The ending delimiter
        :return: The required string
        """
        start_index = message.index(start_tag) + len(start_tag)
        substring = message[start_index:]
        end_index = substring.index(end_tag)
        return substring[:end_index]

    def initialize_subscriber(self, addresses, sub_topic, time_out, web_service_url):
        """
        Initialize the subscriber (separate thread)
        :param addresses: The addresses to connect to
        :param sub_topic: The topic to subscribe to
        :param time_out: The timeout period to wait for replies
        :param web_service_url: The URL of the web service
        :return: Nothing
        """
        thread = threading.Thread(target=self.subscribe,
                                  kwargs={'addresses': addresses, 'sub_topic': str(sub_topic), 'time_out': time_out,
                                          'web_service_url': web_service_url}, name='subscribe')
        thread.daemon = True
        thread.start()

    def subscribe(self, addresses, sub_topic, time_out, web_service_url):
        """
        Subscribes to responses
        :param addresses: The addresses to connect to
        :param sub_topic: The topic to subscribe to
        :param time_out: The timeout period to wait for replies
        :param web_service_url: The URL of the web service
        :return: Nothing
        """
        subscriber = context.socket(zmq.SUB)

        # Connect to all the addresses from the configuration file
        for key, address in addresses:
            subscriber.connect(address)

        # Set the topic - Ok
        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(sub_topic))
        print('SUB: ' + sub_topic)

        while True:
            message = subscriber.recv().decode()
            print('REC: ' + message)
            # Extract the fields from the message
            service = self.parse_message(message, '<params>', '</params>')
            # Append the received service name to the list
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
        """
        Updates the dashboard
        :return: Nothing
        """
        # If the lengths of the lists don't match then a service hasn't replied, otherwise all have replied
        if len(received_service_names) < len(expected_service_names):
            # Convert the lists to sets and subtract to get the difference
            list_services = ' '.join(set(expected_service_names) - set(received_service_names))
            print('Potential issue, dashboard alerted...')
        else:
            list_services = ''
            print('All Ok...')

        try:
            # Update Firebase
            my_firebase.put('/dashboard', 'message', list_services)
        except:
            print('Notification failed...')

    @staticmethod
    def initialize_publisher(pub_addr):
        """
        Initializes the publisher
        :param pub_addr: The address to bind to
        :return: Nothing
        """
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(pub_addr)

    def initialize_scheduler(self, topic, interval):
        """
        Initializes the scheduler
        :param topic: The topic to publish - CheckHeartbeat
        :param interval: How often to publish the check
        :return: Nothing
        """
        scheduler = BlockingScheduler()
        print('Scheduler initialized...')
        # Schedule the job to run, publish_check_service_health_command will run every 'interval' minutes
        scheduler.add_job(self.publish_check_service_health_command,
                          'interval', minutes=int(interval), args=[topic])

        # Start the scheduler running
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print('Scheduler Stopped...')
            pass

    @staticmethod
    def publish_check_service_health_command(topic):
        """
        Publishes the CheckHeart command
        :param topic: The topic to publish - CheckHeartbeat
        :return: Nothing
        """
        if None != publisher:
            publisher.send_string(topic)
            print('PUB: ' + topic)

    def set_timeout(self, time_out, web_service_url):
        """
        Sets the timeout to wait for all services to reply
        :param time_out: The length of time to wait
        :param web_service_url: The URL for the web service
        :return:
        """
        # Tests the web service
        self.test_web_service(web_service_url)
        # Wait for the allotted time
        time.sleep(time_out)
        # Update Firebase
        self.update_dashboard()
        # Reset the list to empty
        received_service_names[:] = []
        return

    @staticmethod
    def test_web_service(web_service_url):
        """
        Tests the web service to make sure it is working
        :param web_service_url: The URL of the web service
        :return: Nothing
        """
        try:
            response = requests.get(web_service_url)
            if not 'true' == response.content:
                raise Exception
        except:
            received_service_names.append('PlaceBid')
            pass