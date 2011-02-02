'Represent initial and ongoing discourse features. Extended by games/stories.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import math
import re
import types

import input_model

class SpecialTime(object):
    'Adapted from extremes.py, based on PEP 326.'

    def __init__(self, comparator, name):
        object.__init__(self)
        self._comparator = comparator
        self._name = name

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self._comparator, other._comparator)
        return self._comparator

    def __repr__(self):
        return self._name

    def __lt__(self, other):
        return (self.__cmp__(other) < 0)

    def __le__(self, other):
        return (self.__cmp__(other) <= 0)

    def __gt__(self, other):
        return (self.__cmp__(other) > 0)

    def __eq__(self, other):
        return (self.__cmp__(other) == 0)

    def __ge__(self, other):
        return (self.__cmp__(other) >= 0)

    def __ne__(self, other):
        return (not self.__cmp__(other) == 0)


def reformat(string):
    'Split a long string into sentences at blank lines; collapse spaces.'
    if string is None:
        return None
    string = re.sub(' +', ' ', string.strip())
    string = re.sub(' *\n *', '\n', string)
    string = re.sub('\n\n\n+', '{}', string)
    sentence_list = []
    for paragraph in string.split('{}'):
        for sentence in paragraph.strip().split('\n\n'):
            sentence_list.append(re.sub('\n', ' ', sentence.strip()))
        sentence_list.append('')
    return sentence_list[:-1]


def splitoff(string):
    'Tokenize the string, splitting it on spaces.'
    if string[0].isupper():
        space_match = re.search(' ', string)
        if space_match is not None:
            first = string[:space_match.start()]
            rest = string[space_match.start()+1:]
            return [first] + splitoff(rest)
        else:
            return [string]
    else:
        upper_match = re.search('[A-Z]', string)
        if upper_match is not None:
            first = string[:upper_match.start()-1]
            rest = string[upper_match.start():]
            return [first] + splitoff(rest)
        else:
            return [string]


def zero_to_ten(point):
    'Maps a float with values of interest in (0.0, 1.0) to range(0,11).'
    digit = int(math.floor((point + .05) * 10))
    digit = max(0, digit)
    digit = min(10, digit)
    return digit


ZERO_TO_19 = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
              'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
              'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
              'nineteen')

HYPHEN_ONES = ('', '-one', '-two', '-three', '-four', '-five', '-six', '-seven',
               '-eight', '-nine')

TWENTY_UP = ('', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
             'eighty', 'ninety')

THOUSAND_UP = ('', ' thousand', ' million', ' billion', ' trillion',
               ' quadrillion', ' quintillion', ' sextillion', ' septillion',
               ' octillion', ' nonillion', ' decillion', ' undecillion',
               ' duodecillion', ' tredecillion', ' quattuordecillion',
               ' sexdecillion', ' septendecillion', ' octodecillion',
               ' novemdecillion', ' vigintillion')


def english_integer(val):
    'Returns an English name for any integer that has one.'
    if val < 0:
        return 'negative ' + english_integer(-val)
    elif val < 20:
        return ZERO_TO_19[val]
    elif val < 100:
        return TWENTY_UP[val / 10] + HYPHEN_ONES[val % 10]
    elif val < 1000:
        name = HYPHEN_ONES[val / 100][1:] + ' hundred'
        if val % 100 > 0:
            name += ' and ' + english_integer(val % 100)
        return name
    name = ''
    step = 0
    while val > 0:
        current = val % 1000
        if current > 0:
            name = english_integer(current) + THOUSAND_UP[step] + ' ' + name
        val = val / 1000
        step += 1
    name = name.strip()
    return name


FICTION_DEFAULTS = {
    'actions': [],
    'concepts': [],
    'cosmos': None,
    'people': []
}

SPIN_DEFAULTS = {
    'dynamic': True,
    'focalizer': '@focalizer',
    'commanded': '@commanded',
    'narratee': '@focalizer',
    'narrator': None,
    'order': 'chronicle',
    'speed': .75,
    'frequency': [('default', 'singulative')],
    'time': 'during',
    'window': 'current',
    'progressive': False,
    'perfect': False,
    'time_words': False,
    'room_name_headings': True,
    'known_directions': False,
    'template_filter': None,
    'sentence_filter': None,
    'paragraph_filter': None,
}

