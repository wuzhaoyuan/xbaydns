#!/usr/bin/env python
# encoding: utf-8
"""
commandtest.py

Created by 黄 冬 on 2007-11-19.
Copyright (c) 2007 XBayDNS Team. All rights reserved.

Copyright © 2005-2007 Christopher Lenz[[BR]]
Copyright © 2007 Edgewall Software[[BR]]
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.
 3. The name of the author may not be used to endorse or promote
    products derived from this software without specific prior
    written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR “AS IS” AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

完成了command的用例测试，同时也是一个command使用的例程
"""

import basetest
import os
import shutil
import sys
import tempfile
import unittest
import logging.config

from xbaydns.utils import shtools
from xbaydns.utils.command import CommandLine,_combine,TimeoutError,FileSet

log = logging.getLogger('xbaydns.tests.commandtest')

class CommandTest(basetest.BaseTestCase):
    """
    command的测试用例类
    """
    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp(suffix='xbaydns_test'))
        basetest.BaseTestCase.setUp(self)

    def tearDown(self):
        shutil.rmtree(self.basedir)
        basetest.BaseTestCase.tearDown(self)

    def _create_file(self, name, content=None):
        filename = os.path.join(self.basedir, name)
        fd = file(filename, 'w')
        if content:
            fd.write(content)
        fd.close()
        return filename

    def testExecute(self):
        returncode = shtools.execute("ls")
        self.assertTrue(returncode==0)

    def testExecuteError(self):
        returncode = shtools.execute("中华人民共和国")
        self.assertTrue(returncode>0)

    def test_extract_lines(self):
        cmdline = CommandLine('test', [])
        data = ['foo\n', 'bar\n']
        lines = cmdline._extract_lines(data)
        self.assertEqual(['foo', 'bar'], lines)
        self.assertEqual([], data)

    def test_extract_lines_spanned(self):
        cmdline = CommandLine('test', [])
        data = ['foo ', 'bar\n']
        lines = cmdline._extract_lines(data)
        self.assertEqual(['foo bar'], lines)
        self.assertEqual([], data)

    def test_extract_lines_trailing(self):
        cmdline = CommandLine('test', [])
        data = ['foo\n', 'bar']
        lines = cmdline._extract_lines(data)
        self.assertEqual(['foo'], lines)
        self.assertEqual(['bar'], data)

    def test_combine(self):
        list1 = ['foo', 'bar']
        list2 = ['baz']
        combined = list(_combine(list1, list2))
        self.assertEqual([('foo', 'baz'), ('bar', None)], combined)

    def test_single_argument(self):
        cmdline = CommandLine('python', ['-V'])
        stdout = []
        stderr = []
        for out, err in cmdline.execute(timeout=5.0):
            if out is not None:
                stdout.append(out)
            if err is not None:
                stderr.append(err)
        py_version = '.'.join([str(v) for (v) in sys.version_info[:3]])
        self.assertEqual(['Python %s' % py_version], stderr)
        self.assertEqual([], stdout)
        self.assertEqual(0, cmdline.returncode)

    def test_multiple_arguments(self):
        script_file = self._create_file('test.py', content="""
import sys
for arg in sys.argv[1:]:
    print arg
""")
        cmdline = CommandLine('python', [script_file, 'foo', 'bar', 'baz'])
        stdout = []
        stderr = []
        for out, err in cmdline.execute(timeout=5.0):
            stdout.append(out)
            stderr.append(err)
        py_version = '.'.join([str(v) for (v) in sys.version_info[:3]])
        self.assertEqual(['foo', 'bar', 'baz'], stdout)
        self.assertEqual([None, None, None], stderr)
        self.assertEqual(0, cmdline.returncode)

    def test_output_error_streams(self):
        script_file = self._create_file('test.py', content="""
import sys, time
print>>sys.stdout, 'Hello'
print>>sys.stdout, 'world!'
sys.stdout.flush()
time.sleep(.1)
print>>sys.stderr, 'Oops'
sys.stderr.flush()
""")
        cmdline = CommandLine('python', [script_file])
        stdout = []
        stderr = []
        for out, err in cmdline.execute(timeout=5.0):
            stdout.append(out)
            stderr.append(err)
        py_version = '.'.join([str(v) for (v) in sys.version_info[:3]])
        self.assertEqual(['Hello', 'world!', None], stdout)
        self.assertEqual([None, None, 'Oops'], stderr)
        self.assertEqual(0, cmdline.returncode)

    def test_input_stream_as_fileobj(self):
        script_file = self._create_file('test.py', content="""
import sys
data = sys.stdin.read()
if data == 'abcd':
    print>>sys.stdout, 'Thanks'
""")
        input_file = self._create_file('input.txt', content='abcd')
        input_fileobj = file(input_file, 'r')
        try:
            cmdline = CommandLine('python', [script_file], input=input_fileobj)
            stdout = []
            stderr = []
            for out, err in cmdline.execute(timeout=5.0):
                stdout.append(out)
                stderr.append(err)
            py_version = '.'.join([str(v) for (v) in sys.version_info[:3]])
            self.assertEqual(['Thanks'], stdout)
            self.assertEqual([None], stderr)
            self.assertEqual(0, cmdline.returncode)
        finally:
            input_fileobj.close()

    def test_input_stream_as_string(self):
        script_file = self._create_file('test.py', content="""
import sys
data = sys.stdin.read()
if data == 'abcd':
    print>>sys.stdout, 'Thanks'
""")
        cmdline = CommandLine('python', [script_file], input='abcd')
        stdout = []
        stderr = []
        for out, err in cmdline.execute(timeout=5.0):
            stdout.append(out)
            stderr.append(err)
        py_version = '.'.join([str(v) for (v) in sys.version_info[:3]])
        self.assertEqual(['Thanks'], stdout)
        self.assertEqual([None], stderr)
        self.assertEqual(0, cmdline.returncode)

    def test_timeout(self):
        script_file = self._create_file('test.py', content="""
import time
time.sleep(2.0)
print 'Done'
""")
        cmdline = CommandLine('python', [script_file])
        iterable = iter(cmdline.execute(timeout=.5))
        self.assertRaises(TimeoutError, iterable.next)

class FileSetTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp(suffix='bitten_test'))

    def tearDown(self):
        shutil.rmtree(self.basedir)

    # Convenience methods

    def _create_dir(self, *path):
        cur = self.basedir
        for part in path:
            cur = os.path.join(cur, part)
            os.mkdir(cur)
        return cur[len(self.basedir) + 1:]

    def _create_file(self, *path):
        filename = os.path.join(self.basedir, *path)
        fd = file(filename, 'w')
        fd.close()
        return filename[len(self.basedir) + 1:]

    # Test methods

    def test_empty(self):
        fileset = FileSet(self.basedir)
        self.assertRaises(StopIteration, iter(fileset).next)

    def test_top_level_files(self):
        foo_txt = self._create_file('foo.txt')
        bar_txt = self._create_file('bar.txt')
        fileset = FileSet(self.basedir)
        assert foo_txt in fileset and bar_txt in fileset

    def test_files_in_subdir(self):
        self._create_dir('tests')
        foo_txt = self._create_file('tests', 'foo.txt')
        bar_txt = self._create_file('tests', 'bar.txt')
        fileset = FileSet(self.basedir)
        assert foo_txt in fileset and bar_txt in fileset

    def test_files_in_subdir_with_include(self):
        self._create_dir('tests')
        foo_txt = self._create_file('tests', 'foo.txt')
        bar_txt = self._create_file('tests', 'bar.txt')
        fileset = FileSet(self.basedir, include='tests/*.txt')
        assert foo_txt in fileset and bar_txt in fileset

    def test_files_in_subdir_with_exclude(self):
        self._create_dir('tests')
        foo_txt = self._create_file('tests', 'foo.txt')
        bar_txt = self._create_file('tests', 'bar.txt')
        fileset = FileSet(self.basedir, include='tests/*.txt', exclude='bar.*')
        assert foo_txt in fileset and bar_txt not in fileset


"""
测试用例结合
"""
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CommandTest, 'test'))
    suite.addTest(unittest.makeSuite(FileSetTestCase, 'test'))
    return suite

"""
单独运行command的测试用例
"""
if __name__ == '__main__':
    unittest.main(defaultTest='suite')
