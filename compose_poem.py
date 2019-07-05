# -*- coding: utf-8 -*-
# file: main.py
# author: JinTian
# time: 11/03/2017 9:53 AM
# Copyright 2017 JinTian. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
import tensorflow as tf
from poems.model import rnn_model
from poems.poems import process_poems
import numpy as np
from pypinyin import pinyin, Style

class Poem(object):
    def __init__(self, s_word):
        self.begin_word = s_word
        self.start_token = 'B'
        self.end_token = 'E'
        self.model_dir = './model/'
        self.corpus_file = './data/poems.txt'
        self.lr = 0.0002
        self.RATE = 0.008
        self.max_len = 78
        self.poems_vector, self.word_int_map, self.vocabs = process_poems(self.corpus_file)
        self.input_data = tf.placeholder(tf.int32, [1, None])
        self.end_points = rnn_model(model='lstm', input_data=self.input_data, output_data=None, vocab_size=len(
            self.vocabs), rnn_size=128, num_layers=2, batch_size=64, learning_rate=self.lr)

    def _rate_for_tone(self, tdst, tsrc):
        tsrc1 = tsrc[:-1]
        tsrc2 = tsrc[-1:]
        tdst1 = tdst[:-1]
        tdst2 = tdst[-1:]
        add_rate = 0
        if (tsrc1 not in tdst1) and (tdst1 not in tsrc1):
            return 0
        if len(tsrc1) == 1:
            if len(tdst1) == 1:
                add_rate += self.RATE
                if (tsrc2 in tdst2):
                    add_rate += self.RATE
        else:
            if len(tdst1) != 1:
                if len(tdst1) == len(tsrc1):
                    add_rate += self.RATE
                if (tsrc2 in tdst2):
                    add_rate += self.RATE
        return add_rate

    def _predict_with_tone(self, predict, tone):
        new_predict = predict
        if tone:
            for i in range(len(self.vocabs)):
                pword = pinyin(self.vocabs[i],style=Style.FINALS_TONE3)[0][0]
                #print("%s %s %s, We need %s %s"%(self.vocabs[i], pword1, pword2, tone1, tone2))
                new_predict[i] += self._rate_for_tone(pword, tone)

        return new_predict/np.sum(new_predict)

    def _to_word(self, predict, tone=None):
        pdata = np.copy(predict[0])
        #print(predict)
        #print(np.sum(predict))
        #print(len(predict))
        pdata = self._predict_with_tone(pdata, tone)
        #tmp = predict.tolist()
        #pdata /= np.sum(pdata)
        sample = np.random.choice(np.arange(len(pdata)), p=pdata)
        #sample = tmp.index(max(tmp))
        #print(sample)
        if sample > len(self.vocabs):
            return self.vocabs[-1]
        else:
            return self.vocabs[sample]

    def gen_poem(self):
        batch_size = 1
        print('## loading corpus from %s' % self.model_dir)


        saver = tf.train.Saver(tf.global_variables())
        init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
        with tf.Session() as sess:
            sess.run(init_op)

            checkpoint = tf.train.latest_checkpoint(self.model_dir)
            saver.restore(sess, checkpoint)

            x = np.array([list(map(self.word_int_map.get, self.start_token))])

            [predict, last_state] = sess.run([self.end_points['prediction'], self.end_points['last_state']],
                                             feed_dict={self.input_data: x})
            word = self.begin_word or self._to_word(predict)
            poem_ = ''

            i = 0
            #print(last_state)
            #for i, (c, h) in enumerate(last_state):
            #    print(last_state[i].c)
            #    print(last_state[i].h)
            single_len = self.max_len
            tone = None
            plist = []
            while word != self.end_token:
                poem_ += word
                i += 1
                if i > self.max_len:
                    break
                x = np.array([[self.word_int_map[word]]])
                [predict, last_state] = sess.run([self.end_points['prediction'], self.end_points['last_state']],
                                                 feed_dict={self.input_data: x, self.end_points['initial_state']: last_state})
                add_tone = tone if (i+2)%single_len == 0 else None
                word = self._to_word(predict, add_tone)
                #print("idx[%d, %d], %s %s %s"%(i, single_len, word, pinyin(word,style=Style.FINALS_TONE3)[0][0], add_tone))
                plist.append(word)
                #print(single_len)
                if (word in '，') and single_len == self.max_len:
                    single_len = i+1
                    tone = pinyin(plist[i-2],style=Style.FINALS_TONE3)[0][0]
                    #print(tone)

            return poem_


