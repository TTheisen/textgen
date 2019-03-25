'''
Author: Thomas Theisen

Objective: Helper program to clean, tokenize, or remove stopwords from the comment text.

'''

#Python Modules
#-----------------------------------------------------------------------------#
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re 
import string
  
stopwords = set(stopwords.words('english'))

def to_lower_case(message):
    return message.lower()

def remove_URLS(message):
    return re.sub(r'http\S+', '', message)

def remove_numbers(message):
    return ''.join([i for i in message if not i.isdigit()])

def remove_commas(message):
    return message.replace(",","")

def remove_apostrophes(message):
    return message.replace("'","")

def remove_emojis(comment):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', comment)

def tokenize(message):
    return word_tokenize(message)

def remove_stopwords(tokens):
    return [word for word in tokens if word not in stopwords]
    
def clean(message):
    message = to_lower_case(message)
    message = remove_numbers(message)
    message = remove_URLS(message)
    message = remove_commas(message)
    message = remove_apostrophes(message)
    message = remove_emojis(message)
    return message.translate(str.maketrans('', '', string.punctuation))
