'Surface realization: Convert a fully specified section to a string.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import re
import types
import irregular_verb

def apply_filter_list(filter_list, string):
    'Transforms the string by applying all filters in the list.'
    if filter_list is not None:
        for output_filter in filter_list:
            string = output_filter(string)
    return string


class Section(object):
    'Encapsulates blocks of text, each one a paragraph or heading.'

    def __init__(self, blocks):
        self.blocks = blocks

    def __str__(self):
        string = '\n<section>\n\n'
        for i in self.blocks:
            string += str(i) + '\n'
        return string + '</section>\n'

    def realize(self, concept, discourse):
        'Return a string realized from this, the concept, and the discourse.'
        string = ''
        previous = None
        for (i, block) in enumerate(self.blocks):
            last = (i == len(self.blocks) - 1)
            string += block.realize(previous, last, concept, discourse)
            previous = block
        return string


class Heading(object):
    'A normally one-line heading, e.g., for indicating the current room.'

    def __init__(self, string):
        self.line = string

    def __str__(self):
        return '<h>' + self.line + '</h>\n'

    def realize(self, previous, last, _, discourse):
        'Return a string realized from this, position info, and the discourse.'
        string = discourse.typo.format_heading(self.line, previous, last)
        return string


class Paragraph(object):
    'Unit of several sentences, realized with indentation and spacing.'

    def __init__(self, template_filter, strings, time=0):
        self.sentences = []
        for i in strings:
            self.sentences.append(Sentence(template_filter, i, time))

    def __eq__(self, pgraph):
        return self.sentences == pgraph.sentences

    def __ne__(self, pgraph):
        return not self.__eq__(pgraph)

    def __str__(self):
        string = ''
        for i in self.sentences:
            string += str(i)
        return '<p>' + string + '</p>\n'

    def merge(self, paragraph):
        "Add the argument's sentences to this paragraph."
        for i in paragraph.sentences:
            self.sentences.append(i)

    def set(self, narrator, narratee, tense_er, tense_rs, progressive):
        'Defines the generator settings for all the sentences.'
        for i in self.sentences:
            i.set(narrator, narratee, tense_er, tense_rs, progressive)

    def realize(self, previous, last, concept, discourse):
        'Return a string from this, position info, concept, and discourse.'
        string = ''
        capitalize = True
        for i in self.sentences:
            if hasattr(i, 'realize'):
                new_sentence = i.realize(concept, discourse)
                string += fix_orthography(new_sentence, capitalize) + ' '
                if len(new_sentence) > 0 and new_sentence[-1] == ',':
                    capitalize = False
                else:
                    capitalize = True
        string = apply_filter_list(discourse.spin['paragraph_filter'], string)
        string = string.strip()
        return discourse.typo.format_paragraph(string, previous, last)


class GeneratorSettings(object):
    'Five narrative/grammatical parameters important for realization.'

    def __init__(self, narrator, narratee, tense_er, tense_rs, progressive):
        self.narrator = narrator
        self.narratee = narratee
        self.tense_er = tense_er
        self.tense_rs = tense_rs
        self.progressive = progressive


