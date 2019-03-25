# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 12:21:23 2019

@author: ThomasTheisen
"""


import random
import operator
import bisect

begin = '__Begin__'
end = '__End__'

class generate():
    
    def __init__(self, order, combined = False, **parameters):
        self.order = order
        if('totalUpvotes' in parameters):
            self.totalUpvotes = parameters['totalUpvotes']
        if('res' in parameters):
            self.results = self.getDataFrame(parameters['res'])
        if combined:
            self.model = parameters['combinedModel']
            self.precompute_begin_state()
        else:
            self.text = self.toText()
            self.model = self.build()
            self.precompute_begin_state()
                
    def getDataFrame(self, res):
        textObj = Text.Text(results = res, order = self.order)
        return textObj.getResults()

    def getModel(self):
        return self.model

    def toText(self):
        self.results = self.results.reset_index(drop=True)
        cleanObj = Clean.Clean(self.results)
        self.results = cleanObj.clean()
        text = ""
        begin_state = '__Begin__ ' * self.order
        for row in self.results['comment']:
            text += begin_state + " " + row + " " + "__End__" + " "
        return text
    
    def word_split(self):
        return self.text.split()
        
    def accumulate(self, iterable, func = operator.add):
        it = iter(iterable)
        total = next(it)
        yield total
        for element in it:
            total = func(total, element)
            yield total

    def levelScore(self, l):
        return round(1/l,2)

    def threadScore(self, t):
        return round(1/t,2)

    def dynamicScore(self, l, t, u):
        return u / (l * t * self.totalUpvotes)

    def build(self):
        all_words =self.word_split()
        model = {}
        commentNum = 0
        for w in range(len(all_words) - self.order):
            state = tuple(all_words[w:w+self.order])
            follow = all_words[w+self.order]
            if follow == end and commentNum < self.results.shape[0] - 1:
                commentNum += 1
            if state not in model:
                model[state] = {}
            if follow not in model[state]:
                model[state][follow] = 0
            level = self.results.loc[commentNum, 'level']
            thread = self.results.loc[commentNum, 'thread']
            upvotes = self.results.loc[commentNum, 'upvotes']
            #score = self.dynamicScore(self.levelScore(level), self.threadScore(thread), upvotes)
            model[state][follow] += 1
        return model
    
    def precompute_begin_state(self):
        begin_state = tuple([begin] * self.order)
        choices, weights = zip(*self.model[begin_state].items())
        cumdist = list(self.accumulate(weights))
        self.begin_cumdist = cumdist
        self.begin_choices = choices
           
    def move(self, state):
        if state == tuple([begin] * self.order):
            choices = self.begin_choices
            cumdist = self.begin_cumdist
        else:
            choices, weights = zip(*self.model[state].items())
            cumdist = list(self.accumulate(weights))
        r = random.random() * cumdist[-1]
        selection = choices[bisect.bisect(cumdist,r)]
        return selection
     
    def gen(self, init_state = None):
        state = init_state or (begin,) * self.order
        sentence = ""
        while True:
            next_word = self.move(state)
            if next_word == end: break
            yield next_word
            state = state[1:] + (next_word,)
            sentence = sentence + " " +next_word
        return sentence
            
    def walk(self, init_state = None):
        return list(self.gen(init_state))
    
    def word_join(self, words):
        return " ".join(words)
    
    def make_sentence(self, init_state = None):
        prefix = []
        for _ in range(10):
            words = prefix + self.walk(init_state)
        return self.word_join(words)
