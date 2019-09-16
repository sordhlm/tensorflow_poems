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
import datetime
from compose_poem import Poem
from pypinyin import pinyin, Style

class GoodPoem(Poem):
    def __init__(self, s_word, format):
        super(GoodPoem, self).__init__(s_word)
        self.format = format
        time = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
        self.output = 'ai_poems_'+time+'.txt'
        self.good_tone_th = 17

    def gen_poem_manual(self):
        poem = self.gen_poem(self.to_word_manual)
        print(poem)

    def gen_poems(self, num = 1):
        i = 0
        while i < num:
            poem = self.gen_poem(self.to_word_auto)
            if self.is_good_format(poem):
                print("Good Poem ...")
                print(poem)
                with open(self.output, 'a+') as fp:
                    fp.write(poem+"\n")
                i += 1
            #else:
            #    print("Bad Poem ...")
            #    print(poem)

    def is_good_format(self, poem):
        if '7jue' in self.format:
            self.max_len = 32
            split = 8
            length = 2
            good_tone = self.is_good_7jue_tone
            self.good_tone_th = 24
        elif '5jue' in self.format:
            self.max_len = 24
            split = 6
            length = 2
            good_tone = self.is_good_5jue_tone
            self.good_tone_th = 17
        elif '5lv' in self.format:
            self.max_len = 48
            split = 6
            length = 4
        elif '7lv' in self.format:
            self.max_len = 64
            split = 8
            length = 4
        if len(poem) != self.max_len:
            return 0
        for i in range(2):
            if '，' not in poem[split*(2*i+1)-1]:
                return 0
            if '。' not in poem[split*(2*i+2)-1]:
                return 0
        return good_tone(poem)

    def is_good_5jue_tone(self, poem):
        good_tone = [0]*4
        good_tone[0] = [[1,2],[1,2],[3,4],[3,4],[1,2],None,[3,4],[3,4],[3,4],[1,2],[1,2],None,[3,4],[3,4],[1,2],[1,2],[3,4],None,[1,2],[1,2],[3,4],[3,4],[1,2],None]
        good_tone[1] = [[1,2],[1,2],[1,2],[3,4],[3,4],None,[3,4],[3,4],[3,4],[1,2],[1,2],None,[3,4],[3,4],[1,2],[1,2],[3,4],None,[1,2],[1,2],[3,4],[3,4],[1,2],None]
        good_tone[2] = [[3,4],[3,4],[3,4],[1,2],[1,2],None,[1,2],[1,2],[3,4],[3,4],[1,2],None,[1,2],[1,2],[1,2],[3,4],[3,4],None,[3,4],[3,4],[3,4],[1,2],[1,2],None]
        good_tone[3] = [[3,4],[3,4],[1,2],[1,2],[3,4],None,[1,2],[1,2],[3,4],[3,4],[1,2],None,[1,2],[1,2],[1,2],[3,4],[3,4],None,[3,4],[3,4],[3,4],[1,2],[1,2],None]
        poem_tone = pinyin(poem,style=Style.TONE3)
        print(poem)
        print(poem_tone)
        if len(poem_tone) != self.max_len:
            return 0
        for i in range(4):
            if self.good_tone_judge(poem_tone, good_tone[i]):
                return 1
        return 0

    def is_good_7jue_tone(self, poem):
        good_tone = [0]*4
        good_tone[0] = [[1,2],[1,2],[3,4],[3,4],[3,4],[1,2],[1,2],None,[3,4],[3,4],[1,2],[1,2],[3,4],[3,4],[1,2],None,\
                        [3,4],[3,4],[1,2],[1,2],[1,2],[3,4],[3,4],None,[1,2],[1,2],[3,4],[3,4],[3,4],[1,2],[1,2],None]
        good_tone[1] = [[1,2],[1,2],[3,4],[3,4],[1,2],[1,2],[3,4],None,[3,4],[3,4],[1,2],[1,2],[3,4],[3,4],[1,2],None,\
                        [3,4],[3,4],[1,2],[1,2],[1,2],[3,4],[3,4],None,[1,2],[1,2],[3,4],[3,4],[3,4],[1,2],[1,2],None]
        good_tone[2] = [[3,4],[3,4],[1,2],[1,2],[3,4],[3,4],[1,2],None,[1,2],[1,2],[3,4],[3,4],[3,4],[1,2],[1,2],None,\
                        [1,2],[1,2],[3,4],[3,4],[1,2],[1,2],[3,4],None,[3,4],[3,4],[1,2],[1,2],[3,4],[3,4],[1,2],None]
        good_tone[3] = [[3,4],[3,4],[1,2],[1,2],[1,2],[3,4],[3,4],None,[1,2],[1,2],[3,4],[3,4],[3,4],[1,2],[1,2],None,\
                        [1,2],[1,2],[3,4],[3,4],[1,2],[1,2],[3,4],None,[3,4],[3,4],[1,2],[1,2],[3,4],[3,4],[1,2],None]
        poem_tone = pinyin(poem,style=Style.TONE3)
        print(poem)
        print(poem_tone)
        if len(poem_tone) != self.max_len:
            return 0
        for i in range(4):
            if self.good_tone_judge(poem_tone, good_tone[i]):
                return 1
        return 0

    def good_tone_judge(self, poem_tone, good_tone):
        rate = 0
        for i in range(self.max_len):
            if good_tone[i]:
                sd = poem_tone[i][0][-1:]
                if sd.isdigit():
                    if int(sd) in good_tone[i]:
                        rate += 1
        print("rate: %d"%rate)
        return (rate >= self.good_tone_th)






if __name__ == '__main__':
    begin_char = input('## please input the first character:')
    poem = GoodPoem(begin_char, '7jue')
    poem.gen_poems(100)
    #poem.gen_poem_manual()
    #pretty_print_poem(poem_=poem)
