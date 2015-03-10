__author__ = 'Conor'

# The official documentation was consulted for all 3rd party libraries used
# ZeroMQ -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html

import zmq
import threading

publisher = None
context = zmq.Context()


class CheckServiceHealth:

    @staticmethod
    def parse_message(message, start_tag, end_tag):
        start_index = message.index(start_tag) + len(start_tag)
        substring = message[start_index:]
        end_index = substring.index(end_tag)
        return substring[:end_index]

    def initialize_subscriber(self, addresses, sub_topic):
        thread = threading.Thread(target=self.subscribe,
                                  kwargs={'addresses': addresses, 'sub_topic': str(sub_topic)},
                                  name='subscribe')
        thread.daemon = True
        thread.start()

    @staticmethod
    def subscribe(addrs, topic):
        subscriber = context.socket(zmq.SUB)

        for key, address in addrs:
            subscriber.connect(address)

        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(topic))
        print('SUB: Heartbeats...')

        while True:
            print('REC: ' + subscriber.recv().decode())

    @staticmethod
    def initialize_publisher(pub_addr):
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(pub_addr)