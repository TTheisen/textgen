'''
Author: Thomas Theisen

Objective: Test program for postgresdb.py functionality

'''

import mongodb
import options

db = options.mongodb_database_healthcare
coll = options.mongodb_collection_healthcare
mongo = mongodb.MongoDB(db, coll, 'topic')
print(mongo.return_post_author('b332ad'))