QUALITY_WORDS = {
    'actor': '| person',
    'clothing': ('of apparel | clothing garment threads wear wearable ' +
                 'vestment habiliment'),
    'container': '| container',
    'device': '| device mechanism machine apparatus',
    'doorway': ('liminal | doorway entry entrance entryway portal ' +
                'threshold passage'),
    'food': 'edible | food',
    'item': '| entity',
    'man': 'male | man guy dude hombre',
    'metal': 'metal metallic |',
    'of_stone': 'stone mineral rock stony |',
    'of_wood': 'wood wooden woody |',
    'person': 'human | person human individual being',
    'room': 'surrounding | area location place',
    'substance': 'amount quantity | substance',
    'thing': '| thing item object',
    'trash': 'discarded cast-off cast off | trash rubbish refuse waste junk',
    'treasure': 'precious valuable | treasure',
    'woman': 'female | woman lady gal'}


class Typography(object):
    'Parameters controlling the appearance of output.'
    indentation = '   '
    _indent_first = True
    _after_paragraph = 1
    _before_heading = 1
    _after_heading = 2
    _frame = ('== ', ' ==')
    prompt = '>'

# Try these settings to see how the typography can vary:
#    indentation = ' // '
#    _indent_first = False
#    _after_paragraph = 0
#    _before_heading = 2
#    _after_heading = 2
#    _frame = ('(<>) ', '')
#    prompt = '>) '

    def format_heading(self, string, previous, last):
        'Return the string framed and otherwise formatted as a heading.'
        string = self._frame[0] + string + self._frame[1]
        if previous is not None:
            string = ('\n' * self._before_heading) + string
        if not last:
            string += ('\n' * self._after_heading)
        return string

    def format_paragraph(self, string, previous, last):
        'Return a string indented and otherwise formatted as a paragraph.'
        if (self._indent_first or previous is not None and
            hasattr(previous, 'sentences')):
            string = self.indentation + string
        if not last:
            string += ('\n' * self._after_paragraph)
        return string


