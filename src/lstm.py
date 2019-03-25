# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 12:22:06 2019

@author: ThomasTheisen
"""

from __future__ import print_function

import numpy
import gensim
import string

from keras.callbacks import LambdaCallback
from keras.layers.recurrent import LSTM
from keras.layers.embeddings import Embedding
from keras.layers import Dense, Activation
from keras.models import Sequential

class model():

    def __init__(self, threads, max_sentence_length):
        self.max_sentence_len = max_sentence_length
        self.sentences = self.create_sentences(threads)
        self.train_x = self.create_training_set()
        self.train_y = self.create_testing_set()
        self.word_model = self.train_word2_vec()[0]
        self.embedding_weights = self.train_word2_vec()[1]
        self.vocab_size = self.train_word2_vec()[2]
        self.embedding_size = self.train_word2_vec()[3]
        self.model = self.define_model()
        self.on_epoch_end = None

    def create_sentences(self, threads):
        sentences = [threads.split()[word:word+self.max_sentence_len] for word in range(0, len(threads.split()), self.max_sentence_len)]
        if len(sentences[-1]) != self.max_sentence_len:
            del sentences[-1]
        return sentences

    def word2idx(self, word):
        return self.word_model.wv.vocab[word].index

    def idx2word(self, idx):
        return self.word_model.wv.index2word[idx]

    def create_training_set(self):
        return numpy.zeros([len(self.sentences), self.max_sentence_len], dtype=numpy.int32)

    def get_training_set_x(self):
        return self.train_x

    def get_training_set_y(self):
        return self.train_y

    def create_testing_set(self): 
        return numpy.zeros([len(self.sentences)], dtype=numpy.int32)

    def train_word2_vec(self):
        word_model = gensim.models.Word2Vec(self.sentences, size=100, min_count=1, window=5, iter=100)
        pretrained_weights = word_model.wv.syn0
        vocab_size, embedding_size = pretrained_weights.shape
        return word_model, pretrained_weights, vocab_size, embedding_size

    def get_similar_word_embedding(self, num_to_return, *words):
        for word in [words]:
            most_similar = ', '.join('%s (%.2f)' % (similar, dist) for similar, dist in self.word_model.most_similar(word)[:num_to_return])
            print('  %s -> %s' % (word, most_similar))

    def create_embedded_matrices(self):
        for i, sentence in enumerate(self.sentences):
            for t, word in enumerate(sentence[:-1]):
                self.train_x[i, t] = self.word2idx(word)
            self.train_y[i] = self.word2idx(sentence[-1])
        print('Created Embedded Matrices')

    def define_model(self):
        model = Sequential()
        model.add(Embedding(input_dim=self.vocab_size, output_dim=self.embedding_size, weights=[self.embedding_weights]))
        model.add(LSTM(units=self.embedding_size))
        model.add(Dense(units=self.vocab_size))
        model.add(Activation('softmax'))
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
        return model

    def sample(self, preds, temperature=1.0):
        if temperature <= 0:
            return numpy.argmax(preds)
        preds = numpy.asarray(preds).astype('float64')
        preds = numpy.log(preds) / temperature
        exp_preds = numpy.exp(preds)
        preds = exp_preds / numpy.sum(exp_preds)
        probas = numpy.random.multinomial(1, preds, 1)
        return numpy.argmax(probas)

    def generate_next(self, text, num_generated=10):
        word_idxs = [self.word2idx(word) for word in text.lower().split()]
        for _ in range(num_generated):
            prediction = self.model.predict(x=numpy.array(word_idxs))
            idx = self.sample(prediction[-1], temperature=0.7)
            word_idxs.append(idx)
        return ' '.join(self.idx2word(idx) for idx in word_idxs)
    
    def _set_texts_(self, texts):
        self.texts = texts

    def _on_epoch_end_(self, epoch, _):
        print('\nGenerating text after epoch: %d' % epoch)
        if self.texts:
            for text in self.texts:
                sample = self.generate_next(text)
                print('%s... -> %s' % (text, sample))

    def fit_model(self, num_epochs = 10):   
        self.model.fit(self.train_x, self.train_y,
            batch_size=128,
            epochs=num_epochs,
            callbacks=[LambdaCallback(on_epoch_end=self._on_epoch_end_)])

    
if __name__ == "__main__":
    #Testing
    thread = 'In science and engineering, intelligent processing of complex signals such as images, sound or language is often performed by a parameterized hierarchy of nonlinear processing layers, sometimes biologically inspired. Hierarchical systems (or, more generally, nested systems) offer a way to generate complex mappings using simple stages. Each layer performs a different operation and achieves an ever more sophisticated representation of the input, as, for example, in an deep artificial neural network, an object recognition cascade in computer vision or a speech front-end processing. Joint estimation of the parameters of all the layers and selection of an optimal architecture is widely considered to be a difficult numerical nonconvex optimization problem, difficult to parallelize for execution in a distributed computation environment, and requiring significant human expert effort, which leads to suboptimal systems in practice. We describe a general mathematical strategy to learn the parameters and, to some extent, the architecture of nested systems, called the method of auxiliary coordinates (MAC). This replaces the original problem involving a deeply nested function with a constrained problem involving a different function in an augmented space without nesting. The constrained problem may be solved with penalty-based methods using alternating optimization over the parameters and the auxiliary coordinates. MAC has provable convergence, is easy to implement reusing existing algorithms for single layers, can be parallelized trivially and massively, applies even when parameter derivatives are not available or not desirable, and is competitive with state-of-the-art nonlinear optimizers even in the serial computation setting, often providing reasonable models within a few iterations. Poor (even random) starting points for learning/training/optimization are common in machine learning. In many settings, the method of Robbins and Monro (online stochastic gradient descent) is known to be optimal for good starting points, but may not be optimal for poor starting points -- indeed, for poor starting points Nesterov acceleration can help during the initial iterations, even though Nesterov methods not designed for stochastic approximation could hurt during later iterations. The common practice of training with nontrivial minibatches enhances the advantage of Nesterov acceleration.'
    m = model(thread, 10)
    texts = [
        'a',
        'the'
    ]
    m._set_texts_(texts)
m.fit_model()