#start_token = 'B'
#end_token = 'E'
#model_dir = './model/'
#corpus_file = './data/poems.txt'
#
#lr = 0.0002
#RATE = 0.008
#def rate_for_tone(tdst, tsrc):
#    tsrc1 = tsrc[:-1]
#    tsrc2 = tsrc[-1:]
#    tdst1 = tdst[:-1]
#    tdst2 = tdst[-1:]
#    add_rate = 0
#    if (tsrc1 not in tdst1) and (tdst1 not in tsrc1):
#        return 0
#    if len(tsrc1) == 1:
#        if len(tdst1) == 1:
#            add_rate += RATE
#            if (tsrc2 in tdst2):
#                add_rate += RATE
#    else:
#        if len(tdst1) != 1:
#            if len(tdst1) == len(tsrc1):
#                add_rate += RATE
#            if (tsrc2 in tdst2):
#                add_rate += RATE
#    return add_rate
#
#def predict_with_tone(predict, vocabs, tone):
#    new_predict = predict
#    if tone:
#        for i in range(len(vocabs)):
#            pword = pinyin(vocabs[i],style=Style.FINALS_TONE3)[0][0]
#            #print("%s %s %s, We need %s %s"%(vocabs[i], pword1, pword2, tone1, tone2))
#            new_predict[i] += rate_for_tone(pword, tone)
#
#    return new_predict/np.sum(new_predict)
#
#def to_word(predict, vocabs, tone=None):
#    pdata = np.copy(predict[0])
#    #print(predict)
#    #print(np.sum(predict))
#    #print(len(predict))
#    pdata = predict_with_tone(pdata, vocabs, tone)
#    #tmp = predict.tolist()
#    #pdata /= np.sum(pdata)
#    sample = np.random.choice(np.arange(len(pdata)), p=pdata)
#    #sample = tmp.index(max(tmp))
#    #print(sample)
#    if sample > len(vocabs):
#        return vocabs[-1]
#    else:
#        return vocabs[sample]
#
#
#def gen_poem(begin_word):
#    batch_size = 1
#    print('## loading corpus from %s' % model_dir)
#    poems_vector, word_int_map, vocabularies = process_poems(corpus_file)
#    #print(poems_vector)
#    #print(word_int_map)
#    input_data = tf.placeholder(tf.int32, [batch_size, None])
#
#    end_points = rnn_model(model='lstm', input_data=input_data, output_data=None, vocab_size=len(
#        vocabularies), rnn_size=128, num_layers=2, batch_size=64, learning_rate=lr)
#
#    saver = tf.train.Saver(tf.global_variables())
#    init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
#    with tf.Session() as sess:
#        sess.run(init_op)
#
#        checkpoint = tf.train.latest_checkpoint(model_dir)
#        saver.restore(sess, checkpoint)
#
#        x = np.array([list(map(word_int_map.get, start_token))])
#
#        [predict, last_state] = sess.run([end_points['prediction'], end_points['last_state']],
#                                         feed_dict={input_data: x})
#        word = begin_word or to_word(predict, vocabularies)
#        poem_ = ''
#
#        i = 0
#        #print(last_state)
#        #for i, (c, h) in enumerate(last_state):
#        #    print(last_state[i].c)
#        #    print(last_state[i].h)
#        max_len = 78
#        single_len = max_len
#        tone = None
#        plist = []
#        while word != end_token:
#            poem_ += word
#            i += 1
#            if i > max_len:
#                break
#            x = np.array([[word_int_map[word]]])
#            [predict, last_state] = sess.run([end_points['prediction'], end_points['last_state']],
#                                             feed_dict={input_data: x, end_points['initial_state']: last_state})
#            add_tone = tone if (i+2)%single_len == 0 else None
#            word = to_word(predict, vocabularies, add_tone)
#            print("idx[%d, %d], %s %s %s"%(i, single_len, word, pinyin(word,style=Style.FINALS_TONE3)[0][0], add_tone))
#            plist.append(word)
#            #print(single_len)
#            if (word in '，') and single_len == max_len:
#                single_len = i+1
#                tone = pinyin(plist[i-2],style=Style.FINALS_TONE3)[0][0]
#                #print(tone)
#        return poem_
#
#
#def pretty_print_poem(poem_):
#    print(poem_)
#    print(len(poem_))
#    poem_sentences = poem_.split('。')
#    for s in poem_sentences:
#        if s != '' and len(s) > 10:
#            print(s + '。')

if __name__ == '__main__':
    begin_char = input('## please input the first character:')
    poem = gen_poem(begin_char)
    pretty_print_poem(poem_=poem)
