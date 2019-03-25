'''
Author: Thomas Theisen

Objective: Receive messages (postids) from the pollingproducer program and initiate the comment
           scraping process.

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

# subject = sys.argv[1]
# s, k, db, coll, topic, table = selectsubject.selection(subject)

consumer = KafkaConsumer('test-healthcare', value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='largest')

def extract_postid(message):
    kv = message.value
    values = kv.values()
    postid = list(values)[0]
    return postid

print('Consumer is waiting to receive postids')
for id in consumer:
    postid = extract_postid(id)
    try:
        scrape.fetch(postid)
    except exceptions.PrawcoreException:
        print('Failed to scrape comment data for post {}'.format(postid))       
    except KeyboardInterrupt:
        break