'''
Author: Thomas Theisen

Objective: Stream new posts from a selection of subreddits about a specific subject.
           The selection of subjects are focused on current controversial issues around the world.
           If a new post arrives that contains one or more pre-determined keywords, the post's 
           information is sent to be stored in a mongodb collection/table. 
'''


#Python Modules
#-----------------------------------------------------------------------------#
import praw
import pandas as pd
import numpy as np
import sys
import re
import time

print('Successfully imported python modules')
#-----------------------------------------------------------------------------#

#Interal Modules
#-----------------------------------------------------------------------------#
import credentials
import options
import mongodb
import selection

print('Successfully imported interal modules')
#-----------------------------------------------------------------------------#

#Reddit API Credentials
#-----------------------------------------------------------------------------#
client_id = credentials.configuration['RedditCredentials']['CLIENTID']
client_secret = credentials.configuration['RedditCredentials']['CLIENTSECRET']
user_agent = credentials.configuration['RedditCredentials']['USERAGENT']
#-----------------------------------------------------------------------------#


#Streaming Context
#-----------------------------------------------------------------------------#
subject = sys.argv[1]
s, k, db, coll, topic, table = selection.info(subject)
print('Successfully gathered streaming context parameters')
#-----------------------------------------------------------------------------#


#Streaming 
#-----------------------------------------------------------------------------#
def stream_submissions(*args):
	mongo = mongodb.MongoDB(db, coll, topic)
	reddit = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent)
	keywords = []
	subreddits = []

	if len(args[0]) > 3:
		raise Exception('Too Many Subreddits to Stream')

	for s in args[0]:
		subreddits.append(s)
	subreddits = "+".join(subreddits)

	for k in args[1]:
		keywords.append(k)

	try:
		while True:
			for submission in reddit.subreddit(subreddits).stream.submissions():
				print(submission.id)
				if re.compile("|".join(keywords), re.IGNORECASE).search(submission.title):
					print("Accepted Submission: {} From {}".format(submission.id, submission.subreddit))
					mongo.insert_into_collection(submission.id, 
					submission.subreddit, 
					submission.title, 
					submission.author,
					submission.created_utc, 
					submission.score, 
					submission.num_comments)
					time.sleep(1)
	except KeyboardInterrupt:
		pass

stream_submissions(s,k)
#-----------------------------------------------------------------------------#
