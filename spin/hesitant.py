from random import randint, choice

interjections = ['uh', 'uh', 'uh', 'um', 'um', 'er']

def sentence_filter(phrases):
    new_phrases = phrases[:1]
    for original in phrases[1:]:
        if randint(1,6) == 1:
            if not new_phrases[-1][-1] in ',.:;':
                new_phrases.append(',')
            new_phrases.append(choice(interjections))
            if not original[:1] in ',.:;':
                new_phrases.append(',')
        new_phrases.append(original)
    return new_phrases

spin = {'sentence_filter': [sentence_filter]}

