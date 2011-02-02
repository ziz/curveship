'Format and display the output text.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import os
import re
import struct

def ioctl_term_size(filed):
    'Attempt to find terminal dimensions using an IO Control system call.'
    try:
        import fcntl, termios
        packed = fcntl.ioctl(filed, termios.TIOCGWINSZ, '1234')
        rows_cols = struct.unpack('hh', packed)
    except ImportError:
        return None
    if rows_cols == (0, 0):
        return None
    return rows_cols


def terminal_size():
    """Determine the terminal size or set a default size if that fails.
    
    From Chuck Blake's code, http://pdos.csail.mit.edu/~cblake/cls/cls.py
    Modifications by Doug Orleans to allow Curveship to run in GNU Emacs."""
    rows_cols = ioctl_term_size(0) or ioctl_term_size(1) or ioctl_term_size(2)
    if not rows_cols:
        try:
            filed = os.open(os.ctermid(), os.O_RDONLY)
            rows_cols = ioctl_term_size(filed)
            os.close(filed)
        except AttributeError:
            pass
    if not rows_cols:
        # Some shells may set these environment variables.
        rows_cols = (os.environ.get('LINES', 25), os.environ.get('COLUMNS', 80))
    return int(rows_cols[1]), int(rows_cols[0]) # Reverses it to cols, rows.


def _break_words(string, char_limit):
    'Lineate the string based on the passed-in character limit.'
    if len(string) <= char_limit:
        next_line = string
        string = ''
    elif '\n' in string[0:char_limit]:
        first_newline = string.index('\n')
        next_line = string[0:first_newline]
        string = string[(first_newline + 1):]
    elif ' ' not in string[0:char_limit]:
        next_line = string[0:char_limit]
        string = string[char_limit:]
    else:
        last_space = string[0:char_limit].rindex(' ')
        next_line = string[0:last_space]
        string = string[(last_space + 1):]
    return (next_line, string)


def present(string, out_streams, pre='', post='\n\n'):
    'Print the string, broken into lines, to the output streams.'
    if len(string) == 0:
        return
    if string[-1:] == '\n':
        post = re.sub('^[ \t]+', '', post)
    string = pre + string + post
    while len(string) > 0:
        (cols, _) = terminal_size()
        (next_line, string) = _break_words(string, cols)
        out_streams.write(next_line)
        if len(string) > 0:
            out_streams.write('\n')
    out_streams.write(string)


def center(string, out_streams, pre='', post='\n'):
    'Center the output and print it to the output streams.'
    string = pre + string + post
    (cols, _) = terminal_size()
    while len(string) > 0:
        (next_line, string) = _break_words(string, cols)
        while len(next_line) > 0 and next_line[0] == '\n':
            out_streams.write('\n')
            next_line = next_line[1:]
        spaces = ''
        i = 1
        while i <= (cols - len(next_line))/2:
            spaces += ' '
            i += 1
        out_streams.write(' ' + spaces + next_line)
        if len(string) > 0:
            out_streams.write('\n')