class Sentence(object):
    'Holds a template with slots and other necessary parameters.'

    def __init__(self, t_filter, string, time):
        string = re.sub(']', '] ', string)
        string = apply_filter_list(t_filter, string)
        self.parts = []
        self.settings = None
        for token in string.split():
            noun_kws = {}
            if token[0] == '[' and token[-1] == ']':
                slot = token[1:-1].lower()
                if slot[-2:] == "'s":
                    self.parts.append(Pronoun(slot[:-2], Pronoun.possessive,
                                      time))
                else:
                    bits = slot.split('/') # A slot has different bits.
                    if 'pro' in bits:
                        noun_kws['pronominalize'] = True
                        bits.remove('pro')
                    kind = bits.pop()
                    if kind in ['here', 'now', 'this', 'these']:
                        self.parts.append(Deictic(kind))
                    elif kind in ['begin-caps', 'end-caps']:
                        self.parts.append(token)
                    else:
                        head = bits.pop(0)
                        if kind == 's':
                            self.parts.append(Noun(head, Noun.subject, bits,
                                                   time, **noun_kws))
                        elif kind == 'o':
                            self.parts.append(Noun(head, Noun.object, bits,
                                                   time, **noun_kws))
                        elif kind == 'a':
                            self.parts.append(Adjective(bits[-1], head, time))
                        elif kind == 'v':
                            verb_kws = {}
                            verb_kws['negated'] = False
                            if 'do' in bits:
                                verb_kws['intensive'] = True
                            if 'not' in bits:
                                verb_kws['negated'] = True
                            if '1' in bits:
                                verb_kws['default_number'] = 'singular'
                            elif '2' in bits:
                                verb_kws['default_number'] = 'plural'
                            if 'ing' in bits:
                                verb_kws['progressive'] = True
                            if 'ed' in bits:
                                verb_kws['tense_er'] = 'anterior'
                            self.parts.append(Verb(head, time, **verb_kws))
            elif '_' in token:
                self.parts.append(NP(token))
            else:
                if token[:2] == '\\[':
                    token = token[1:]
                self.parts.append(token)

    def __eq__(self, sentence):
        return self.parts == sentence.parts

    def __ne__(self, sentence):
        return not self.__eq__(sentence)

    def __str__(self):
        string = ''
        for i in self.parts:
            string += str(i) + ' '
        if len(self.parts) > 0:
            string = string[0:-1]
        return '<s>' + string + '</s>'

    def set(self, narrator, narratee, tense_er, tense_rs, progressive):
        'Defines five grammatical/narrative settings needed to realize.'
        self.settings = GeneratorSettings(narrator, narratee, tense_er,
                                          tense_rs, progressive)

    def prepend(self, string):
        'Add this string to the beginning of the sentence.'
        self.parts = [string] + self.parts

    def realize(self, concept, discourse):
        'Return a string from this, a concept, and the discourse.'
        phrases = []
        all_caps = False
        subjects, tf = (), False
        for part in self.parts:
            more = ''
            if type(part) is types.StringType:
                if part == '[begin-caps]':
                    all_caps = True
                elif part == '[end-caps]':
                    all_caps = False
                else:
                    more = part
            else:
                (more, subjects, tf) = part.realize(concept, discourse,
                                                    self.settings, subjects, tf)
            if len(more) > 0:
                if all_caps:
                    more = more.upper()
                phrases.append(more)
        phrases = apply_filter_list(discourse.spin['sentence_filter'], phrases)
        string = ' '.join(phrases)
        string = re.sub('\( ', '(', string)
        string = re.sub(' \)', ')', string)
        return string.strip()
 

def fix_orthography(string, capitalize=True):
    'Capitalize (optionally) and punctuate the end of a sentence string.'

    string = string.strip()
    if len(string) == 0:
        return string
    else:
        if capitalize:
            string = string[0].upper() + string[1:]
    if (re.match('[a-zA-Z0-9]', string) and string[-1] not in list(',.!?;:')):
        string = string + '.'
    string = re.sub(' *\,', ',', string)
    string = re.sub(' *\;', ';', string)
    string = re.sub(' *\:', ':', string)
    string = re.sub('"\.$', '."', string)
    string = re.sub('"\,$', ',"', string)
    return string


class Word(object):
    'Base representation of a lexical element, not for instantiation.'

    def __init__(self, tag):
        self.tag = tag

    def __eq__(self, word):
        return str(self) == str(word)

    def __ne__(self, word):
        return not self.__eq__(word)

    def __str__(self):
        return self.tag

    def realize(self, _, __, ___, subjects, tf):
        'Return a string realized from the word.'
        return (self.tag, subjects, tf)


class Adjective(Word):
    'Adjective describing a feature of an item.'

    def __init__(self, tag, feature, time):
        self.feature = feature
        self.time = time
        Word.__init__(self, tag)

    def __str__(self):
        return 'A.' + self.tag + '.' + self.feature

    def realize(self, concept, discourse, _, subjects, tf):
        'Return a string realized from the word.'
        tag = self.tag
        if self.tag == '*':
            tag = discourse.spin['focalizer']
        value = getattr(concept.item_at(tag, self.time), self.feature)
        string = discourse.feature_to_english[self.feature](value)
        return (string, subjects, tf)


