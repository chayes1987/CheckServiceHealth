__author__ = 'Conor'

# The official documentation was consulted for all three 3rd party libraries used
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples

from apscheduler.schedulers.background import BlockingScheduler
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
    def subscribe(addresses, sub_topic):
        subscriber = context.socket(zmq.SUB)

        for key, address in addresses:
            subscriber.connect(address)

        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(sub_topic))
        print('SUB: Heartbeats...')

        while True:
            print('REC: ' + subscriber.recv().decode())

    @staticmethod
    def initialize_publisher(pub_addr):
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(pub_addr)

    def initialize_scheduler(self, topic, interval):
        scheduler = BlockingScheduler()
        print('Scheduler initialized...')
        self.schedule_jobs(scheduler, topic, int(interval))
        print('Scheduler Running...')

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

    def schedule_jobs(self, sched, topic, interval):
        sched.add_job(self.publish_check_service_health_command,
                      'interval', minutes=interval, args=topic)
