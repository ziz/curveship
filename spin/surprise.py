'A spin to make the narrator seem surprised at everything.'

__author__ = 'Nick Montfort <nickm@nickm.com>'
__version__ = '0.5'

from random import randint, choice


def sentence_filter(phrases):
    chosen = randint(1,8)
    if chosen == 1:
        phrases = [choice(['whoa,', 'dude,',])] + phrases
    elif chosen == 2:
        if not phrases[-1][-1] in ',.:;':
            phrases[-1] += ','
        phrases = phrases + [choice(['man','dude',])]
    phrases[-1] = phrases[-1] + '!'
    return phrases

def paragraph_filter(paragraphs):
    chosen = randint(1,3)
    if chosen == 1:
        paragraphs = paragraphs + choice(['Amazing!', 'Wow!', 'Awesome!',
                                          'Out of this world!', 'Incredible!'])
    return paragraphs

spin = {'sentence_filter': [sentence_filter],
        'paragraph_filter': [paragraph_filter]}

