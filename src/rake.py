# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 12:21:02 2019

@author: ThomasTheisen
"""

import io
import re
import operator


class keywords(object):

    def __init__(self, regex=r'[\W\n]+'):
        self.stop_words =  "C:/Users/Thomas_Theisen/Documents/Reddit/RedditProjectFiles/STOPWORDS.txt"
        if isinstance(self.stop_words, list):
            self.__stop_words_pattern = self.build_stop_word_regex(self.stop_words)
        else:
            self.__stop_words_pattern = self.build_stop_word_regex(self.load_stop_words(self.stop_words, regex))
            
    def is_number(self, s):
        try:
            float(s) if '.' in s else int(s)
            return True
        except ValueError:
            return False
    
    def load_stop_words(self, stop_word_file, regex):
        with io.open(stop_word_file, encoding='utf8') as stop_word_file:
            stop_words = re.split(regex, stop_word_file.read())
        return [word for word in stop_words if word not in ('', ' ')]  # filters empty string matches
    
    
    def separate_words(self, text):
        splitter = re.compile(r'(?u)\W+')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            # leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
            if current_word != '' and not self.is_number(current_word):
                words.append(current_word)
        return words
    
    
    def split_sentences(self, text):
        sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sentences = sentence_delimiters.split(text)
        return sentences
    
    
    def build_stop_word_regex(self, stop_word_list):
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = r'\b' + word + r'(?![\w-])'
            stop_word_regex_list.append(word_regex)
        return re.compile('(?u)' + '|'.join(stop_word_regex_list), re.IGNORECASE)
    
    
    def generate_candidate_keywords(self, sentence_list, stop_word_pattern, minCharacters, maxWords):
        phrase_list = []
        for s in sentence_list:
            tmp = re.sub(stop_word_pattern, '|', s.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != '' and len(phrase) >= minCharacters and len(phrase.split()) <= maxWords:
                    phrase_list.append(phrase)
        return phrase_list
    
    def calculate_word_scores(self, phraseList):
        word_frequency = {}
        word_degree = {}
        for phrase in phraseList:
            word_list = self.separate_words(phrase)
            word_list_length = len(word_list)
            word_list_degree = word_list_length - 1
            for word in word_list:
                word_frequency.setdefault(word, 0)
                word_frequency[word] += 1
                word_degree.setdefault(word, 0)
                word_degree[word] += word_list_degree
        for item in word_frequency:
            word_degree[item] = word_degree[item] + word_frequency[item]
    
        word_score = {}
        for item in word_frequency:
            word_score.setdefault(item, 0)
            word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)
        return word_score
    
    def generate_candidate_keyword_scores(self, phrase_list, word_score, minFrequency):
        keyword_candidates = {}
        for phrase in phrase_list:
            if phrase_list.count(phrase) >= minFrequency:
                keyword_candidates.setdefault(phrase, 0)
                word_list = self.separate_words(phrase)
                candidate_score = 0
                for word in word_list:
                    candidate_score += word_score[word]
                keyword_candidates[phrase] = candidate_score
        return keyword_candidates

    def run(self, text, minCharacters=1, maxWords=5, minFrequency=1):
        sentence_list = self.split_sentences(text)

        phrase_list = self.generate_candidate_keywords(sentence_list, self.__stop_words_pattern, minCharacters, maxWords)

        word_scores = self.calculate_word_scores(phrase_list)

        keyword_candidates = self.generate_candidate_keyword_scores(phrase_list, word_scores, minFrequency)

        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_keywords