class NP(Word):
    'Noun phrase.'

    def __init__(self, string):
        if string[:1] == '_':
            string = string[1:]
        words = string.split('_')
        self.determiner = ''
        if words[0] in ['a', 'an', 'one', 'some', 'the', 'that', 'this']:
            self.determiner = words.pop(0)
        self.rest = words
        Word.__init__(self, words[-1])

    def __str__(self):
        return self.determiner + '_'.join(self.rest)

    def realize(self, _, discourse, __, subjects, tf):
        'Return a string realized from the word.'
        string = ''
        phrase = '_' + '_'.join(self.rest)
        if len(self.determiner) > 0:
            if phrase not in discourse.givens:
                string = self.determiner + ' '
            else:
                string = 'the '
        string += ' '.join(self.rest)
        if phrase not in discourse.givens:
            discourse.givens.add(phrase)
        return (string, subjects, tf)


class Noun(Word):
    'Noun describing an Item; may be pronominalized upon realization.'

    subject, object, possessive, reflexive = range(4)

    def __init__(self, tag, form, adjs, time, **keywords):
        self.form = form
        self.adjs = adjs
        self.pronominalize = False
        if 'pronominalize' in keywords:
            self.pronominalize = keywords['pronominalize']
        self.time = time
        Word.__init__(self, tag)

    def __str__(self):
        return 'N.' + self.tag + '.' + 'SOPR'[self.form]

    def realize(self, concept, discourse, settings, subjects, tf):
        'Return a string realized from the word.'
        tag = self.tag
        if self.tag == '*':
            tag = discourse.spin['focalizer']
        if tag in subjects and self.form == self.object:
            self.form = self.reflexive
            self.pronominalize = True
        elif tag in [settings.narrator, settings.narratee]:
            self.pronominalize = True
        if self.pronominalize:
            # Ignore what pronoun returns as subjects to avoid double-
            # counting this word
            (string, _, __) = Pronoun(tag, self.form, 
                self.time).realize(concept, discourse, settings, subjects, tf)
        else:
            extra_adjs = ', '.join(self.adjs)
            item = concept.item_at(tag, self.time)
            if item is None:
                string = 'something'
            else:
                string = item.noun_phrase(discourse, extra_adjs=extra_adjs)
            if self.form == self.possessive:
                string += "'s"
        if tag not in discourse.givens:
            discourse.givens.add(tag)
        if self.form == self.subject:
            if tf is True:
                subjects = ()
            subjects = tuple(list(subjects) + [tag])
            tf = False
        return (string, subjects, tf)


class Deictic(Word):
    'Deictic word which is sensitive to the use of the present tense.'

    def __str__(self):
        return 'D.' + self.tag

    def realize(self, _, __, settings, subjects, tf):
        'Return a string realized from the word.'
        string = str(self)
        if self.tag == 'now':
            string = ['then', 'now'][settings.tense_rs == 'present']
        elif self.tag == 'here':
            string = ['there', 'here'][settings.tense_rs == 'present']
        elif self.tag == 'this':
            string = ['that', 'this'][settings.tense_rs == 'present']
        elif self.tag == 'these':
            string = ['those', 'these'][settings.tense_rs == 'present']
        return (string, subjects, tf)