class Discourse(object):
    """The per-fiction/per-game discourse model.

    This represents all exchanges of langauge between system and interactor and
    all verbal resources that are needed to recognize, narrate and describe, 
    and output replies from the Joker."""

    typo = Typography()
    separator = [';', '.']
    determiner = '(a |an |the |my |your |his |her |that |these |one |some |)?'
    me_nouns = ['me', 'myself', 'self']
    you_nouns = ['you', 'yourself', 'self']
    indefinite = ['a', 'an', 'some']

    min = SpecialTime(-2, "minimum")
    right_before = SpecialTime(-1, "right before")
    follow = SpecialTime(0, "follow")
    right_after = SpecialTime(1, "right after")
    max = SpecialTime(2, "maximum")

    debug = False

    def __init__(self, discourse):
        self.input_list = input_model.InputList()
        self.narrated = {}
        self.spin = discourse['spin']
        self.initial_spin = discourse['spin']
        self.metadata = discourse['metadata']
        if 'prologue' in self.metadata:
            self.metadata['prologue'] = reformat(self.metadata['prologue'])
        self.action_templates = []
        for i in ['initial_inputs', 'action_templates']:
            if i in discourse:
                setattr(self, i, discourse[i])
        for i in ['command_grammar', 'compass', 'verb_representation']:
            if i in discourse:
                for key, new_value in discourse[i].items():
                    getattr(self, i)[key] = new_value
        self.givens = set()
        self.english_to_link = {}
        for (relation, names) in self.link_to_english.items():
            for name in names:
                self.english_to_link[name] = relation
        self.commands = []
        for action in self.command_grammar:
            action_parts = action.split()
            for rule in self.command_grammar[action]:
                rule_parts = splitoff(rule)
                self.commands += [(action_parts, rule_parts)]
        self.command_canonical = {}
        for action in self.command_grammar:
            verb = action.split()[0]
            self.command_canonical[verb] = self.command_grammar[action][0]

    def mark_narrated(self, action_id):
        'Tally the number of times a particular action has been narrated.'
        if action_id not in self.narrated:
            self.narrated[action_id] = 1
        else:
            self.narrated[action_id] += 1

    @staticmethod
    def list_phrases(phrases, delimiter=',', conjunction='and',
                     serial_comma=True):
        'Creates an English list, delimited and conjoined as specified.'
        for i in range(0, len(phrases)):
            # Convert any integers in the list to strings here
            if type(phrases[i]) == types.IntType:
                phrases[i] = str(phrases[i])
        if len(phrases) >= 2:
            phrases[-1] = conjunction + ' ' + phrases[-1]
        joiner = delimiter + ' '
        if len(phrases) <= 2:
            joiner = ' '
        if serial_comma:
            complete_list = joiner.join(phrases)
        else:
            complete_list = joiner.join(phrases[:-1]) + ' ' + phrases[-1]
        return complete_list

    verb_representation = {}

    command_grammar = {
        'BURN ACCESSIBLE':
         ['burn ACCESSIBLE',
          '(ignite|torch) ACCESSIBLE'],

        'CLOSE ACCESSIBLE':
         ['close ACCESSIBLE',
          '(close|shut)( up)? ACCESSIBLE'],

        'DOFF WORN':
         ['take off WORN',
          '(doff|remove|take off|shed|strip off) WORN',
          '(take|strip) WORN off'],

        'DRINK ACCESSIBLE':
         ['drink ACCESSIBLE',
          '(gulp|imbibe|sip|swallow) ACCESSIBLE'],

        'DRINK_FROM ACCESSIBLE':
         ['drink from ACCESSIBLE',
          '(gulp|imbibe|sip|swallow) from ACCESSIBLE'],

        'DRINK_IT_FROM ACCESSIBLE':
         ['drink ACCESSIBLE from ACCESSIBLE',
          '(gulp|imbibe|sip|swallow) ACCESSIBLE from ACCESSIBLE'],

        'DROP DESCENDANT':
         ['(discard|put down|release) DESCENDANT',
          'put DESCENDANT down',
          '(drop|dump)( off)? DESCENDANT'],

        'EAT ACCESSIBLE':
         ['eat ACCESSIBLE',
          '(consume|devour|ingest|yum) ACCESSIBLE'],

        'ENTER ACCESSIBLE':
         ['enter ACCESSIBLE',
          '(go|walk) (in|into|through) ACCESSIBLE'],

        'EXPLODE ACCESSIBLE':
         ['blow ACCESSIBLE up',
          '(explode|blow up|detonate) ACCESSIBLE'],

        'EXTINGUISH ACCESSIBLE':
         ['extinguish ACCESSIBLE',
          'snuff( out)? ACCESSIBLE'],

        'FEED ACCESSIBLE ACCESSIBLE':
         ['feed ACCESSIBLE to ACCESSIBLE',
          'feed ACCESSIBLE( with)? ACCESSIBLE'],

        'FILL_WITH ACCESSIBLE ACCESSIBLE':
         ['fill ACCESSIBLE with ACCESSIBLE',
          'fill( up)? ACCESSIBLE with ACCESSIBLE'],

        'FILL_FROM ACCESSIBLE ACCESSIBLE':
         ['fill ACCESSIBLE from ACCESSIBLE',
          'fill( up)? ACCESSIBLE (from|out of) ACCESSIBLE'],

        'FILL_WITH_FROM ACCESSIBLE ACCESSIBLE ACCESSIBLE':
         ['fill ACCESSIBLE with ACCESSIBLE from ACCESSIBLE',
          'fill( up)? ACCESSIBLE with ACCESSIBLE (from|out of) ACCESSIBLE'],

        'FREE NOT-DESCENDANT':
         ['free NOT-DESCENDANT',
          '(extract|extricate|liberate|release) NOT-DESCENDANT'],

        'FREE_FROM NOT-DESCENDANT ACCESSIBLE':
         ['free NOT-DESCENDANT from ACCESSIBLE',
          '(extract|extricate|free|liberate|release) '+
          'NOT-DESCENDANT (from|off) ACCESSIBLE'],

        'FREEZE':
         ['freeze',
          '(remain|stand)( extremely| very)? still'],

        'GIVE ACCESSIBLE ACCESSIBLE':
         ['give ACCESSIBLE to ACCESSIBLE',
          '(give|offer|provide|supply) ACCESSIBLE ACCESSIBLE',
          '(offer|provide|supply) ACCESSIBLE to ACCESSIBLE'],

        'INVENTORY':
         ['take inventory',
          '(inventory|inv|i)'],

        'ILLUMINATE ACCESSIBLE':
         ['light ACCESSIBLE',
          '(light up|illuminate) ACCESSIBLE'],

        'KICK ACCESSIBLE':
         ['kick ACCESSIBLE'],

        'LEAVE DIRECTION':
         ['go DIRECTION',
          '(continue|depart|explore|head|leave|move|proceed|stride|' +
          'travel|run|walk)( to)? DIRECTION'],

        'LEAVE_FROM ACCESSIBLE':
         ['leave ACCESSIBLE',
          '(depart|exit|get out of|leave)( from)? ACCESSIBLE'],

        'LISTEN':
         ['listen',
          '(eavesdrop|hear)'],

        'LISTEN_TO NEARBY':
         ['listen to NEARBY',
          '(hear|listen)( to)? NEARBY'],

        'LOCK ACCESSIBLE':
         ['lock ACCESSIBLE',
          '(lock down|lock up|engage) ACCESSIBLE'],

        'LOOK':
         ['look around',
          '(gaze|inspect|l|look|observe|peer|view)' +
          '( all)?( around| about| up and down| back and forth| to and fro)?'],

        'LOOK_AT NEARBY':
         ['look at NEARBY',
          '(examine|inspect|observe|ogle|peer at|view|x) NEARBY',
          '(l|look|stare) (at|on|in|through)? NEARBY',
          'gaze upon NEARBY'],

        'OPEN_UP ACCESSIBLE':
         ['open ACCESSIBLE',
          'open up ACCESSIBLE',
          'open ACCESSIBLE up',
          '(swing|throw) ACCESSIBLE open'],

        'OPEN_WITH ACCESSIBLE ACCESSIBLE':
         ['open ACCESSIBLE with ACCESSIBLE',
          'open up ACCESSIBLE with ACCESSIBLE',
          'open ACCESSIBLE up with ACCESSIBLE',
          '(swing|throw) ACCESSIBLE open with ACCESSIBLE'],

        'POUR_IN ACCESSIBLE ACCESSIBLE':
         ['pour ACCESSIBLE into ACCESSIBLE',
          'pour( out)? ACCESSIBLE (in|into|to) ACCESSIBLE',
          'decant ACCESSIBLE (in|into|to) ACCESSIBLE'],

        'POUR_IN_FROM ACCESSIBLE ACCESSIBLE ACCESSIBLE':
         ['pour ACCESSIBLE from ACCESSIBLE into ACCESSIBLE',
          'pour( out)? ACCESSIBLE (from|out of) ACCESSIBLE '+
              '(in|into|to) ACCESSIBLE',
          'decant ACCESSIBLE (from|out of) ACCESSIBLE '+
              '(in|into|to) ACCESSIBLE'],

        'POUR_ON ACCESSIBLE ACCESSIBLE':
         ['pour ACCESSIBLE onto ACCESSIBLE',
          'pour( out)? ACCESSIBLE (on|onto|upon) ACCESSIBLE'],

        'POUR_ON_FROM ACCESSIBLE ACCESSIBLE ACCESSIBLE':
         ['pour ACCESSIBLE from ACCESSIBLE onto ACCESSIBLE',
          'pour( out)? ACCESSIBLE (from|out of) ACCESSIBLE '+
              '(on|onto|upon) ACCESSIBLE'],

        'PRESS ACCESSIBLE':
         ['push ACCESSIBLE',
          'press ACCESSIBLE'],

        'PUT_IN ACCESSIBLE ACCESSIBLE':
         ['put ACCESSIBLE into ACCESSIBLE',
          '(put|place) ACCESSIBLE (in|into) ACCESSIBLE'],

        'PUT_ON ACCESSIBLE ACCESSIBLE':
         ['put ACCESSIBLE onto ACCESSIBLE',
          '(put|place) ACCESSIBLE (atop|on|onto) ACCESSIBLE'],

        'READ ACCESSIBLE':
         ['read ACCESSIBLE',
          '(read|peruse|scan|skim) ACCESSIBLE'],

        'REMOVE NOT-DESCENDANT':
         ['remove NOT-DESCENDANT'],

        'REMOVE_FROM NOT-DESCENDANT ACCESSIBLE':
         ['remove NOT-DESCENDANT from ACCESSIBLE',
          'remove NOT-DESCENDANT (off|out) ACCESSIBLE'],

        'SHAKE ACCESSIBLE':
         ['shake ACCESSIBLE',
          '(agitate|brandish|flourish|shake|swing|wave) ACCESSIBLE (all )?' +
          '(around|about|up and down|back and forth|to and fro)?',
          'move ACCESSIBLE ' +
          '(all )?(around|about|up and down|back and forth|to and fro)'],

        'SHAKE_AT ACCESSIBLE NEARBY':
         ['shake ACCESSIBLE at NEARBY',
          '(agitate|brandish|flourish|shake|swing|wave) ACCESSIBLE (all )?' +
          '(around|about|up and down|back and forth|to and fro)?' +
          '(at|to|toward) NEARBY',
          'move ACCESSIBLE ' +
          '(all )?(around|about|up and down|back and forth|to and fro) ' +
          '(at|to|toward) NEARBY'],

        'SMELL':
         ['smell',
          '(smell|sniff)( all)?( around| about)?'],

        'SMELL_OF NEARBY':
         ['smell NEARBY',
          '(nose|scent|smell|sniff|snuff|snuffle|whiff)( of)? ACCESSIBLE'],

        'STRIKE ACCESSIBLE':
         ['attack ACCESSIBLE',
          '(break|destroy|engage|fight|hit|kill|murder|shatter|' + 
          'slaughter|slay|smack|smash) ACCESSIBLE',
          'strike( down)? ACCESSIBLE',
          'strike ACCESSIBLE down'],

        'STRIKE_WITH ACCESSIBLE DESCENDANT':
         ['attack ACCESSIBLE with DESCENDANT',
          '(break|destroy|fight|hit|kill|murder|shatter|slaughter|' +
          'slay|strike|smack|smash) ACCESSIBLE (with|using) DESCENDANT',
          'strike DESCENDANT (against|at) ACCESSIBLE'],

        'TAKE NOT-DESCENDANT':
         ['pick NOT-DESCENDANT up',
          '(carry|keep|get|obtain|pick up|steal|take|tote) NOT-DESCENDANT'],

        'TASTE ACCESSIBLE':
         ['taste ACCESSIBLE',
          '(sample|smack) ACCESSIBLE'],

        'TELL ACCESSIBLE STRING':
         ['tell ACCESSIBLE STRING',
          '(chant|mumble|say|shout|sing|tell|utter) STRING to ACCESSIBLE',
          '(chant|mumble|say|sing|utter) to ACCESSIBLE STRING'],

        'THROW ACCESSIBLE ACCESSIBLE':
         ['throw ACCESSIBLE to ACCESSIBLE',
          '(hurl|throw|toss) ACCESSIBLE (at|to|toward) ACCESSIBLE'],

        'TOGGLE ACCESSIBLE':
         ['toggle ACCESSIBLE',
          '(flip|switch) ACCESSIBLE'],

        'TOUCH ACCESSIBLE':
         ['touch ACCESSIBLE',
          '(caress|feel|rub|stroke) ACCESSIBLE'],

        'TOUCH_WITH ACCESSIBLE DESCENDANT':
         ['touch ACCESSIBLE with DESCENDANT',
          '(caress|rub|touch) ACCESSIBLE (with|using) DESCENDANT'],

        'TURN_OFF ACCESSIBLE':
         ['turn off ACCESSIBLE',
          '(deactivate|stop) ACCESSIBLE',
          'power down ACCESSIBLE',
          'switch off ACCESSIBLE',
          '(switch|turn) ACCESSIBLE off',
          'shut ACCESSIBLE (off|down)'],

        'TURN_ON ACCESSIBLE':
         ['turn on ACCESSIBLE',
          'activate ACCESSIBLE',
          '(boot|start)( up)? ACCESSIBLE',
          '(boot|start) ACCESSIBLE up',
          '(power up|switch on) ACCESSIBLE',
          '(switch|turn) ACCESSIBLE on'],

        'TURN_TO ACCESSIBLE STRING':
         ['turn ACCESSIBLE to STRING',
          '(rotate|revolve|set|swivel|turn) ACCESSIBLE (at|to|toward) STRING'],

        'UNLOCK ACCESSIBLE':
         ['unlock ACCESSIBLE',
          'disengage ACCESSIBLE'],

        'UTTER STRING':
         ['say STRING',
          '(chant|mumble|pronounce|shout|sing|tell|utter) STRING'],

        'UTTER STRING STRING':
         ['say STRING STRING',
          '(chant|mumble|pronounce|shout|sing|tell|utter) STRING STRING'],

        'UTTER STRING STRING STRING':
         ['say STRING STRING STRING',
          '(chant|mumble|pronounce|shout|sing|tell|utter) STRING STRING ' + 
             'STRING'],

        'UTTER STRING STRING STRING STRING':
         ['say STRING STRING STRING STRING',
          '(chant|mumble|pronounce|shout|sing|tell|utter) STRING STRING ' + 
             'STRING STRING'],

        'WAIT':
         ['wait',
          'z'],

        'WANDER':
         ['wander around',
          '(explore|go|move|move about|ramble|rove|run|stroll|walk|wander)'],

        'WAVE':
         ['wave',
          '(beckon|gesture|gesticulate|wave)'],

        'WAVE_AT NEARBY':
         ['wave at NEARBY',
          '(beckon|gesture|gesticulate|wave) (at|to|toward) NEARBY'],

        'WEAR ACCESSIBLE':
         ['wear ACCESSIBLE',
          '(don|put on) ACCESSIBLE',
          'put ACCESSIBLE on']}

    debugging_verbs = {
        'world': 'world_info',
        'concept': 'concept_info',
        'focal': 'concept_info',
        'directives': 'count_directives',
        'inputs': 'inputs',
        'll': 'light',
        'lightlevel': 'light',
        'level': 'light',
        'narrating': 'narrating',
        'spin': 'narrating',
        'telling': 'narrating',
        'prologue': 'prologue',
        'recount': 'recount',
        'room': 'room_name',
        'location': 'room_name',
        'place': 'room_name',
        'ticks': 'ticks',
        'title': 'title',
        'unrecognized': 'count_unrecognized'}

    directive_verbs = {
        '#': 'comment',
        '*': 'comment',
        'commands': 'count_commands',
        'comment': 'comment',
        'turns': 'count_commands',
        'end': 'terminate',
        'exits': 'exits',
        'stop': 'terminate',
        'terminate': 'terminate',
        'q': 'terminate',
        'quit': 'terminate',
        'reset': 'restart',
        'restart': 'restart',
        'resume': 'resume',
        'restore': 'restore',
        'bookmark': 'save',
        'pause': 'save',
        'save': 'save',
        'suspend': 'save',
        'score': 'score',
        'undo': 'undo'}

    spin_arguments = {
        'focalize': 'focalizer',
        'focalized': 'focalizer',
        'focalizer': 'focalizer',
        'focal': 'focalizer',
        'fc': 'focalizer',
        'command': 'commanded',
        'commanded': 'commanded',
        'cc': 'commanded',
        'player': 'player',
        'pc': 'player',
        'narrator': 'narrator',
        'narratee': 'narratee',
        'order': 'order',
        'perfect': 'perfect',
        'progressive': 'progressive',
        'speed': 'speed',
        'time': 'time',
        'tw': 'timewords',
        'timewords': 'timewords',
        'uses': 'uses',
        'load': 'uses',
        'dynamic': 'dynamic'}

    compass = {
        'n': 'north',
        'north': 'north',
        'ne': 'northeast',
        'northeast': 'northeast',
        'e': 'east',
        'east': 'east',
        'se': 'southeast',
        'southeast': 'southeast',
        's': 'south',
        'south': 'south',
        'sw': 'southwest',
        'southwest': 'southwest',
        'w': 'west',
        'west': 'west',
        'nw': 'northwest',
        'northwest': 'northwest',
        'u': 'up',
        'up': 'up',
        'ascend': 'up',
        'd': 'down',
        'down': 'down',
        'descend': 'down',
        'in': 'in',
        'into': 'in',
        'inside': 'in',
        'within': 'in',
        'out': 'out',
        'outside': 'out'}

    link_to_english = {
        'on': ['on', 'on top of', 'onto', 'upon'],
        'of': ['held by', 'of'],
        'in': ['in', 'inside', 'into', 'within'],
        'part_of': ['on', 'part of', 'affixed to'],
        'through': ['through']}

    feature_to_english = {
        'on': lambda i: ('off', 'on')[i],
        'open': lambda i: ('closed', 'open')[i],
        'glow': lambda i: ('unlit', 'barely glowing', 'weakly glowing',
                           'dimly shining', 'glowing', 'shining',
                           'brightly glowing', 'brightly shining', 'brilliant',
                           'radiant', 'searingly radiant')[zero_to_ten(i)],
        'locked': lambda i: ('unlocked', 'locked')[i],
        'intact': lambda i: ('trampled', 'pristine')[i],
        'angry': lambda i: ('calm', 'enraged')[i],
        'setting': lambda i: str(i),
        'word': lambda i: i.upper()}

    failure_to_english = {
        'actor_in_play': '[agent/s] [is/not/v] in the world',
        'allowed_in': '[direct/s] [fit/do/not/v] into [indirect/o]',
        'allowed_of': '[indirect/s] [is/not/v] able to hold [direct/o]',
        'allowed_on': '[direct/s] [fit/do/not/v] onto [indirect/o]',
        'allowed_through': '[direct/s] [fit/do/not/v] through [indirect/o]',
        'can_access_direct': "[direct/s] [is/not/v] within [agent's] reach",
        'can_access_indirect': "[indirect/s] [is/not/v] within [agent's] reach",
        'can_access_flames': '[agent/s] [have/not/v] anything to light ' + 
                             '[direct/o] with',
        'can_access_key': "the key [is/not/1/v] within [agent's] reach",
        'configure_to_different': '[agent/s] [try/ing/v] to move [direct/o]' +
                                  ' to where [direct/s] already [is/v]',
        'enough_light': 'it [is/1/v] too dark for [agent/s] to see',
        'exit_exists': '[agent/s] [is/not/v] able to find an exit to the' + 
                        ' [direction]',
        'good_enough_view': '[agent/s] [do/v] not have a good enough view ' +
                            'from [here]',
        'has_feature': '[direct/s] [is/not/v] suitable for that',
        'has_value': '',
          # Don't add anything; in the microplanner this will be overwritten
          # to name the value of the feature which is required.
        'item_in_play': '[direct/s] [is/not/v] in the world',
        'item_prominent_enough': '[direct/s] [is/not/v] prominent enough ' +
                                 'to pick out',
        'line_of_sight': '[direct/s] [is/not/v] visible',
        'modify_to_different': '[agent/s] [try/ing/v] to chage [direct/o]' +
                               ' to a state [direct/s] already [is/v] in',
        'never_configure_doors': '[direct/s] [is/not/v] repositionable',
        'never_configure_parts': '[agent/s] [is/not/v] able to detach' +
                                 ' [direct/o]',
        'never_configure_sharedthings': '[direct/s] [is/not/v] repositionable',
        'never_permanently_locked': 'there [is/1/v] no way to unlock' +
                                    ' [direct/o]',
        'no_new_parent': 'WHEN DOES THIS HAPPEN?',
        'not_own_descendant': 'things [go/do/not/2/v], directly or ' +
                              ' otherwise, into or onto themselves',
        'parent_is': '[direct/s] [is/not/v] [old_link] [old_parent/o]',
        'prevented_by': '',
          # Don't add anything; the preventing action will be narrated and
          # will explain why this action was prevented.
        'rooms_cannot_move': 'entire locations [move/do/not/2/v]',
        'substance_contained': '[indirect/s] [is/not/v] able to hold' + 
                               ' [direct/o]',
        'value_unchanged': '[direct/s] [is/v] already [feature/direct/o]'}

    sense_verb = {
        'sight': 'see',
        'touch': 'feel',
        'hearing': 'hear',
        'smell': 'smell',
        'taste': 'taste'}

