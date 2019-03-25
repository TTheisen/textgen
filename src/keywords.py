'''
Author: Thomas Theisen

Objective: As comments are extracted from a given post, this program determines the keywords
           based on all comment data from a given post. 

'''

#Python Modules
#-----------------------------------------------------------------------------#
from kafka import KafkaProducer
from collections import Counter
import pickle

#Interal Modules
#-----------------------------------------------------------------------------#
import clean

producer = KafkaProducer(bootstrap_servers = ['localhost:9092'])
       
def insertion(counter, postid, message):
    
    clean_message = clean.clean(message)
    tokens =clean.tokenize(clean_message)
    keywords = clean.remove_stopwords(tokens)
        
    if not bool(counter):
        current_postid = None
    else:
        current_postid = next(iter(counter)) 
        
    if keywords:
    
        if postid != current_postid and not bool(counter):
            counter[postid] = {}
                    
        elif postid != current_postid and bool(counter):
            ranked = rank(counter, current_postid)
            print(ranked)
            ranked_bytes = serialize(ranked)
            send_keywords(ranked_bytes)
            deletion(counter, current_postid)
            counter[postid] = {}
            
        for word in keywords:
            if word not in counter[postid]:
                counter[postid][word] = 1
            else:
                counter[postid][word] += 1
                    
    return counter
                
def deletion(counter, postid):
    return counter.pop(postid)

def rank(counter, postid):
    d = {}
    inner = counter[postid]
    c = Counter(inner)
    mc = c.most_common(10)
    d[str(postid)] = dict(mc)
    return d

def serialize(data):
    return pickle.dumps(data)
    
def send_keywords(data):
    producer.send('keywords', data)
    producer.flush()