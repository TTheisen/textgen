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

def send_message(topic, postid, parent, child, author, comment, level, thread, upvotes):
    producer.send(topic, {'postid': postid, 'parent': parent, 'child': child, 'author': author, 
                            'comment': comment, 'level': level, 'thread': thread, 'upvotes': upvotes})
    producer.flush()