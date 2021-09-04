#!/usr/bin/env python3
from clang import cindex

class EasyIndex(cindex.Index):
    def __new__(cls, *args):
        new = cindex.Index.create()
        new.__class__ = cls
        return new

    def __init__(self, *args):
        pass
