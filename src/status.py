'''
Author: Thomas Theisen

Objective: Every (n) units of time, the stored posts within the MongoDB collection are polled
           again through the API to append the current number of comments. Posts are considered 
           'mature' (an inflection point in the number of comments being posted) when the second
           derivative turns negative. Once a post is deemed mature, a Kafka producer sends the 
           post's postid to a Kafka consumer.
'''

#Python Modules
#-----------------------------------------------------------------------------#
import schedule
import sys

#Interal Modules
#-----------------------------------------------------------------------------#
import selection
import mongodb
import options

subject = sys.argv[1]
s, k, db, coll, topic, table = selection.info(subject)

def start_database_status_check(db, coll, topic):
    mongo = mongodb.MongoDB(db, coll, topic)
    schedule.every(10).seconds.do(mongo.check_post_maturity)
    while True:
        try:
            schedule.run_pending()
        except KeyboardInterrupt:
            break

#Status Checking Context
#-----------------------------------------------------------------------------#
print('Starting database status checker')
start_database_status_check(db, coll, topic)
#-----------------------------------------------------------------------------#