class Pronoun(Word):
    'Pronoun of some form representing some Item.'

    subject, object, possessive, reflexive = range(4)

    subject_pronoun = {1:
    {'singular': {'male': 'I', 'female': 'I', 'neuter': 'I', '?': 'I'},
     'plural': {'male': 'we', 'female': 'we', 'neuter': 'we', '?': 'we'}},
    2:
    {'singular': {'male': 'you', 'female': 'you', 'neuter': 'you', '?': 'you'},
     'plural': {'male': 'you', 'female': 'you', 'neuter': 'you', '?': 'you'}},
    3:
    {'singular': {'male': 'he', 'female': 'she', 'neuter': 'it',
                  '?': 'she or he'},
     'plural': {'male': 'they', 'female': 'they', 'neuter': 'they',
                '?': 'they'}}}

    object_pronoun = {1:
    {'singular': {'male': 'me', 'female': 'me', 'neuter': 'me', '?': 'me'},
     'plural': {'male': 'us', 'female': 'us', 'neuter': 'us', '?': 'us'}},
    2:
    {'singular': {'male': 'you', 'female': 'you', 'neuter': 'you', '?': 'you'},
     'plural': {'male': 'you', 'female': 'you', 'neuter': 'you', '?': 'you'}},
    3:
    {'singular': {'male': 'him', 'female': 'her', 'neuter': 'it',
                  '?': 'her or him'},
     'plural': {'male': 'them', 'female': 'them', 'neuter': 'them',
                '?': 'them'}}}

    possessive_pronoun = {1:
    {'singular': {'male': 'my', 'female': 'my', 'neuter': 'my', '?': 'my'},
     'plural': {'male': 'our', 'female': 'our', 'neuter': 'our', '?': 'our'}},
    2:
    {'singular': {'male': 'your', 'female': 'your', 'neuter': 'your',
                  '?': 'your'},
     'plural': {'male': 'your', 'female': 'your', 'neuter': 'your',
                '?': 'your'}},
    3:
    {'singular': {'male': 'his', 'female': 'her', 'neuter': 'its',
                  '?': 'her or his'},
     'plural': {'male': 'their', 'female': 'their', 'neuter': 'their',
                '?': 'their'}}}

    reflexive_pronoun = {1:
    {'singular': {'male': 'myself', 'female': 'myself', 'neuter': 'myself',
                  '?': 'myself'},
     'plural': {'male': 'ourselves', 'female': 'ourselves',
                'neuter': 'ourselves', '?': 'selves'}},
    2:
    {'singular': {'male': 'yourself', 'female': 'yourself',
                  'neuter': 'yourself', '?': 'yourself'},
     'plural': {'male': 'yourself', 'female': 'yourself', 'neuter': 'yourself',
                '?': 'yourself'}},
    3:
    {'singular': {'male': 'himself', 'female': 'herself', 'neuter': 'itself',
                  '?': 'herself or himself'},
     'plural': {'male': 'themselves', 'female': 'themselves',
                'neuter': 'themselves', '?': 'themselves'}}}

    def __init__(self, tag, form, time):
        self.form = form
        self.time = time
        Word.__init__(self, tag)

    def __str__(self):
        return 'P.' + self.tag + '.' + str(self.form)

    def realize(self, concept, discourse, settings, subjects, tf):
        'Return a string realized from the word.'
        tag = self.tag
        if tag == '*':
            tag = discourse.spin['focalizer']
        if tag == settings.narrator:
            person = 1
        elif tag == settings.narratee:
            person = 2
        else:
            person = 3
        item = concept.item_at(tag ,self.time)
        if item is None:
            number = 'singular'
            gender = 'neuter'
            # If we knew this referred to an unknown person, gender = '?'
        else:
            number = item.number
            gender = item.gender
        if self.form == self.subject:
            string = self.subject_pronoun[person][number][gender]
        elif self.form == self.object:
            string = self.object_pronoun[person][number][gender]
        elif self.form == self.possessive:
            string = self.possessive_pronoun[person][number][gender]
        elif self.form == self.reflexive:
            string = self.reflexive_pronoun[person][number][gender]
        if self.form == self.subject:
            subjects = tuple(list(subjects) + [tag])
        return (string, subjects, tf)


