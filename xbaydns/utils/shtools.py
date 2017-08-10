# encoding: utf-8
"""
shtools.py

Created by 黄 冬 on 2007-11-07.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.

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

"""

import logging
import os
import shlex

from xbaydns.utils.command import CommandLine

log = logging.getLogger('xbaydns.utils.shtools')

def execute(executable=None, file_=None, input_=None, output=None, args=None):
    """Generic external program execution.
    
    This function is not itself bound to a recipe command, but rather used from
    other commands.
    
    :param executable: name of the executable to run
    :param file\_: name of the script file, relative to the project directory,
                  that should be run
    :param input\_: name of the file containing the data that should be passed
                   to the shell script on its standard input stream
    :param output: name of the file to which the output of the script should be
                   written
    :param args: command-line arguments to pass to the script
    """
    if args:
        if isinstance(args, basestring):
            args = shlex.split(args)
    else:
        args = []

    if executable is None:
        executable = file_
    elif file_:
        args[:0] = [file_]

    if input_:
        input_file = file(input_, 'r')
    else:
        input_file = None

    output_file = None
    if output:
        output_file = file(output, 'w')

    try:
        log.debug('%s excuting args is %s', executable, args)
        cmdline = CommandLine(executable, args, input=input_file)
        for out, err in cmdline.execute():
            if out is not None:
                log.info(out)
                if output:
                    output_file.write(out + os.linesep)
            if err is not None:
                log.error(err)
                if output:
                    output_file.write(err + os.linesep)
    finally:
        if input_:
            input_file.close()
        if output:
            output_file.close()

    return cmdline.returncode