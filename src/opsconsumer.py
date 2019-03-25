'''
Author: Thomas Theisen

Objective: Receive individual comments from opsproducer.py for a given post and perform the following
           operations: extract keywords, extract links, and extract associations. Each extraction operation
           refines the data in order to be graphed in Neo4j.  

'''

#Python Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaConsumer
from prawcore import exceptions
import json
import sys

#Interal Modules
#-----------------------------------------------------------------------------#
import selection
import scrape
import keywords
import time
import associations
# import urls

# subject = sys.argv[1]
# s, k, db, coll, topic, table = selectsubject.selection(subject)

consumer = KafkaConsumer('ops-healthcare', value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest')

counter = {}
connections = {}

def extract(message):
    return message.value 

print('Consumer is waiting to receive comment data')
for id in consumer:
    print('received another row')
    try:
        data = extract(id)
        counter = keywords.insertion(counter, data['postid'], data['comment'])
        connections = associations.insertion(connections, data['postid'], data['parent'], data['child'], data['author'])
    except KeyboardInterrupt:
        break