class Verb(Word):
    'Verb, conjugated based on the subject and other settings.'

    helpers = [
        '',               #  0 Infinitive
        '',               #  1 1-S-present
        '',               #  2 1-P-present
        'am ',            #  3 1-S-present-progressive
        'are ',           #  4 1-P-present-progressive
        'have ',          #  5 1-S-present-perfect
        'have ',          #  6 1-P-present-perfect
        'have been ',     #  7 1-S-present-progressive-perfect
        'have been ',     #  8 1-P-present-progressive-perfect
        '',               #  9 1-S-past
        '',               # 10 1-P-past
        'was ',           # 11 1-S-past-progressive
        'were ',          # 12 1-P-past-progressive
        'had ',           # 13 1-S-past-perfect
        'had ',           # 14 1-P-past-perfect
        'had been ',      # 15 1-S-past-progressive-perfect
        'had been ',      # 16 1-P-past-progressive-perfect
        'will ',          # 17 1-S-future
        'will ',          # 18 1-P-future
        'will be ',       # 19 1-S-future-progressive
        'will be ',       # 20 1-P-future-progressive
        'will have ',     # 21 1-S-future-perfect
        'will have ',     # 22 1-P-future-perfect
        'had been ',      # 23 1-S-future-progressive-perfect
        'had been ',      # 24 1-P-future-progressive-perfect
        '',               # 25 2-S-present
        '',               # 26 2-P-present
        'are ',           # 27 2-S-present-progressive
        'are ',           # 28 2-P-present-progressive
        'have ',          # 29 2-S-present-perfect
        'have ',          # 30 2-P-present-perfect
        'have been ',     # 31 2-S-present-progressive-perfect
        'have been ',     # 32 2-P-present-progressive-perfect
        '',               # 33 2-S-past
        '',               # 34 2-P-past
        'were ',          # 35 2-S-past-progressive
        'were ',          # 36 2-P-past-progressive
        'had ',           # 37 2-S-past-perfect
        'had ',           # 38 2-P-past-perfect
        'had been ',      # 39 2-S-past-progressive-perfect
        'had been ',      # 40 2-P-past-progressive-perfect
        'will ',          # 41 2-S-future
        'will ',          # 42 2-P-future
        'will be ',       # 43 2-S-future-progressive
        'will be ',       # 44 2-P-future-progressive
        'will have ',     # 45 2-S-future-perfect
        'will have ',     # 46 2-P-future-perfect
        'will have been ',# 47 2-S-future-progressive-perfect
        'will have been ',# 48 2-P-future-progressive-perfect
        '',               # 49 3-S-present
        '',               # 50 3-P-present
        'is ',            # 51 3-S-present-progressive
        'are ',           # 52 3-P-present-progressive
        'has ',           # 53 3-S-present-perfect
        'have ',          # 54 3-P-present-perfect
        'has been ',      # 55 3-S-present-progressive-perfect
        'have been ',     # 56 3-P-present-progressive-perfect
        '',               # 57 3-S-past
        '',               # 58 3-P-past
        'was ',           # 59 3-S-past-progressive
        'were ',          # 60 3-P-past-progressive
        'had ',           # 61 3-S-past-perfect
        'had ',           # 62 3-P-past-perfect
        'had been ',      # 63 3-S-past-progressive-perfect
        'had been ',      # 64 3-P-past-progressive-perfect
        'will ',          # 65 3-S-future
        'will ',          # 66 3-P-future
        'will be ',       # 67 3-S-future-progressive
        'will be ',       # 68 3-P-future-progressive
        'will have ',     # 69 3-S-future-perfect
        'will have ',     # 70 3-P-future-perfect
        'will have been ',# 71 3-S-future-progressive-perfect
        'will have been ']# 72 3-P-future-progressive-perfect

    to_be = [
       'be',       #  0 Infinitive
       'am',       #  1 1-S-present
       'are',      #  2 1-P-present
       'being',    #  3 1-S-present-progressive
       'being',    #  4 1-P-present-progressive
       'been',     #  5 1-S-present-perfect
       'been',     #  6 1-P-present-perfect
       'being',    #  7 1-S-present-progressive-perfect
       'being',    #  8 1-P-present-progressive-perfect
       'was',      #  9 1-S-past
       'were',     # 10 1-P-past
       'being',    # 11 1-S-past-progressive
       'being',    # 12 1-P-past-progressive
       'been',     # 13 1-S-past-perfect
       'been',     # 14 1-P-past-perfect
       'being',    # 15 1-S-past-progressive-perfect
       'being',    # 16 1-P-past-progressive-perfect
       'be',       # 17 1-S-future
       'be',       # 18 1-P-future
       'being',    # 19 1-S-future-progressive
       'being',    # 20 1-P-future-progressive
       'been',     # 21 1-S-future-perfect
       'been',     # 22 1-P-future-perfect
       'being',    # 23 1-S-future-progressive-perfect
       'being',    # 24 1-P-future-progressive-perfect
       'are',      # 25 2-S-present
       'are',      # 26 2-P-present
       'being',    # 27 2-S-present-progressive
       'being',    # 28 2-P-present-progressive
       'been',     # 29 2-S-present-perfect
       'been',     # 30 2-P-present-perfect
       'being',    # 31 2-S-present-progressive-perfect
       'being',    # 32 2-P-present-progressive-perfect
       'were',     # 33 2-S-past
       'were',     # 34 2-P-past
       'being',    # 35 2-S-past-progressive
       'being',    # 36 2-P-past-progressive
       'been',     # 37 2-S-past-perfect
       'been',     # 38 2-P-past-perfect
       'being',    # 39 2-S-past-progressive-perfect
       'being',    # 40 2-P-past-progressive-perfect
       'be',       # 41 2-S-future
       'be',       # 42 2-P-future
       'being',    # 43 2-S-future-progressive
       'being',    # 44 2-P-future-progressive
       'been',     # 45 2-S-future-perfect
       'been',     # 46 2-P-future-perfect
       'being',    # 47 2-S-future-progressive-perfect
       'being',    # 48 2-P-future-progressive-perfect
       'is',       # 49 3-S-present
       'are',      # 50 3-P-present
       'being',    # 51 3-S-present-progressive
       'being',    # 52 3-P-present-progressive
       'been',     # 53 3-S-present-perfect
       'been',     # 54 3-P-present-perfect
       'being',    # 55 3-S-present-progressive-perfect
       'being',    # 56 3-P-present-progressive-perfect
       'was',      # 57 3-S-past
       'were',     # 58 3-P-past
       'being',    # 59 3-S-past-progressive
       'being',    # 60 3-P-past-progressive
       'been',     # 61 3-S-past-perfect
       'been',     # 62 3-P-past-perfect
       'being',    # 63 3-S-past-progressive-perfect
       'being',    # 64 3-P-past-progressive-perfect
       'be',       # 65 3-S-future
       'be',       # 66 3-P-future
       'being',    # 67 3-S-future-progressive
       'being',    # 68 3-P-future-progressive
       'been',     # 69 3-S-future-perfect
       'been',     # 70 3-P-future-perfect
       'being',    # 71 3-S-future-progressive-perfect
       'being']     # 72 3-P-future-progressive-perfect

    def __init__(self, tag, time, **keywords):
        self.default_number = None
        self.progressive = None
        self.intensive = False
        self.negated = False
        self.future_style = 'will'
        for (key, value) in keywords.items():
            setattr(self, key, value)
        self.is_be = (tag in ['be', 'am', 'are', 'is'])
        self.time = time
        Word.__init__(self, tag)

    def __str__(self):
        return 'V.' + self.tag + '.' + str(self.default_number)

    def third_person_singular(self):
        if re.search('(ch|sh|s|z|x)$', self.tag):
            new_form = self.tag + 'es'
        elif re.search('[bcdfghjklmnpqrstvwxz]y$', self.tag):
            new_form = self.tag[:-1] + 'ies'
        elif re.search('[^o]o$', self.tag):
            new_form = self.tag + 'es'
        elif self.tag == 'have':
            new_form = 'has'
        else:
            new_form = self.tag + 's'
        return new_form

    def regular_pret_pp(self):
        if self.tag[-1] == 'e':
            new_form = self.tag + 'd'
        elif re.search('[bcdfghjklmnpqrstvwxz]y$', self.tag):
            new_form = self.tag[:-1] + 'ied'
        else:
            new_form = self.tag + 'ed'
        return new_form

    def preterite(self):
        if self.tag in irregular_verb.FORMS:
            new_form = irregular_verb.FORMS[self.tag][0]
        else:
            new_form = self.regular_pret_pp()
        return new_form

    def past_participle(self):
        if self.tag in irregular_verb.FORMS:
            new_form = irregular_verb.FORMS[self.tag][1]
        else:
            new_form = self.regular_pret_pp()
        return new_form

    def present_participle(self):
        if self.tag in irregular_verb.FORMS:
            new_form = irregular_verb.FORMS[self.tag][2]
        else:
            if re.search('e$', self.tag):
                new_form = self.tag[:-1] + 'ing'
            elif re.search('ie$', self.tag):
                new_form = self.tag[:-2] + 'ying'
            else:
                new_form = self.tag + 'ing'
        return new_form

    def determine_person(self, concept, settings, subjects):
        'Check narrator/naratee and use first, second, or third person.'
        person = 3
        if self.default_number is None and len(subjects) == 1:
            only_tag = subjects[0]
            if concept.item_at(only_tag, self.time) is not None:
                if (settings.narrator is not None and
                    only_tag == settings.narrator):
                    person = 1
                elif (settings.narratee is not None and
                      only_tag == settings.narratee):
                    person = 2
        return person

    def determine_number(self, concept, _, subjects):
        "Check verb's number setting or fall back to the subjects' number."
        number = self.default_number
        if number is None:
            number = 'singular'
            if len(subjects) == 0:
                number = 'singular'
            elif len(subjects) == 1:
                only_tag = subjects[0]
                only_item = concept.item_at(only_tag, self.time)
                if only_item is None:
                    number = 'singular'
                else:
                    number = only_item.number
            else:
                number = 'plural'
        return number

    def determine_progressive(self, settings):
        "Check verb's override for progressive or use sentence settings."
        if self.progressive is None:
            progressive = settings.progressive
        else:
            progressive = self.progressive
        return progressive

    def determine_main_word(self, person, number, r_s, e_r, progressive):
        'Based on tense, produce main word and appropriate helpers.'
        i = 0
        if person > 0:
            i = (24 * person) - 23
        if r_s == 'past':
            i += 8
        if r_s == 'future':
            i += 16
        if progressive:
            i += 2
        if e_r == 'anterior': # Perfect aspect
            i += 4
        if number == 'plural':
            i += 1
        if self.is_be:
            main_word = self.to_be[i]
        else:
            main_word = self.tag
            if r_s == 'present' and number == 'singular' and person == 3:
                main_word = self.third_person_singular()
            elif r_s == 'past':
                main_word = self.preterite()
            if progressive:
                main_word = self.present_participle()
            if e_r == 'anterior':
                main_word = self.past_participle()
        return main_word, self.helpers[i]

    def apply_intensive(self, main_word, helper_words, person, number, r_s, e_r,
                        progressive):
        'Change, e.g., "eat" to "do eat".'
        if not progressive and not e_r == 'anterior' and not self.is_be:
            main_word = self.tag
            if r_s == 'present':
                if person == 3:
                    if number == 'plural':
                        helper_words = 'do '
                    else:
                        helper_words = 'does '
                else:
                    if number == 'plural':
                        helper_words = 'does '
                    else:
                        helper_words = 'do '
            if r_s == 'past':
                helper_words = 'did '
        return main_word, helper_words

    def apply_future_style(self, main_word, helper_words, person,
                           number, e_r, progressive):
        'Use "will" or "shall" to get the future.'
        if not self.future_style == 'will':
            if self.future_style == 'shall':
                helper_words = re.sub('will', 'shall', helper_words)
            if self.future_style == 'going to':
                if not e_r == 'anterior' and not progressive:
                    main_word = self.tag
                i = 0
                if person > 0:
                    i = (24 * person) - 23
                if number == 'plural':
                    i += 1
                helper_words = self.to_be[i] + ' going to '
                if progressive and e_r == 'anterior':
                    helper_words += 'have been '
                elif progressive:
                    helper_words += 'be '
                elif e_r == 'anterior':
                    helper_words += 'have '
        return main_word, helper_words

    def realize(self, concept, _, settings, subjects, tf):
        'Return a string realized from the word.'
        person = self.determine_person(concept, settings, subjects)
        number = self.determine_number(concept, settings, subjects)
        progressive = self.determine_progressive(settings)
        if hasattr(self, 'tense_er'):
            settings.tense_er = self.tense_er

        main_word, helper_words = self.determine_main_word(person, number,
                                  settings.tense_rs, settings.tense_er,
                                  progressive)
        if self.intensive or self.negated:
            main_word, helper_words = self.apply_intensive(main_word,
                                      helper_words, person, number, 
                                      settings.tense_rs, settings.tense_er,
                                      progressive)
        if self.negated:
            main_word, helper_words = negate(main_word, helper_words)
        if settings.tense_rs == 'future':
            main_word, helper_words = self.apply_future_style(main_word,
                                      helper_words, person, number,
                                      settings.tense_er, progressive)

        if settings.tense_er == 'posterior' and settings.tense_rs == 'future':
            helper_words += 'be about to '

        all_words = helper_words + main_word

        tf = True
        return (all_words, subjects, tf)


def negate(main_word, helper_words):
    'Return the negative of the verb passed in as main words and helper words.'
    if helper_words == '':
        main_word = main_word + ' not'
    else:
        helper_list = helper_words.split(' ')
        helper_list = helper_list[:1] + ['not'] + helper_list[1:]
        helper_words = ' '.join(helper_list)
    return main_word, helper_words

