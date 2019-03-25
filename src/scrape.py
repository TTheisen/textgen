'''
Author: Thomas Theisen

Objective: This program receives a postid through the pollingconsumer and recursively extracts 
           every comment from the post. The information extracted from every comment includes
           the postid, parent, child, author, comment, level, thread, and upvotes. The parent
           is the id of the comment the current comment is responding to. Child is the current
           comments id. Level and thread are hierarchical indicators of where the comment is 
           located. Instead of extracting all the data and then moving it to a database, each
           comment is sent through another producer/consumer to have operations/transformations
           performed on its data.
'''


#Python Modules
#-----------------------------------------------------------------------------#
import praw
import pandas as pd
from datetime import datetime
import time
import re

#Interal Modules
#-----------------------------------------------------------------------------#
import credentials
import opsproducer

client_id = credentials.configuration['RedditCredentials']['CLIENTID']
client_secret = credentials.configuration['RedditCredentials']['CLIENTSECRET']
user_agent = credentials.configuration['RedditCredentials']['USERAGENT']


#Message Struct: {postid, parent, child, author, comment, level, thread, upvotes}

def getSubComments(postid, comment, level, thread):
    if type(comment).__name__ == "Comment":
        replies = comment.replies                               #Get replies of comment
        level += 1
    elif type(comment).__name__ == "MoreComments":
        replies = comment.comment()                             #Get more comments at the same level
        level -= 1
    for child in replies:
        # print(postid, str(comment.parent()), str(comment.id), str(comment.author), str(comment.body), level, thread, comment.score)
        opsproducer.send_message('ops-healthcare', postid, str(comment.parent()), str(comment.id), str(comment.author), \
                                    str(comment.body), level, thread, comment.score)
        print('sent a message')
        getSubComments(postid, child, level, thread)            #Recursively find all comments

def getAllComments(submission): 
    comments = submission.comments
    submission.comments.replace_more(limit=0)
    postid = submission.id
    thread = 0
    for comment in comments:
        thread += 1
        level = 1
        # print(postid, str(comment.parent()), str(comment.id), str(comment.author), str(comment.body), level, thread, comment.score)
        opsproducer.send_message('ops-healthcare', postid, str(comment.parent()), str(comment.id), str(comment.author), \
                                    str(comment.body), level, thread, comment.score)
        print('sent a message')
        getSubComments(postid, comment, level, thread)

def fetch(submissionID):    
    try:
        reddit = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent)
        submission = reddit.submission(id = submissionID)
        getAllComments(submission) 
        print('Finished scraping comments from submission {}'.format(submissionID))
    except: 
        print('Something failed')
        


