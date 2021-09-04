#!/usr/bin/env python3
from clang import cindex
import os

class EasyIndex(cindex.Index):
    def __new__(cls, *args):
        new = cindex.Index.create()
        new.__class__ = cls
        return new

    def __init__(self, dbpath):
        self.compdb = cindex.CompilationDatabase.fromDirectory(dbpath)
        self.compile_commands = {
            os.path.abspath(cc.filename) : dict(
                directory=cc.directory,
                arguments=list(cc.arguments),
            )
            for cc in self.compdb.getAllCompileCommands()
        }
        self.options_by_compiler = {}

    def getargs(self, filename):
        abspath = os.path.abspath(filename)
        cc = self.compile_commands[abspath]
        arguments = cc['arguments']
        compiler, arguments = arguments[0], arguments[1:]
        arguments.remove(abspath)
        for i, a in enumerate(arguments):
            if a == '-o':
                del arguments[i:i+2]
                break
        return arguments

    def getcompilerargs(self, compiler):



    def parse(self, path, args=None, *moreargs, **kwargs):
        args = self.getargs(path)
        print(args)
        return super(EasyIndex, self).parse(path, args, *moreargs, **kwargs)
