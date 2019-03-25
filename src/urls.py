'''
Author: Thomas Theisen

Objective: Helper program to extract urls from the comment text

'''

#Python Modules
#-----------------------------------------------------------------------------#
import re

def extract_urls(comment):
    return re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', comment)


