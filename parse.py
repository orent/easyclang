#!/usr/bin/env python3
from clang import cindex
import os
import subprocess

class EasyIndex(cindex.Index):
    def __new__(cls, *args):
        new = cindex.Index.create()
        new.__class__ = cls
        return new

    def __init__(self, dbpath):
        compdb = cindex.CompilationDatabase.fromDirectory(dbpath)
        self.compile_commands = {
            os.path.abspath(cc.filename) : dict(
                directory=cc.directory,
                arguments=list(cc.arguments),
            )
            for cc in compdb.getAllCompileCommands()
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
        return ['-working-directory='+cc['directory']] + self.getcompilerargs(compiler) + arguments
        return self.getcompilerargs(compiler) + arguments

    def getcompilerargs(self, compiler):
        try:
            return self.options_by_compiler[compiler]
        except KeyError:
            pass
        output = subprocess.check_output(
                [compiler, '-E', '-v', '-'], 
                stdin=open('/dev/null'),
                stderr=subprocess.STDOUT,
                encoding='latin1',
        )
        lines = output.splitlines()
        a = lines.index('#include "..." search starts here:')
        b = lines.index('#include <...> search starts here:')
        c = lines.index('End of search list.')
        inc = lines[a+1:b]
        isystem = lines[b+1:c]
        args = []
        for path in inc:
            args.append('-I')
            args.append(path.strip())
        for path in isystem:
            args.append('-isystem')
            args.append(path.strip())
        self.options_by_compiler[compiler] = args
        return args

    def parse(self, path, args=None, *moreargs, **kwargs):
        abspath = os.path.abspath(path)
        args = self.getargs(abspath) + list(args or [])
        print(args)

        cwd = os.getcwd()
        try:
            return super(EasyIndex, self).parse(abspath, args, *moreargs, **kwargs)
        finally:
            os.chdir(cwd)
