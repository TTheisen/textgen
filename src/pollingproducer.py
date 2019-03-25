'''
Author: Thomas Theisen

Objective: Helper program to send messages (postids) to be scraped when a post is mature

'''

#Python Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaConsumer, KafkaProducer
import json

producer = KafkaProducer(value_serializer = lambda v: json.dumps(v).encode('utf-8'),
                         bootstrap_servers = ['localhost:9092'])

#Send message to scrape
def send_message(topic, postid):
    producer.send(topic, {'postid': postid})
    producer.flush()
