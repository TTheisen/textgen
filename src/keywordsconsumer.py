'''
Author: Thomas Theisen

Objective: Receive serialized keywords and deserialize. Add postid and corresponding keywords to graph. 

'''

#Python Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaConsumer
import sys
import pickle

#Interal Modules
#-----------------------------------------------------------------------------#
import graphdb

consumer = KafkaConsumer('keywords',
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest')

def deserializer(k_bytes):
    return pickle.loads(k_bytes.value)

print('Waiting to receive keywords')
for keyword_bytes in consumer:
    data = deserializer(keyword_bytes)
    postid = next(iter(data.keys()))
    keywords = data[postid]
    graphdb.find_or_create_relationship_keywords(postid, keywords)


