#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Tony on 2018/9/27
class MyObject:

    def __init__(self, name):
        self.name = name

    def eat(self, what):
        return '%s eats %s' % (self.name, what)

    def __str__(self):
        return self.name


OBJECT = MyObject('Robot')
DICTIONARY = {1: 'one', 2: 'two', 3: 'three'}

if __name__ == '__main__':
    OBJECT = MyObject('Robot')
    DICTIONARY = {1: 'one', 2: 'two', 3: 'three'}
