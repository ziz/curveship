'Tokenize input text for the Recognizer.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import sys
import re
try:
    import readline
except ImportError:
    pass

import input_model

def prepare(separator, prompt='', in_stream=sys.stdin, out_stream=sys.stdout):
    """Read a string from the input string and return it tokenized.

    Andrew Plotkin fixed this so that up arrow fetches the previous command."""
    if (hasattr(in_stream, 'isatty') and in_stream.isatty()):
        input_string = raw_input(prompt)
    else:
        out_stream.write(prompt)
        input_string = in_stream.readline()
        if input_string == '':
            # Empty string indicates end of the input file.
            # (A blank input line would look like '\n'.)
            raise EOFError()
        out_stream.write(input_string)
    return tokenize(input_string, separator)

def tokenize(input_string, separator):
    'Returns tokenized and slightly reformatted text.'
    input_string = re.sub('\s*$', '', input_string)
    new_text = input_string
    new_text = re.sub(' *([\.\?\!\&\(\)\-\;\:\,]) *', r' \1 ', new_text)
    new_text = re.sub('^[ \t]+', '', new_text)
    new_text = re.sub('[ \t\n]+$', '', new_text)
    new_text = re.sub('[ \t]+', ' ', new_text)
    new_text = re.sub(" *' *", " '", new_text)

    new_text = re.sub(" *' *", " '", new_text)
    tokens = new_text.lower().split()
    while len(tokens) > 0 and tokens[0] in separator:
        tokens.pop(0)
    while len(tokens) > 0 and tokens[-1] in separator:
        tokens.pop()
    user_input = input_model.RichInput(input_string, tokens)
    return user_input

if __name__ == "__main__":
    TEST_INPUT = prepare()
    print TEST_INPUT.tokens

