#Python Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaConsumer
from prawcore import exceptions
import json
import sys

#Interal Modules
#-----------------------------------------------------------------------------#

consumer = KafkaConsumer('links', value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='largest')

