from random import randint, choice

def sentence_filter(phrases):
    new_phrases = phrases[:1]
    for original in phrases[1:]:
        if randint(1,5) == 1:
            if not new_phrases[-1][-1] in ',.:;':
                new_phrases.append(',')
            new_phrases.append('like')
            if not original in ',.:;':
                new_phrases.append(',')
        new_phrases.append(original)
    if len(new_phrases) > 0 and randint(1,6) == 1:
        if not new_phrases[-1] in ',.:;':
            new_phrases.append(',')
        new_phrases.append(choice(['totally', 'for sure']))
    return new_phrases

spin = {'sentence_filter': [sentence_filter]}

