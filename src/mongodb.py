'''
Author: Thomas Theisen

Objective: Provide all functionality related to the use of mongodb for post information storage,
           updating the number of upvotes and comments throughout time, and determining when posts
           are mature i.e. when the comment data can be scraped. 
'''


#Python Modules
#-----------------------------------------------------------------------------#
import praw

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, InvalidDocument

#Internal Modules
#-----------------------------------------------------------------------------#
import credentials
import pollingproducer

client_id = credentials.configuration['RedditCredentials']['CLIENTID']
client_secret = credentials.configuration['RedditCredentials']['CLIENTSECRET']
user_agent = credentials.configuration['RedditCredentials']['USERAGENT']

class MongoDB:

    def __init__(self, db, coll, topic):
        client = MongoClient('localhost', 27017)
        self.database = client[db]
        self.collection = self.database[coll]
        self.topic = topic
        self.reddit = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent)

    def insert_into_collection(self, postid, subreddit, title, author, timeposted, num_upvotes, num_comments):
        try:
            post = {"_id": postid,
                "subreddit": str(subreddit),
                "title": str(title),
                "author": str(author),
                "timeposted": str(timeposted),
                "archived": 'false',
                "num_upvotes": [str(num_upvotes)],
                "num_comments": [str(num_comments)]
            }
            self.collection.insert_one(post)
        except InvalidDocument:
                n = {}
                for k, v in post.items():
                    if isinstance(k, unicode):
                        for i in ['utf-8', 'iso-8859-1']:
                            try:
                                k = k.encode(i)
                            except (UnicodeEncodeError, UnicodeDecodeError):
                                continue
                    if isinstance(v, np.int64):
                        self.info("k is %s , v is %s" % (k, v))
                        v = int(v)
                        self.info("V is %s" % v)
                    if isinstance(v, unicode):
                        for i in ['utf-8', 'iso-8859-1']:
                            try:
                                v = v.encode(i)
                            except (UnicodeEncodeError, UnicodeDecodeError):
                                continue
                    n[k] = v
                    self.collection.insert_one(n)
        except DuplicateKeyError:
            print('Attempted to post duplicate key')

    def update_comments_in_collection(self, postid, comments):
        self.collection.find_one_and_update({'_id': postid}, {'$push': {'num_comments': comments}})

    def update_upvotes_in_collection(self, postid, votes):
        self.collection.find_one_and_update({'_id': postid}, {'$push': {'num_upvotes': votes}})

    def set_document_as_archived(self, id):
        self.collection.update_one({'_id': id}, {'$set': {"archived": 'true'}})

    def return_all_non_archived(self):
        non_arc = []
        for doc in self.collection.find({"archived": "false"}):
            non_arc.append(doc)
        return non_arc

    def get_updated_post_counts(self, postid):
        submission = self.reddit.submission(id = postid)
        return str(submission.score), str(submission.num_comments)

    def maturity(self, arr):
        obs = len(arr)
        int_arr = list(map(int, arr))
        if obs >= 3:
            # first_diff = [j-i for i,j in zip(int_arr[:-1], int_arr[1:])]
            # second_diff = [j-i for i,j in zip(first_diff[:-1], first_diff[1:])]
            # if second_diff[-1] < 0:
            return True
        return False

    def pull_updated_post_data(self):
        print('Updating Post Metrics')
        non_arc = self.return_all_non_archived()
        for index, doc in enumerate(non_arc):
            postid = doc['_id']
            u_votes, u_comments = self.get_updated_post_counts(postid)
            self.update_upvotes_in_collection(postid, u_votes)
            self.update_comments_in_collection(postid, u_comments)
            
    def check_post_maturity(self):
        self.pull_updated_post_data()
        print('Checking Post Maturity')
        non_arc = self.return_all_non_archived()
        for index, doc in enumerate(non_arc):
            arr = doc['num_comments']
            mature = self.maturity(arr)
            if mature:
                postid = doc['_id']
                self.set_document_as_archived(postid)
                pollingproducer.send_message(self.topic, postid)
                print('Archived Post {} and Sent to Consumer'.format(postid))
        
    def return_all_documents(self):
        cursor = self.collection
        for doc in cursor.find():
            print(doc)

    def return_post_author(self, postid):
        record =  self.collection.find({"_id": postid})    #Returns memory address
        return list(record)[0]['author']

    def drop_collection(self):
        self.collection.drop()













