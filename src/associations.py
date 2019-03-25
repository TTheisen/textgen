'''
Author: Thomas Theisen

Objective: Aggregate interactions between users. Either post author to comment author or comment author to 
           comment author. This information will be used to personalize responses/replies to maximize the 
           propensity for a user to reply back. 

'''

# Python Modules
#-----------------------------------------------------------------------------#
import pickle

# Interal Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaProducer
import mongodb
import options

db = options.mongodb_database_healthcare
coll = options.mongodb_collection_healthcare
producer = KafkaProducer(bootstrap_servers = ['localhost:9092'])

mongo = mongodb.MongoDB(db, coll, None)

def insertion(connections, postid, parent, child, child_author):

    if not bool(connections):
        current_postid = None
    else:
        current_postid = next(iter(connections)) 

    if not bool(connections): 
        print('New Post Incoming')
        post_author = mongo.return_post_author(postid)

        #Create pointer between id and author
        connections[postid] = {}
        connections[postid][parent] = post_author
        connections[postid][child] = child_author

    elif bool(connections) and current_postid == postid:
        print('Receiving Data from the same post')
        connections[postid][child] = child_author

    elif bool(connections) and current_postid != postid: #Moving onto next post
        print('Moving onto next post')
        deletion(connections, current_postid)
        post_author = mongo.return_post_author(postid)

        #Create pointer between id and author
        connections[postid] = {}
        connections[postid][parent] = post_author
        connections[postid][child] = child_author

    #Send interaction
    inner = connections[postid]
    parent_author = inner.get(parent)
    # print('sent   postid: {},     parent_author: {},    child_author: {}'.format(postid, parent_author, child_author))
    send_associations(postid, parent_author, child_author)
    print('sent interaction')

    return connections

def send_associations(postid, author1, author2): #Send the users that interacted and on what post
    interaction = (postid, author1, author2)
    interaction_bytes = serialize(interaction)
    producer.send('associations', interaction_bytes)
    producer.flush()

def serialize(data):
    return pickle.dumps(data)
        
def deletion(connections, postid):
    return connections.pop(postid)

