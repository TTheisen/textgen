'''
Author: Thomas Theisen

Objective: Receive serialized interactions between post/comment authors. Graph these interactions.  

'''

#Python Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaConsumer
import sys
import pickle

#Interal Modules
#-----------------------------------------------------------------------------#
import graphdb

consumer = KafkaConsumer('associations',
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest')

def deserializer(k_bytes):
    return pickle.loads(k_bytes.value)

print('Waiting to receive keywords')
for interaction_bytes in consumer:
    data = deserializer(interaction_bytes)
    postid, parent_author, child_author = data[0], data[1], data[2]
    graphdb.find_or_create_relationship_interaction(postid, (parent_author, child_author))



