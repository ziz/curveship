"""A spin to make the narrator seem downcast and abusive.

Copyright (c) 2011 Amaranth Borsuk and Brad Bouse

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE."""

__author__ = 'Amaranth Borsuk and Brad Bouse'
__version__ = '0.5'

from random import randint, choice


def sentence_filter(phrases):
    chosen = randint(1,4)
    if chosen == 1:
        phrases = [choice(['dammit', 'geez', 'well', 'sigh', 
                           'oh, bother']) + ','] + phrases
    elif chosen == 2:
        if not phrases[-1][-1] in [',', '.', ':', ';']:
            phrases.append(',')
        phrases.append(choice(['dork', 'loser', 'wimp', 'typical',
                               'just as I suspected', 'if you must']))
    phrases += ['...']
    return phrases

def paragraph_filter(paragraphs):
    chosen = randint(1,3)
    if chosen == 1:
        paragraphs += choice(['Oh well.', 'Whatever.', 'Whoopty doo.',
            "I guess that's good news if you're into that sort of thing.",
            'Like you care.', "How 'bout that.",
            "This can't be good.", 'I can never be happy again.', 
            "It's all the same to me.", 'Dear, dear.', 'Why?', 'Why bother?',
            "I'm very sorry about that.", 'How like them.', 'How sad.',
            'Is that really all there is?', 'Is that all there is?',
            'I might have known.', 'Oh, poo.', 'Very well.'])
    return paragraphs

spin = {'sentence_filter': [sentence_filter],
        'paragraph_filter': [paragraph_filter]}

