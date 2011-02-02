'Adventure in Style, based on the classic game and an unusual book.'

__author__ = 'Nick Montfort (based on works by Crowther, Woods, and Queneau)'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

from random import random, randint, choice

from item_model import Actor, Door, Room, SharedThing, Substance, Thing
from action_model import Behave, Configure, Modify, Sense
from joker import update_spin
import can
import when

discourse = {

    'command_grammar': {
        'CAGE ACCESSIBLE':
         ['cage ACCESSIBLE',
          '(cage in|entrap|trap) ACCESSIBLE'],

        'OIL ACCESSIBLE':
         ['oil ACCESSIBLE',
          'lubricate ACCESSIBLE'],

        'UNCHAIN ACCESSIBLE':
         ['(unchain|unleash) ACCESSIBLE'],

        'WATER ACCESSIBLE':
         ['water ACCESSIBLE']},

    'compass': {
        'across': 'across',
        'barren': 'barren',
        'bed': 'bed',
        'bedquilt': 'bedquilt',
        'building': 'house',
        'broken': 'broken',
        'canyon': 'canyon',
        'cavern': 'cavern',
        'climb': 'climb',
        'cobble': 'cobble',
        'crack': 'crack',
        'crawl': 'crawl',
        'dark': 'dark',
        'debris': 'debris',
        'depression': 'depression',
        'downstream': 'downstream',
        'enter': 'enter',
        'entrance': 'entrance',
        'exit': 'leave',
        'floor': 'floor',
        'forest': 'forest',
        'fork': 'fork',
        'giant': 'giant',
        'gully': 'gully',
        'hall': 'hall',
        'hill': 'hill',
        'hole': 'hole',
        'house': 'house',
        'in': 'in',
        'jump': 'jump',
        'leave': 'leave',
        'left': 'left',
        'low': 'low',
        'nowhere': 'nowhere',
        'onward': 'onward',
        'oriental': 'oriental',
        'outdoors': 'outdoors',
        'over': 'over',
        'pit': 'pit',
        'plover': 'plover',
        'plugh': 'plugh',
        'reservoir': 'reservoir',
        'right': 'right',
        'rock': 'rock',
        'room': 'room',
        'secret': 'secret',
        'shell': 'shell',
        'slab': 'slab',
        'slit': 'slit',
        'stair': 'stair',
        'stream': 'stream',
        'surface': 'surface',
        'tunnel': 'tunnel',
        'upstream': 'upstream',
        'valley': 'valley',
        'view': 'view',
        'wall': 'wall',
        'xyzzy': 'xyzzy',
        'y2': 'y2'},

    'metadata': {
        'title': 'Adventure in Style',
        'headline': 'Two Great Tastes that Taste Great Together',
        'people': [('by', 'Nick Montfort'),
                   ('based on Adventure by',
                    'Will Crowther and Don Woods'),
                   ('and based on Exercises in Style by',
                    'Raymond Queneau')],
        'prologue': """Welcome to Adventure!!

        Note that the cave entrance is SOUTH, SOUTH, SOUTH from here."""},

    'spin': {
        'commanded': '@adventurer',
        'focalizer': '@adventurer',
        'narratee': '@adventurer'},

    'verb_representation': {
        'examine': '[agent/s] [take/v] a look at [direct/o]',
        'leave': '[agent/s] [set/v] off [direction]ward',
        'scare': '[agent/s] [scare/v] [direct/o] away',
        'appear': '[direct/s] [appear/v]',
        'block': '[direct/s] [are/not/v] able to get by [agent/o]',
        'flit': '[agent/s] [flit/v] away, remaining in the general area',
        'flee': '[agent/s] [flee/v], trembling (or at least wriggling)',
        'blast': 'the treasure valut [blast/1/v] open -- Victory!',
        'disappear': '[direct/s] [scurry/v] away out of sight',
        'set_closing': 'a voice [boom/v], "The cave will be closing soon!"'}}


def COMMAND_cage(agent, tokens, _):
    'to confine in a cage'
    return Configure('cage', agent,
                     template=('[agent/s] [put/v] [direct/o] in ' +
                               '[indirect/o]'),
                     direct=tokens[1], new=('in', '@cage'))


def COMMAND_oil(agent, tokens, concept):
    'to pour oil onto something, such as a rusty door'
    direct = '@cosmos'
    for held in concept.descendants(agent):
        if held[:4] == '@oil':
            direct = held
    return Configure('pour', agent,
                     template='[agent/s] [oil/v] [indirect/o]',
                     direct=direct, new=('on', tokens[1]))


def COMMAND_turn_to(agent, tokens, concept):
    'to rotate; to revolve; to make to face differently'
    if tokens[1] == '@lamp':
        tokens[1] = '@dial'
    try:
        value = int(tokens[2])
    except ValueError:
        value = 1
    if value < 1 or value > len(variation):
        value = 1
    return Modify('turn', agent,
                  template='[agent/s] [turn/v] [direct/o] to ' + str(value),
                  direct=tokens[1], feature='setting', new=value)


def COMMAND_unchain(agent, tokens, _):
    'to free from being restrained by a chain'
    return Modify('unchain', agent,
                  direct=tokens[1], feature='chained', new=False)


def COMMAND_water(agent, tokens, concept):
    'to pour water onto something, such as a plant'
    direct = '@cosmos'
    for held in concept.descendants(agent):
        if held[:6] == '@water':
            direct = held
    return Configure('pour', agent,
                     template='[agent/s] [water/v] [indirect/o]',
                     direct=direct, new=('on', tokens[1]))

initial_actions = [
    Sense('examine', '@adventurer', direct='@end_of_road', modality='sight')]

all_treasures = ['@nugget', '@diamonds', '@bars', '@jewelry', '@coins',
                 '@eggs', '@trident', '@vase', '@emerald', '@pyramid',
                 '@pearl', '@chest', '@rug', '@spices', '@chain']


interjections = ['uh', 'uh', 'uh', 'um', 'um', 'er']

def double_template(phrases):
    new_phrases = []
    for phrase in phrases.split():
        new_phrases.append(phrase)
        if phrase[-3:] == '/o]':
            new_phrases += ['and', choice(['the radiant being',
                'the majestic presence', 'the tremendous aura',
                'the incredible unity', 'the solemn physicality',
                'the uplifting nature', 'the full existence',
                'the all-singing, all-dancing being', 'the profound air',
                'the ineffable quality', 'the unbearable lightness',
                'the harmonious flow', 'the powerful memory']), 
                'of', phrase]
    return ' '.join(new_phrases)

def hesitant_sentence(phrases):
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

def surprise_sentence(phrases):
    chosen = randint(1,8)
    if chosen == 1:
        phrases = [choice(['whoa', 'dude']) + ','] + phrases
    elif chosen == 2:
        if not phrases[-1][-1] in ',.:;':
            phrases[-1] += ','
        phrases = phrases + [choice(['man', 'dude',])]
    phrases[-1] = phrases[-1] + '!'
    return phrases

def surprise_paragraph(paragraphs):
    chosen = randint(1,3)
    if chosen == 1:
        paragraphs = paragraphs + choice(['Amazing!', 'Wow!', 'Awesome!',
                                          'Out of this world!', 'Incredible!'])
    return paragraphs

def valley_sentence(phrases):
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

variation = [
    ['typical', {}],
    ['memoir', {'narrator': '@adventurer', 'narratee': None, 'time': 'after'}],
    ['royal', {'narrator': '@adventurer', 'narratee': None,
               '@adventurer': [('@adventurer',  'number', 'plural')]}],
# NEXT-STEPS
# This '@adventurer' entry doesn't do anything now; it's an idea for now
# spin files might override aspects of the simulated world to allow tellings
# of this sort.
    ['impersonal', {'narrator': None, 'narratee': None}],
    ['prophecy', {'time': 'before'}],
    ['retrograde', {'order': 'retrograde', 'window': 7,
                    'room_name_headings': False, 'time_words': True}],
# NEXT-STEPS
# 'time-words' are baked into the Microplanner right now. It would be better
# to pass in a dictionary with lists of words that can be selected from at
# random, at the least -- perheps with functions that would return
# appropriate words. 
    ['flashback', {'order': 'analepsis'}],
    ['double entry', {'narratee': None, 'template_filter': [double_template]}],
    ['oriented', {'known_directions': True, 'room_name_headings': False}],
    ['in medias res', {'progressive': True}],
    ['finished by then', {'perfect': True, 'time': 'before'}],
    ['tell it to the lamp', {'narrator': None, 'narratee': '@lamp'}],
]


class Cosmos(Actor):

    def __init__(self, tag, **keywords):
        self.closing = 0
        self.lamp_controls_changed = False
        Actor.__init__(self, tag, **keywords)

    def update_spin(self, world, discourse):
        if world.item['@lamp'].on and self.lamp_controls_changed:
            discourse.spin = discourse.initial_spin.copy()
            _, spin = variation[world.item['@dial'].setting - 1]
            discourse.spin = update_spin(discourse.spin, spin)
            if world.item['@hesitant'].on:
                discourse.spin['sentence_filter'] += [hesitant_sentence]
            if world.item['@surprise'].on:
                discourse.spin['sentence_filter'] += [surprise_sentence]
                discourse.spin['paragraph_filter'] += [surprise_paragraph]
            if world.item['@valley_girl'].on:
                discourse.spin['sentence_filter'] += [valley_sentence]
            if variation[world.item['@dial'].setting - 1][0] == 'royal':
                 world.item['@adventurer'].number = 'plural'
                 adv_concept = world.concept['@adventurer']
                 adv_concept.item['@adventurer'].number = 'plural'
            else:
                 world.item['@adventurer'].number = 'singular'
                 adv_concept = world.concept['@adventurer']
                 adv_concept.item['@adventurer'].number = 'singular'
            self.lamp_controls_changed = False
        return discourse.spin

    def react(self, world, basis):
        actions = []
        if (basis.modify and basis.direct == '@dial' and
            basis.feature == 'setting') or (basis.modify and
            basis.direct == '@lamp' and basis.feature == 'on' and
            basis.new_value == True):
            self.lamp_controls_changed = True
        elif (basis.modify and basis.direct in ['@hesitant', '@surprise',
                                                '@valley_girl']):
            self.lamp_controls_changed = True
        if (not world.item['@troll'].scared and
            not world.item['@troll'].parent == '@northeast_side_of_chasm'
            and basis.configure and basis.direct == '@adventurer' and
            basis.new_parent == '@northeast_side_of_chasm'):
            appear = Configure('appear', '@cosmos',
                               template='[direct/s] [appear/v]',
                               direct='@troll',
                               new=('in', '@northeast_side_of_chasm'),
                               salience=0.9)
            actions.append(Modify('change_blocked', '@cosmos',
                                 direct='@troll', feature='blocked',
                                 new=['cross', 'over', 'southwest'],
                                 salience=0.1))
        if (self.closing > 0 and world.ticks == self.closing):
            actions.append(Configure('appear', '@cosmos',
                                    template=('[direct/s] [appear/v] in ' +
                                              '[indirect/o]'),
                                    direct='@adventurer',
                                    new=('in', '@northeast_end'),
                                    salience=0.9))
        return actions

cosmos = Cosmos('@cosmos', called='creation', referring=None,
                allowed=can.have_any_item)


class Lamp(Thing):
    '@lamp is the only instance.'

    def react(self, _, basis):
        'Increase/decrease the light emitted when turned on/off.'
        actions = []
        if (basis.modify and basis.direct == str(self) and
            basis.feature == 'on'):
            # If turned on, make it glow; otherwise, have it stop glowing.
            if basis.new_value:
                actions.append(Modify('light', basis.agent,
                                      direct=str(self), feature='glow',
                                      new=0.6, salience=0.1))
            else:
                actions.append(Modify('extinguish', basis.agent,
                                      direct=str(self), feature='glow',
                                      new=0.0, salience=0.1))
        return actions


class Dial(Thing):
    '@dial is the only instance.'

    def react(self, _, basis):
        'Select the appropraite word for the new variation.'
        actions = []
        if (basis.modify and basis.direct == str(self) and
            basis.feature == 'setting'):
            (name, _) = variation[basis.new_value - 1]
            actions.append(Modify('select', basis.agent,
                                  template=('[agent/s] [select/v]' +
                                   ' [begin-caps]"' + name + '"'),
                                  direct=basis.direct, feature='word',
                                  new=name))
        return actions


class Button(Thing):
    '@button is the only instance.'

    def react(self, world, basis):
        'Blast and win the game if the black rod is in place.'
        actions = []
        if (basis.behave and hasattr(basis, 'direct') and
            basis.direct == str(self) and basis.force > 0.1 and
            str(world.room_of('@black_rod')) == '@northeast_end'):
            blast = Behave('blast', '@cosmos',
                           direct='@southwest_end', force=1)
            # The adventurer won't sense the action unless it has something
            # visible, such as the room, as its direct object.
            blast.final = True
            actions.append(blast)
        return actions


class Guardian(Thing):
    """There are several subclasses representing different guardians."""

    def __init__(self, tag, **keywords):
        self.alive = True
        Thing.__init__(self, tag, **keywords)

    def prevent(self, world, basis):
        """Block exits."""
        if (basis.behave and basis.verb == 'leave' and
            basis.way in self.blocked):
            return True
        return False


class Snake(Guardian):
    '@snake is the only instance.'

    def react(self, world, basis):
        'Flee if the bird arrives.'
        actions = []
        if (basis.configure and basis.direct == '@bird' and
            basis.new_parent == world.room_of(str(self))):
            actions.append(Configure('flee', '@cosmos',
                                     template='[@snake/s] [flee/v]',
                                     direct='@snake', new=('of', '@cosmos'),
                                     salience=0.9))
        return actions + Guardian.react(self, world, basis)


class Dragon(Guardian):
    '@dragon is the only instance.'

    def react(self, world, basis):
        'Perish if struck, move off of rug, change description.'
        actions = []
        if (basis.behave and basis.direct == str(self) and
            basis.force > 0.3):
            actions.append(Modify('kill', basis.agent,
                                  direct=str(self), feature='alive',
                                  new=False, salience=0.9))
            actions.append(Configure('fall', '@cosmos',
                                     direct=str(self),
                                     new=('in',
                                          str(world.room_of(str(self)))),
                                     salience=0.1))
            sight = """
            [this] [is/1/v] just a huge, dead dragon, flopped on the ground"""
            actions.append(Modify('change_appearance', basis.agent,
                                 direct=str(self), feature='sight', new=sight,
                                 salience=0.0))
        return actions + Guardian.react(self, world, basis)


class Troll(Guardian):
    '@troll is the only instance.'

    def __init__(self, tag, **keywords):
        self.scared = False
        Guardian.__init__(self, tag, **keywords)

    def react(self, world, basis):
        actions = []
        'Disappear if given a treasure.'
        if (basis.configure and basis.new_parent == str(self) and
             'treasure' in world.item[basis.direct].qualities):
            actions.append(Configure('disappear', '@cosmos',
                                    template='[direct/s] [disappear/v]',
                                    direct='@troll', new=('of', '@cosmos'),
                                    salience=0.9))
        'Flee if scared.'
        if (basis.modify and basis.direct == str(self) and
            basis.feature == 'scared' and basis.new_value == True):
            actions.append(Configure('flee', '@cosmos',
                                     template='[@troll/s] [flee/v]',
                                     direct='@troll', new=('of', '@cosmos'),
                                     salience=0.9))
        return actions + Guardian.react(self, world, basis)


class Bear(Actor):
    '@bear is the only instance.'

    def __init__(self, tag, **keywords):
        self.angry = True
        self.chained = True
        Actor.__init__(self, tag, **keywords)

    def act(self, command_map, concept):
        'If not chained and the troll is present, scare him.'
        actions = []
        if ((not self.chained) and '@troll' in concept.item and
            concept.room_of(str(self)) == concept.room_of('@troll')):

            actions.append(Modify('scare', str(self),
                                  template='[agent/s] [scare/v] [@troll/s]',
                                  direct='@troll', feature='scared',
                                  new=True))
        return actions

    def prevent(self, world, basis):
        # No one can manipulate the chain if the bear is angry.
        if ((basis.configure or basis.modify) and
            basis.direct == '@chain' and self.angry):
            return True
        return False

    def react(self, world, basis):
        'Food- and chain-related reactions.'
        actions = []
        # Eat food if it is offered, calm down.
        if (basis.configure and basis.new_parent == str(self) and
            'food' in world.item[basis.direct].qualities):
            actions.append(Behave('eat', str(self), direct=basis.direct))
            actions.append(Modify('calm', '@cosmos',
                                  template='[direct/s] [calm/v] down',
                                  direct=str(self), feature='angry',
                                  new=False))
        # If chained, follow the holder of the chain.
        if (self.chained and basis.configure and
            basis.direct == world.item['@chain'].parent):
            actions.append(Configure('follow', str(self),
                                     template=('[agent/s] [follow/v] [' +
                                               basis.direct + '/o]'),
                                     direct=str(self),
                                     new=(basis.new_link, basis.new_parent)))
        # If entering the bridge, destroy it; kill whoever is holding the chain.
        if (basis.configure and basis.direct == str(self) and
            basis.new_parent == '@bridge'):
            actions.append(Modify('collapse', '@cosmos',
                                  template='the bridge [collapse/1/v]',
                                  direct='@bridge', feature='connects',
                                  new=()))
            actions.append(Modify('die', '@cosmos',
                                  template='[direct/s] [die/1/v]',
                                  direct='@bear', feature='alive',
                                  new=False))
            if self.chained:
                holder == world.item['@chain'].parent
                actions.append(Modify('die', '@cosmos',
                                      template='[direct/s] [die/1/v]',
                                      direct=holder, feature='alive',
                                      new=False))
        return actions


class Oyster(Thing):
    '@oyster is the only instance.'

    def prevent(self, _, basis):
        if (basis.modify and basis.direct == str(self) and
            basis.feature == 'open' and basis.new_value and
            (not hasattr(basis, 'indirect') or
             not basis.indirect == '@trident')):
            return True
        return False

    def react(self, _, basis):
        'When opened, move the pearl to the cul-de-sac.'
        actions = []
        if (basis.modify and basis.direct == str(self) and
            basis.feature == 'open' and basis.new_value and
            ('in', '@pearl') in self.children):
            sight = """
            an enormous oyster, currently [open/@oyster/a]"""
            actions.append(Configure('fall', '@cosmos',
                                template=('[direct/o] [fall/v] from ' +
                                          '[@oyster/o]'),
                                direct='@pearl',
                                new=('in', '@cul_de_sac')))
            actions.append(Modify('change_sight', basis.agent,
                                  direct=str(self), feature='sight',
                                  new=sight, salience=0))
            actions.append(Modify('rename', basis.agent,
                                  direct=str(self), feature='called',
                                  template="""so, at it happens, [this]
                                           actually [is/v/v] an oyster,
                                           not a clam""",
                                  new='(enormous) oyster'))
        return actions


class Plant(Thing):
    '@plant is the only instance.'

    def __init__(self, tag, **keywords):
        self.size = 0
        self.alive = True
        Thing.__init__(self, tag, **keywords)

    def react(self, world, basis):
        'Consume water; then grow when watered, the first two times.'
        actions = []
        if (basis.configure and basis.new_parent == str(self) and
            basis.direct.partition('_')[0] == '@oil'):
            # Consume oil
            actions.append(Configure('consume', '@cosmos',
                           template=('[direct/s] [soak/v] into [' +
                                     str(self) + '/o]'),
                           direct=basis.direct, new=('of', '@cosmos'),
                           salience=0.1))
            # And die!
            actions.append(Modify('die', '@cosmos',
                              template='[@plant/s] [die/v]',
                              direct=str(self), feature='alive',
                              new=False))
        if (basis.configure and basis.new_parent == str(self) and
            basis.direct.partition('_')[0] == '@water'):
            # Consume water
            actions.append(Configure('consume', '@cosmos',
                                     template=('[@plant/s] [soak/v] up ' +
                                               '[direct/o]'),
                                     direct=basis.direct,
                                     new=('of', '@cosmos'), salience=0.1))
            # If not already the maximum size, grow.
            if self.size == 0 or self.size == 1:
                actions.append(Modify('grow', '@cosmos',
                                  template='[@plant/s] [grow/v]',
                                  direct=str(self), feature='size',
                                  new=(self.size + 1)))
                sight = ["""a twelve-foot beanstalk""",
                """a 25-foot beanstalk"""][self.size]
                actions.append(Modify('change_sight', '@cosmos',
                                      direct=str(self), feature='sight',
                                      new=sight, salience=0.0))
                if self.size == 1:
                    exits = world.item['@west_pit'].exits.copy()
                    exits.update({'climb': '@narrow_corridor'})
                    actions.append(Modify('change_exits', '@cosmos',
                                          direct='@west_pit',
                                          feature='exits', new=exits,
                                          salience=0.0))
        return actions


class RustyDoor(Door):
    '@rusty_door is the only instance.'

    def react(self, world, basis):
        'Consume oil; then unlock if not already unlocked.'
        actions = []
        if (basis.configure and basis.new_parent == str(self) and
            basis.direct.partition('_')[0] == '@oil'):
            # Consume the oil
            actions.append(Configure('consume', '@cosmos',
                           template=('[direct/s] [soak/v] into [' +
                                     str(self) + '/o]'),
                           direct=basis.direct, new=('of', '@cosmos'),
                           salience=0.1))
            # If not already unlocked, unlock.
            if self.locked:
                actions.append(Modify('unlock', '@cosmos',
                               template=('[' + str(self) + '/s] ' +
                                         '[come/v] loose'),
                               direct=str(self), feature='locked', new=False,
                               salience=0.9))
        return actions


class Bird(Thing):
    '@bird is the only instance.'

    def __init__(self, tag, **keywords):
        self.alive = True
        Thing.__init__(self, tag, **keywords)

    def prevent(self, world, basis):
        if (basis.configure and basis.direct == str(self) and
            basis.new_parent == '@cage' and
            basis.agent == world.item['@rusty_rod'].parent):
            return True
        return False

    def react(self, world, basis):
        'Flee from one holding the rod; Leave all but the cage or a room.'
        actions = []
        if (basis.configure and basis.direct == str(self) and
            not basis.new_parent == '@cage' and
            not world.item[basis.new_parent].room):
            room = str(world.item[str(self)].place(world))
            actions.append(Configure('flit', str(self),
                                     template='[agent/s] [flit/v] off',
                                     direct=str(self), new=('in', room),
                                     salience=0.7))
        return actions


class Delicate(Thing):
    '@vase is the only instance.'

    def react(self, _, basis):
        'Shatter if placed on anything other than the pillow.'
        actions = []
        if (basis.configure and basis.direct == str(self)):
            if (not basis.new_parent in ['@pillow', '@soft_room',
                                         '@adventurer', '@cosmos']):
                smash = Configure('smash', basis.agent, direct=basis.direct,
                                  new=('of', '@cosmos'), salience=0.9)
                actions.append(smash)
        return actions


class Wanderer(Actor):
    'Not used, but could be used for the dwarves and the pirate.'

    def act(self, command_map, world):
        if random() > .2 and len(self.exits(world)) > 0:
            way = choice(self.exits(world).keys())
            return [self.do_command('exit ' + way, command_map, world)]


class OutsideArea(Room):
    'Subclass for all forest/outside Rooms, with sky and sun.'

    def __init__(self, tag, **keywords):
        if 'shared' not in keywords:
            keywords['shared'] = []
        keywords['shared'] += ['@sky', '@sun']
        Room.__init__(self, tag, **keywords)


class CaveRoom(Room):
    'Subclass for all cave Rooms.'

    def __init__(self, tag, **keywords):
        adj, noun = '', ''
        if 'referring' in keywords:
            (adj, _, noun) = keywords['referring'].partition('|')
        keywords['referring'] = adj + '| cave chamber room' + noun
        if 'glow' not in keywords:
            keywords['glow'] = 0.0
        Room.__init__(self, tag, **keywords)


class Bridgable(CaveRoom):
    '@fissure_east is the only instance.'

    def react(self, world, basis):
        'When the rod is waved, the bridge appears.'
        actions = []
        if (basis.behave and basis.direct == '@rusty_rod' and
            basis.verb == 'shake' and 'west' not in self.exits):
            exits = self.exits.copy()
            exits.update({'west': '@bridge',
                          'over': '@bridge'})
            sight = """
            [*/s] [are/v] on the east bank of a fissure slicing clear across
            the hall

            the mist [is/1/v] quite thick [here], and the fissure [is/1/v]
            too wide to jump

            it [is/1/v] a good thing the fissure [is/1/v] bridged [now], and
            [*/s] [are/v] able to walk across it to the west
            """
            actions.append(Modify('change_exits', '@cosmos',
                                  template='a_bridge [now] [lead/v] west',
                                  direct=str(self), feature='exits',
                                  new=exits, salience=0.9))
            actions.append(Modify('change_sight', '@cosmos',
                                  direct=str(self), feature='sight',
                                  new=sight, salience=0.0))
        return actions


class EggSummoning(CaveRoom):
    '@giant_room_92 is the only instance.'

    def react(self, world, basis):
        'Have "fee fie foe sum" summon the eggs here.'
        actions = []
        if (basis.behave and hasattr(basis, 'utterance') and
            basis.utterance in ['fee fie foe foo', '"fee fie foe foo"'] and
            ('@eggs', 'in') not in self.children):
            actions.append(Configure('appear', '@cosmos',
                           template='[direct/s] [appear/v]',
                           direct='@eggs', new=('in', str(self)),
                           salience=0.9))
        return actions


class Building(Room):
    '@building_3 is the only instance.'

    def react(self, world, basis):
        'When all treasures are in place, countdown to cave closing.'
        actions = []
        if world.item['@cosmos'].closing == 0:
            all_there = True
            for treasure in all_treasures:
                all_there &= (str(self) == str(world.room_of(treasure)))
            if all_there:
                actions.append(Modify('change_closing', '@cosmos',
                                      direct='@cosmos', feature='closing',
                                      new=(world.ticks + 28), salience=0))
        return actions

def contain_any_thing_if_open(tag, link, world):
    return link == 'in' and getattr(world.item['@cage'], 'open')

def support_one_item(tag, link, world):
    return link == 'on' and len(world.item['@pillow'].children) < 2

def contain_any_treasure(tag, link, world):
    return link == 'in' and 'treasure' in world.item[tag].qualities

def possess_any_treasure(tag, link, world):
    return link == 'of' and 'treasure' in world.item[tag].qualities

def support_any_item_or_dragon(tag, link, world):
    return link == 'on' and '@dragon' not in world.item['@rug'].children

def support_chain(tag, link, world):
    return (tag, link) == ('@chain', 'on')

can.contain_any_thing_if_open = contain_any_thing_if_open
can.support_one_item = support_one_item
can.contain_any_treasure = contain_any_treasure
can.possess_any_treasure = possess_any_treasure
can.support_any_item_or_dragon = support_any_item_or_dragon
can.support_chain = support_chain

items = [

    Substance('@water',
        called='water',
        referring='clear |',
        qualities=['drink', 'liquid'],
        consumable=True,
        sight='clear water',
        taste="nothing unpleasant"),

    Substance('@oil',
        called='oil',
        referring='black dark thick |',
        qualities=['liquid'],
        sight='black oil'),

    Actor('@adventurer in @end_of_road',
        article='the',
        called='(intrepid) adventurer',
        allowed=can.possess_any_thing,
        qualities=['person', 'man'],
        gender='?',
        sight='a nondescript adventurer'),

    OutsideArea('@end_of_road',
        article='the',
        called='end of the road',
        referring='of the | road end',
        exits={'hill': '@hill', 'west': '@hill', 'up': '@hill',
               'enter': '@building', 'house': '@building',
               'in': '@building', 'east': '@building',
               'downstream': '@valley', 'gully': '@valley',
               'stream': '@valley', 'south': '@valley',
               'down': '@valley', 'forest': '@forest_near_road',
               'north': '@forest_near_road', 'depression': '@outside_grate'},
        sight="""

        [*/s] [stand/ing/v] at _the_end of _a_road before
        _a_small_brick_building

        [@stream_by_road/s] [flow/v] out of _the_building and down _a_gully"""),

    Thing('@stream_by_road part_of @end_of_road',
        article='a',
        called='small stream',
        referring='| stream creek river spring',
        source='@water',
        mention=False,
        sight='a small stream',
        touch='cool water',
        hearing='quiet babbling'),

    SharedThing('@sky',
        article='the',
        called='sky',
        referring='blue clear | heavens',
        mention=False,
        accessible=False,
        sight='a blue, clear sky'),

    SharedThing('@sun',
        article='the',
        called='sun',
        mention=False,
        accessible=False),

    OutsideArea('@hill',
        article='the',
        called='hill in road',
        exits={'hill': '@end_of_road', 'house': '@end_of_road',
               'onward': '@end_of_road', 'east': '@end_of_road',
               'north': '@end_of_road', 'down': '@end_of_road',
               'forest': '@forest_near_road', 'south': '@forest_near_road'},
        sight="""

        [*/s] [walk/ed/v] up _a_hill, still in _the_forest

        _the_road [slope/1/v] back down _the_other_side of _the_hill

        there [is/1/v] _a_building in the_distance"""),

    Building('@building',
        article='the',
        called="building's interior",
        referring='well | building house',
        exits={'enter': '@end_of_road', 'leave': '@end_of_road',
               'outdoors': '@end_of_road', 'west': '@end_of_road',
               'xyzzy': '@debris_room', 'plugh': '@y2',
               'down': """the_stream [flow/1/v] out through a pair of 
               1 foot diameter sewer pipes, too small to enter""",
               'stream': """the_stream [flow/1/v] out through a pair of 
               1 foot diameter sewer pipes, too small to enter"""},
        sight="""

        [*/s] [are/v] inside _a_building, _a_well_house for _a_large_spring"""),

    Thing('@keys in @building',
        article='some',
        called='(glinting) keys',
        referring='key of ring | key keyring ring',
        qualities=['device', 'metal'],
        number='plural',
        sight='ordinary keys, on a ring'),

    Thing('@food in @building',
        article='some',
        called='food',
        referring='tasty fresh edible | wrap',
        qualities=['food'],
        consumable=True,
        sight='a wrap, fresh and edible',
        smell="""

        something pleasing

        _bacon was somehow involved in the production of [this] wrap""",
        taste="food that [seem/1/v] fresh and palatable"),

    Thing('@bottle in @building',
        article='a',
        called='(clear) (glass) bottle',
        open=False,
        transparent=True,
        vessel='@water',
        sight='a clear glass bottle, currently [open/@bottle/a]',
        touch="smooth glass"),

    Lamp('@lamp in @building',
        article='a',
        called='(shiny) (brass) (carbide) lamp',
        referring='| lantern light',
        qualities=['device', 'metal'],
        on=False,
        sight="""

        a brass carbide lamp, the kind often used for illuminating caves

        [@lamp/s/pro] [is/v] shiny and [glow/@lamp/a]

        [@lamp/s/pro] [display/v] the word [word/@dial/a] and [have/v] three
        switches: a "HESITANT" switch, a "SURPRISE" switch, and a "VALLEY GIRL"
        switch

        [@lamp/s] also [feature/v] a dial which can range from 1 to 12 and
        [is/v] set to [setting/@dial/a]""",
        touch="""

        [@lamp/s] and [@dial/s] on it, which [*/s] [sense/v] [is/1/v] set to
        [setting/@dial/a]"""),

    Dial('@dial part_of @lamp',
        article='the',
        called='dial',
        referring='round | dial knob',
        setting=2,
        word='memoir',
        mention=False,
        sight="""

        [@dial/s] can be set to any number between 1 and 12

        [@dial/pro/s] [is/v] set to [setting/@dial/a]"""),

    Thing('@hesitant part_of @lamp',
        article='the',
        called='"HESITANT" switch',
        referring='hesitant | switch',
        mention=False,
        on=False),

    Thing('@surprise part_of @lamp',
        article='the',
        called='"SURPRISE" switch',
        referring='surprise | switch',
        mention=False,
        on=False),

    Thing('@valley_girl part_of @lamp',
        article='the',
        called='"VALLEY GIRL" switch',
        referring='valley girl | switch',
        mention=False,
        on=False),

    OutsideArea('@valley',
        article='the',
        called='valley',
        exits={'upstream': '@end_of_road', 'house': '@end_of_road',
               'north': '@end_of_road', 'forest': '@forest_near_road',
               'east': '@forest_near_road', 'west': '@forest_near_road',
               'up': '@forest_near_road', 'downstream': '@slit',
               'south': '@slit', 'down': '@slit',
               'depression': '@outside_grate'},
        sight="""

        [*/s] [are/v] in _a_valley in _the_forest beside _a_stream tumbling
        along _a_rocky_bed"""),

    Thing('@stream_in_valley part_of @valley',
        article='a',
        called='tumbling stream',
        referring='| stream creek river spring',
        qualities=['liquid'],
        source='@water',
        mention=False,
        sight='a tumbling stream'),

    OutsideArea('@forest_near_road',
        article='the',
        called='forest',
        exits={'valley': '@valley', 'east': '@valley', 'down': '@valley',
               'forest': '@forest_near_valley', 'west': '@forest_near_road',
               'south': '@forest_near_road'},
        sight="""

        [*/s] [are/v] in open forest, with _a_deep_valley to _one_side"""),

    OutsideArea('@forest_near_valley',
        article='the',
        called='forest',
        sight="""

        [*/s] [are/v] in open forest near both _a_valley and _a_road""",
        exits={'hill': '@end_of_road', 'north': '@end_of_road',
               'valley': '@valley', 'east': '@valley', 'west': '@valley',
               'down': '@valley', 'forest': '@forest_near_road',
               'south': '@forest_near_road'}),

    OutsideArea('@slit',
        article='the',
        called='slit in the streambed',
        exits={'house': '@end_of_road', 'upstream': '@valley',
               'north': '@valley', 'forest': '@forest_near_road',
               'east': '@forest_near_road', 'west': '@forest_near_road',
               'downstream': '@outside_grate', 'rock': '@outside_grate',
               'bed': '@outside_grate', 'south': '@outside_grate',
               'slit': '[*/s] [fit/not/v] through a two-inch slit',
               'stream': '[*/s] [fit/not/v] through a two-inch slit',
               'down': '[*/s] [fit/not/v] through a two-inch slit'},
        sight="""

        at [*'s] feet all _the_water of _the_stream [splash/1/v] into
        _a_2-inch_slit in _the_rock

        downstream _the_streambed [is/1/v] bare rock"""),

    Thing('@spring_7 in @slit',
        article='a',
        called='small stream',
        referring='| stream creek river spring',
        qualities=['liquid'],
        source='@water',
        mention=False,
        sight='a small stream'),

    OutsideArea('@outside_grate',
        article='the',
        called='area outside the grate',
        sight="""

        [*/s] [are/v] in a _20-foot_depression floored with bare dirt

        set into the_dirt [is/1/v] [@grate/o] mounted in _concrete

        _a_dry_streambed [lead/1/v] into _the_depression""",
        exits={'forest': '@forest_near_road', 'east': '@forest_near_road',
               'west': '@forest_near_road', 'south': '@forest_near_road',
               'house': '@end_of_road', 'upstream': '@slit', 'gully': '@slit',
               'north': '@slit', 'enter': '@grate', 'down': '@grate'}),

    Door('@grate',
        article='a',
        called='(strong) (steel) grate',
        referring='| grating grill grille barrier',
        qualities=['doorway', 'metal'],
        allowed=can.permit_any_item,
        open=False,
        locked=True,
        key='@keys',
        transparent=True,
        connects=['@outside_grate', '@below_grate'],
        mention=False,
        sight="""

        a grate, placed to restrict entry to the cave

        it [is/1/v] currently [open/@grate/a]"""),

    CaveRoom('@below_grate',
        article='the',
        called='area below the grate',
        referring='below the grate |',
        sight="""

        [*/s] [are/v] in _a_small_chamber beneath _a_3x3_steel_grate to the
        surface

        _a_low crawl over _cobbles [lead/1/v] inward to the west""",
        glow=0.7,
        exits={'leave': '@grate', 'exit': '@grate',
               'up': '@grate', 'crawl': '@cobble_crawl',
               'cobble': '@cobble_crawl', 'in': '@cobble_crawl',
               'west': '@cobble_crawl', 'pit': '@small_pit',
               'debris': '@debris_room'}),

    CaveRoom('@cobble_crawl',
        article='the',
        called='cobble crawl',
        referring='passage',
        sight="""

        [*/s] [crawl/ing/v] over _cobbles in _a_low_passage

        there [is/1/v] a dim _light at _the_east_end of _the_passage""",
        glow=0.5,
        exits={'leave': '@below_grate', 'surface': '@below_grate',
               'nowhere': '@below_grate', 'east': '@below_grate',
               'in': '@debris_room', 'dark': '@debris_room',
               'west': '@debris_room', 'debris': '@debris_room',
               'pit': '@small_pit'}),

    Thing('@cage in @cobble_crawl',
        article='a',
        called='wicker cage',
        referring='wicker | cage',
        allowed=can.contain_any_thing_if_open,
        open=True,
        transparent=True,
        sight="""

        a wicker cage, about the size of a breadbasket, currently
        [open/@cage/a]"""),

    CaveRoom('@debris_room',
        article='the',
        called='debris room',
        sight="""
        [*/s] [are/v] in _a_room filled with _debris washed in from
        _the_surface

        _a_low_wide_passage with _cobbles [become/1/v] plugged with _mud and
        _debris [here], but _an_awkward_canyon [lead/1/v] upward and west

        _a_note on the wall [say/1/v] "MAGIC WORD XYZZY\"""",
        exits={'entrance': '@below_grate', 'crawl': '@cobble_crawl',
               'cobble': '@cobble_crawl', 'tunnel': '@cobble_crawl',
               'low': '@cobble_crawl', 'east': '@cobble_crawl',
               'canyon': '@awkward_canyon', 'in': '@awkward_canyon',
               'up': '@awkward_canyon', 'west': '@awkward_canyon',
               'xyzzy': '@building', 'pit': '@small_pit'}),

    Thing('@rusty_rod in @debris_room',
        article='a',
        called='black rod',
        referring='black iron rusty sinister | rod',
        sight='[this] ordinary sinister black rod, rather rusty'),

    CaveRoom('@awkward_canyon',
        article='the',
        called='awkward canyon',
        sight="""

        [*/s] [are/v] in _an_awkward_sloping_east/west_canyon""",
        exits={'entrance': '@below_grate', 'down': '@debris_room',
               'east': '@debris_room', 'debris': '@debris_room',
               'in': '@bird_chamber', 'up': '@bird_chamber',
               'west': '@bird_chamber', 'pit': '@small_pit'}),

    CaveRoom('@bird_chamber',
        article='the',
        called='bird chamber',
        sight="""

        [*/s] [are/v] in _a_splendid_chamber thirty feet high

        _the_walls [are/2/v] frozen _rivers of orange _stone

        _an_awkward_canyon and _a_good_passage [exit/2/v] from the east and
        west _sides of _the_chamber""",
        exits={'entrance': '@below_grate', 'debris': '@debris_room',
               'canyon': '@awkward_canyon', 'east': '@awkward_canyon',
               'tunnel': '@small_pit', 'pit': '@small_pit',
               'west': '@small_pit'}),

    Bird('@bird in @bird_chamber',
        article='a',
        called='little bird',
        referring='little cheerful | bird',
        sight='nothing more than a bird'),

    CaveRoom('@small_pit',
        article='the',
        called='top of the small pit',
        exits={'entrance': '@below_grate', 'debris': '@debris_room',
               'tunnel': '@bird_chamber', 'east': '@bird_chamber',
               'down': '@hall_of_mists',
               'west': 'the crack [is/1/v] far too small to follow',
               'crack': 'the crack [is/1/v] far too small to follow'},
        sight="""
        at [*'s] feet [is/1/v] _a_small_pit breathing traces of white _mist

        _an_east_passage [end/1/v] [here] except for _a_small_crack leading
        on"""),

    CaveRoom('@hall_of_mists',
        article='the',
        called='hall of mists',
        sight="""
        [*/s] [are/v] at one _end of _a_vast_hall stretching forward out of
        sight to the west

        there [are/2/v] _openings to either _side

        nearby, _a_wide_stone_staircase [lead/1/v] downward

        _the_hall [is/1/v] filled with _wisps of white _mist swaying to and fro
        almost as if alive

        _a_cold_wind [blow/1/v] up _the_staircase

        there [is/1/v] _a_passage at _the_top of _a_dome behind [*/o]""",
        exits={'left': '@nugget_room', 'south': '@nugget_room',
               'onward': '@fissure_east', 'hall': '@fissure_east',
               'west': '@fissure_east', 'stair': '@hall_of_mountain_king',
               'down': '@hall_of_mountain_king',
               'north': '@hall_of_mountain_king', 'up': '@small_pit',
               'y2': '@y2'}),

    Bridgable('@fissure_east',
        article='the',
        called='east bank of the fissure',
        referring='east of fissure | bank',
        sight="""

        [*/s] [are/v] on _the_east_bank of _a_fissure that [slice/1/v] clear
        across _the_hall

        _the_mist [is/1/v] quite thick here, and _the_fissure [is/1/v] too
        wide to jump""",
        shared=['@fissure'],
        exits={'hall': '@hall_of_mists', 'east': '@hall_of_mists'}),

    SharedThing('@fissure',
        article='a',
        called='fissure',
        referring='massive |',
        sight='a massive fissure'),

    Door('@bridge',
        article='a',
        called='bridge',
        referring='| bridge span',
        allowed=can.permit_any_item,
        connects=['@fissure_east', '@fissure_west'],
        sight='[@bridge] [span/v] the chasm'),

    CaveRoom('@nugget_room',
        article='the',
        called='nugget of gold room',
        referring='nugget of gold low |',
        exits={'hall': '@hall_of_mists', 'leave': '@hall_of_mists',
               'north': '@hall_of_mists'},
        sight="""

        [this] [is/1/v] _a_low_room with _a_crude_note on _the_wall

        _the_note [say/1/v] , "You won't get it up the steps" """),

    Thing('@nugget in @nugget_room',
        article='a',
        called='nugget of gold',
        referring='large sparkling of | nugget gold',
        qualities=['treasure', 'metal'],
        sight='a large gold nugget'),

    CaveRoom('@hall_of_mountain_king',
        article='the',
        called='Hall of the Mountain King',
        referring='of the mountain king | hall',
        sight="""

        [*/s] [are/v] in _the_Hall_of_the_Mountain_King, with _passages off in
        all _directions""",
        exits={'stair': '@hall_of_mists', 'up': '@hall_of_mists',
               'east': '@hall_of_mists', 'west': '@west_side_chamber',
               'north': '@low_passage', 'south': '@south_side_chamber',
               'secret': '@secret_east_west_canyon',
               'southwest': '@secret_east_west_canyon'}),

    Snake('@snake in @hall_of_mountain_king',
        article='a',
        called='huge snake',
        referring='huge green fierce | snake',
        sight='[this] [is/1/v] just a huge snake, barring the way',
        smell="something like Polo cologne",
        blocked=['west', 'north', 'south', 'secret', 'southwest']),

    CaveRoom('@west_end_of_twopit_room',
        article='the',
        called='west end of twopit room',
        sight="""

        [*/s] [are/v] at _the_west_end of _the_Twopit_Room

        there [is/1/v] _a_large_hole in _the_wall above _the_pit at [this]
        _end of _the_room""",
        exits={'east': '@east_end_of_twopit_room',
               'across': '@east_end_of_twopit_room', 'west': '@slab_room',
               'slab': '@slab_room', 'down': '@west_pit',
               'pit': '@west_pit', 'hole': '@complex_junction'}),

    CaveRoom('@east_pit',
        article='the',
        called='east pit',
        referring='eastern east | pit',
        sight="""

        [*/s] [are/v] at _the_bottom of _the_eastern_pit in _the_Twopit_Room

        there [is/1/v] [@pool_of_oil/o] in _one_corner of _the_pit""",
        exits={'up': '@east_end_of_twopit_room',
               'leave': '@east_end_of_twopit_room'}),

    Thing('@pool_of_oil in @east_pit',
        article='a',
        called='small pool of oil',
        referring='small of oil | pool',
        qualities=['liquid'],
        source='@oil',
        sight='a small pool of oil'),

    CaveRoom('@west_pit',
        article='the',
        called='west pit',
        referring='western west | pit',
        sight="""

        [*/s] [are/v] at _the_bottom of _the_western_pit in _the_Twopit_Room

        there [is/1/v] _a_large_hole in _the_wall about 25 feet above [*/o]""",
        exits={'up': '@west_end_of_twopit_room',
               'leave': '@west_end_of_twopit_room'}),

    Plant('@plant in @west_pit',
        article='a',
        called='plant',
        referring='tiny little big tall gigantic | plant beanstalk',
        open=False,
        sight='a tiny little plant, murmuring "Water, water, ..."'),

    CaveRoom('@fissure_west',
        article='the',
        called='west side of fissure',
        referring='west of fissure | side',
        sight="""

        [*/s] [are/v] on _the_west_side of _the_fissure in
        _the_Hall_of_Mists""",
        shared=['@fissure'],
        exits={'over': '@fissure_east', 'east': '@fissure_east',
               'west': '@west_end_of_hall_of_mists'}),

    Thing('@diamonds in @fissure_west',
        article='some',
        called='diamonds',
        referring='| jewel jewels',
        qualities=['treasure'],
        sight='diamonds'),

    CaveRoom('@low_passage',
        article='the',
        called='low passage',
        sight="""

        [*/s] [are/v] in _a_low_north/south_passage at _a_hole in _the_floor

        the hole [go/1/v] down to an east/west passage""",
        exits={'hall': '@hall_of_mountain_king',
               'leave': '@hall_of_mountain_king',
               'south': '@hall_of_mountain_king', 'north': '@y2',
               'y2': '@y2', 'down': '@dirty_passage',
               'hole': '@dirty_passage'}),

    Thing('@bars in @low_passage',
        article='the',
        called='bars of silver',
        referring='several of | bars silver',
        qualities=['treasure', 'metal'],
        number='plural',
        sight='several bars of silver'),

    CaveRoom('@south_side_chamber',
        article='the',
        called='south side chamber',
        sight="""

        [*/s] [are/v] in the south side chamber""",
        exits={'hall': '@hall_of_mountain_king',
               'leave': '@hall_of_mountain_king',
               'north': '@hall_of_mountain_king'}),

    Thing('@jewelry in @south_side_chamber',
        article='some',
        called='(precious) jewelry',
        referring='| jewel jewels',
        qualities=['treasure'],
        sight='precious jewelry'),

    CaveRoom('@west_side_chamber',
        article='the',
        called='west side chamber',
        sight="""

        [*/s] [are/v] in _the_west_side_chamber of
        _the_Hall_of_the_Mountain_King

        _a_passage continues west and up [here]""",
        exits={'hall': '@hall_of_mountain_king',
               'leave': '@hall_of_mountain_king',
               'east': '@hall_of_mountain_king', 'west': '@crossover',
               'up': '@crossover'}),

    Thing('@coins in @west_side_chamber',
        article='many',
        called='coins',
        referring='shiny numerous | money',
        qualities=['treasure', 'metal'],
        number='plural',
        sight='numerous coins'),

    CaveRoom('@y2',
        called='Y2',
        sight="""

        [*/s] [are/v] in _a_large_room, with _a_passage to the south,
        _a_passage to the west, and _a_wall of broken _rock to the east

        there [is/1/v] a large "Y2" on a rock in the room's center""",
        exits={'plugh': '@building', 'south': '@low_passage',
               'east': '@jumble', 'wall': '@jumble',
               'broken': '@jumble', 'west': '@window_on_pit',
               'plover': '@plover_room'}),

    CaveRoom('@jumble',
        article='the',
        called='jumble',
        sight="""

        [*/s] [are/v] in _a_jumble of _rock, with _cracks everywhere""",
        exits={'down': '@y2', 'y2': '@y2', 'up': '@hall_of_mists'}),

    CaveRoom('@window_on_pit',
        article='the',
        called='window on pit',
        sight="""

        [*/s] [are/v] at _a_low_window overlooking _a_huge_pit, which extends
        up out of sight

        _a_floor [is/1/v] indistinctly visible over 50 feet below

        _traces of white _mist [cover/2/v] _the_floor of _the_pit, becoming
        thicker to the right

        _marks in _the_dust around _the_window [seem/2/v] to indicate that
        _someone [have/1/v] been [here] recently

        directly across _the_pit from [*/o] and 25 feet away there [is/1/v]
        _a_similar_window looking into _a_lighted_room

        _a_shadowy_figure [is/1/v] there peering back at [*/o]""",
        exits={'east': '@y2', 'y2': '@y2'}),

    CaveRoom('@dirty_passage',
        article='the',
        called='dirty passage',
        sight="""

        [*/s] [are/v] in _a_dirty_broken_passage

        to the east [is/1/v] _a_crawl

        to the west [is/1/v] _a_large_passage

        above [*/o] [is/1/v] _a_hole to _another_passage""",
        exits={'east': '@brink_of_pit', 'crawl': '@brink_of_pit',
               'up': '@low_passage', 'hole': '@low_passage',
               'west': '@dusty_rock_room', 'bedquilt': '@bedquilt'}),

    CaveRoom('@brink_of_pit',
        article='the',
        called='brink of pit',
        sight="""

        [*/s] [are/v] on _the_brink of _a_small_clean_climbable_pit

        _a_crawl [lead/1/v] west""",
        exits={'west': '@dirty_passage', 'crawl': '@dirty_passage',
               'down': '@bottom_of_pit', 'pit': '@bottom_of_pit',
               'climb': '@bottom_of_pit'}),

    CaveRoom('@bottom_of_pit',
        article='the',
        called='bottom of pit',
        sight="""

        [*/s] [are/v] in the bottom of _a_small_pit with [@stream_in_pit/o],
        which [enter/1/v] and [exit/1/v] through _tiny_slits""",
        exits={'climb': '@brink_of_pit', 'up': '@brink_of_pit',
               'leave': '@brink_of_pit'}),

    Thing('@stream_in_pit part_of @bottom_of_pit',
        article='a',
        called='little stream',
        referring='small | stream creek river spring',
        qualities=['liquid'],
        source='@water',
        mention=False,
        sight='a little stream'),

    CaveRoom('@dusty_rock_room',
        article='the',
        called='dusty rock room',
        sight="""

        [*/s] [are/v] in _a_large_room full of _dusty_rocks

        there [is/1/v] _a_big_hole in _the_floor

        there [are/2/v] _cracks everywhere, and _a_passage leading east""",
        exits={'east': '@dirty_passage', 'tunnel': '@dirty_passage',
               'down': '@complex_junction', 'hole': '@complex_junction',
               'floor': '@complex_junction', 'bedquilt': '@bedquilt'}),

    CaveRoom('@west_end_of_hall_of_mists',
        article='the',
        called='west end of hall of mists',
        sight="""
        [*/s] [are/v] at _the_west_end of _the_Hall_of_Mists

        _a_low_wide_crawl [continue/1/v] west and _another [go/1/v] north

        to the south [is/1/v] _a_little_passage 6 feet off _the_floor""",
        exits={'south': '@maze_1', 'up': '@maze_1', 'tunnel': '@maze_1',
               'climb': '@maze_1', 'east': '@fissure_west',
               'west': '@east_end_of_long_hall',
               'crawl': '@east_end_of_long_hall'}),

    CaveRoom('@maze_1',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'up': '@west_end_of_hall_of_mists', 'north': '@maze_1',
               'east': '@maze_2', 'south': '@maze_4', 'west': '@maze_11'}),

    CaveRoom('@maze_2',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'west': '@maze_1', 'south': '@maze_3', 'east': '@room'}),

    CaveRoom('@maze_3',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'east': '@maze_2', 'down': '@dead_end_3', 'south': '@maze_6',
               'north': '@dead_end_11'}),

    CaveRoom('@maze_4',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'west': '@maze_1', 'north': '@maze_2', 'east': '@dead_end_1',
               'south': '@dead_end_2', 'up': '@maze_14', 'down': '@maze_14'}),

    CaveRoom('@dead_end_1',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'west': '@maze_4', 'leave': '@maze_4'}),

    CaveRoom('@dead_end_2',
        article='the',
        called='dead end',
        referring='dead | end',
        sight="""
        dead end""",
        exits={'east': '@maze_4', 'leave': '@maze_4'}),

    CaveRoom('@dead_end_3',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'up': '@maze_3', 'leave': '@maze_3'}),

    CaveRoom('@maze_5',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'east': '@maze_6', 'west': '@maze_7'}),

    CaveRoom('@maze_6',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'east': '@maze_3', 'west': '@maze_5', 'down': '@maze_7',
               'south': '@maze_8'}),

    CaveRoom('@maze_7',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'west': '@maze_5', 'up': '@maze_6', 'east': '@maze_8',
               'south': '@maze_9'}),

    CaveRoom('@maze_8',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'west': '@maze_6', 'east': '@maze_7', 'south': '@maze_8',
               'up': '@maze_9', 'north': '@maze_10', 'down': '@dead_end_13'}),

    CaveRoom('@maze_9',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'west': '@maze_7', 'north': '@maze_8',
               'south': '@dead_end_4'}),

    CaveRoom('@dead_end_4',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'west': '@maze_9', 'leave': '@maze_9'}),

    CaveRoom('@maze_10',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'west': '@maze_8', 'north': '@maze_10', 'down': '@dead_end_5',
               'east': '@brink_with_column'}),

    CaveRoom('@dead_end_5',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'up': '@maze_10', 'leave': '@maze_10'}),

    CaveRoom('@brink_with_column',
        article='the',
        called='brink of pit',
        sight="""

        [*/s] [are/v] on _the_brink of _a_thirty_foot_pit with
        _a_massive_orange_column down _one_wall

        [*/s] could climb down [here] but [*/s] could not get back up

        _the_maze [continue/1/v] at _this_level""",
        exits={'down': '@bird_chamber', 'climb': '@bird_chamber',
               'west': '@maze_10', 'south': '@dead_end_6', 'north': '@maze_12',
               'east': '@maze_13'}),

    CaveRoom('@dead_end_6',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'east': '@brink_with_column', 'leave': '@brink_with_column'}),

    CaveRoom('@east_end_of_long_hall',
        article='the',
        called='east end of long hall',
        sight="""

        [*/s] [are/v] at _the_east_end of _a_very_long_hall apparently without
        _side_chambers

        to the east _a_low_wide_crawl [slant/1/v] up

        to the north _a_round_two-foot_hole [slant/1/v] down""",
        exits={'east': '@west_end_of_hall_of_mists',
               'up': '@west_end_of_hall_of_mists',
               'crawl': '@west_end_of_hall_of_mists',
               'west': '@west_end_of_long_hall',
               'north': '@crossover', 'down': '@crossover',
               'hole': '@crossover'}),

    CaveRoom('@west_end_of_long_hall',
        article='the',
        called='west end of long hall',
        sight="""

        [*/s] [are/v] at _the_west_end of _a_very_long_featureless_hall

        _the_hall [join/1/v] up with _a_narrow_north/south_passage""",
        exits={'east': '@east_end_of_long_hall',
               'north': '@crossover'}),

    CaveRoom('@crossover',
        article='the',
        called='crossover',
        sight="""

        [*/s] [are/v] at _a_crossover of _a_high_north/south_passage and
        _a_low_east/west_one""",
        exits={'west': '@east_end_of_long_hall', 'north': '@dead_end_7',
               'east': '@west_side_chamber',
               'south': '@west_end_of_long_hall'}),

    CaveRoom('@dead_end_7',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'south': '@crossover', 'leave': '@crossover'}),

    CaveRoom('@complex_junction',
        article='the',
        called='complex junction',
        sight="""

        [*/s] [are/v] at a_complex_junction

        _a_low_hands_and_knees_passage from the north [join/1/v]
        _a_higher_crawl from the east to make _a_walking_passage going west

        there [is/1/v] also _a_large_room above

        _the_air [is/1/v] damp [here]""",
        exits={'up': '@dusty_rock_room', 'climb': '@dusty_rock_room',
               'room': '@dusty_rock_room', 'west': '@bedquilt',
               'bedquilt': '@bedquilt', 'north': '@shell_room',
               'shell': '@shell_room', 'east': '@anteroom'}),

    CaveRoom('@bedquilt',
        article='the',
        called='bedquilt',
        sight="""

        [*/s] [are/v] in Bedquilt, _a_long_east/west_passage with _holes
        everywhere""",
        exits={'east': '@complex_junction', 'west': '@swiss_cheese_room',
               'slab': '@slab_room', 'up': '@dusty_rock_room',
               'north': '@junction_of_three_secret_canyons',
               'down': '@anteroom'}),
        # NEXT STEPS Passages should lead off randomly, south should exist

    CaveRoom('@swiss_cheese_room',
        article='the',
        called='swiss cheese room',
        sight="""

        [*/s] [are/v] in _a_room whose _walls [resemble/1/v] _Swiss_cheese

        _obvious_passages [go/2/v] west, east, northeast, and northwest

        _part of _the_room [is/1/v] occupied by _a_large_bedrock_block""",
        exits={'northeast': '@bedquilt',
               'west': '@east_end_of_twopit_room',
               'canyon': '@tall_canyon', 'south': '@tall_canyon',
               'east': '@soft_room', 'oriental': '@oriental_room'}),

    CaveRoom('@east_end_of_twopit_room',
        article='the',
        called='east end of twopit room',
        exits={'east': '@swiss_cheese_room',
               'west': '@west_end_of_twopit_room',
               'across': '@west_end_of_twopit_room',
               'down': '@east_pit',
               'pit': '@east_pit'},
        sight="""

        [*/s] [are/v] at _the_east_end of _the_Twopit_Room

        _the_floor [here] [is/1/v] littered with _thin_rock_slabs, which
        [make/2/v] it easy to descend _the_pits

        there [is/1/v] _a_path [here] bypassing _the_pits to connect
        _passages from east and west

        there [are/2/v] _holes all over, but the only _big_one [is/1/v]
        on _the_wall directly over _the_west_pit where [*/s] [are/v] unable to
        get to it"""),

    CaveRoom('@slab_room',
        article='the',
        called='slab room',
        exits={'south': '@west_end_of_twopit_room',
               'up': '@secret_canyon_above_room',
               'climb': '@secret_canyon_above_room',
               'north': '@bedquilt'},
        sight="""

        [*/s] [are/v] in _a_large_low_circular_chamber whose _floor [is/v]
        _an_immense_slab fallen from _the_ceiling

        east and west there once were _large_passages, but _they [are/2/v]
        [now] filled with _boulders

        _low_small_passages [go/2/v] north and south, and _the_south_one
        quickly [bend/1/v] west around _the_boulders"""),

    CaveRoom('@secret_canyon_above_room',
        article='the',
        called='secret canyon above room',
        sight="""

        [*/s] [are/v] in _a_secret_north/south_canyon above _a_large_room""",
        exits={'down': '@slab_room', 'slab': '@slab_room',
               'south': '@secret_canyon', 'north': '@mirror_canyon',
               'reservoir': '@reservoir'}),

    CaveRoom('@secret_canyon_above_passage',
        article='the',
        called='secret canyon above passage',
        sight="""

        [*/s] [are/v] in _a_secret_north/south_canyon above
        _a_sizable_passage""",
        exits={'north': '@junction_of_three_secret_canyons',
               'down': '@bedquilt', 'tunnel': '@bedquilt',
               'south': '@top_of_stalactite'}),

    CaveRoom('@junction_of_three_secret_canyons',
        article='the',
        called='junction of three secret canyons',
        sight="""

        [*/s] [are/v] in _a_secret_canyon at _a_junction of _three_canyons,
        bearing north, south, and southeast

        _the_north_one is as tall as _the_other_two combined""",
        exits={'southeast': '@bedquilt',
               'south': '@secret_canyon_above_passage',
               'north': '@window_on_pit_redux'}),

    CaveRoom('@large_low_room',
        article='the',
        called='large low room',
        sight="""

        [*/s] [are/v] in _a_large_low_room

        _crawls lead north, southeast, and southwest""",
        exits={'bedquilt': '@bedquilt', 'southwest': '@sloping_corridor',
               'north': '@dead_end_8', 'southeast': '@oriental_room',
               'oriental': '@oriental_room'}),

    CaveRoom('@dead_end_8',
        article='the',
        called='dead end crawl',
        referring='dead | end crawl',
        exits={'south': '@large_low_room', 'crawl': '@large_low_room',
               'leave': '@large_low_room'}),

    CaveRoom('@secret_east_west_canyon',
        article='the',
        called='secret east/west canyon above tight canyon',
        sight="""

        [*/s] [are/v] in _a_secret_canyon which [here] [run/1/v] east/west

        it [cross/1/v] over _a_very_tight_canyon 15 feet below

        if [*/s] were to go down [*/s] may not be able to get back up""",
        exits={'east': '@hall_of_mountain_king',
               'west': '@secret_canyon', 'down': '@wide_place'}),

    CaveRoom('@wide_place',
        article='the',
        called='wide place',
        sight="""

        [*/s] [are/v] at _a_wide_place in _a_very_tight_north/south_canyon""",
        exits={'south': '@tight_spot', 'north': '@tall_canyon'}),

    CaveRoom('@tight_spot',
        article='the',
        called='tight spot',
        sight='_the_canyon [here] [become/1/v] too tight to go further south',
        exits={'north': '@wide_place'}),

    CaveRoom('@tall_canyon',
        article='the',
        called='tall canyon',
        sight="""

        [*/s] [are/v] in _a_tall_east/west_canyon

        _a_low_tight_crawl [go/1/v] three feet north and [seem/1/v] to open
        up""",
        exits={'east': '@wide_place', 'west': '@dead_end_9',
               'north': '@swiss_cheese_room',
               'crawl': '@swiss_cheese_room'}),

    CaveRoom('@dead_end_9',
        article='the',
        called='dead end',
        referring='dead | end',
        sight="""
        _the_canyon runs into _a_mass_of_boulders -- [*/s] [are/v] at
        _a_dead_end""",
        exits={'south': '@tall_canyon'}),

    CaveRoom('@maze_11',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all alike""",
        exits={'north': '@maze_1', 'west': '@maze_11', 'south': '@maze_11',
               'east': '@dead_end_10'}),

    CaveRoom('@dead_end_10',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'west': '@maze_11', 'leave': '@maze_11'}),

    CaveRoom('@dead_end_11',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'south': '@maze_3', 'leave': '@maze_3'}),

    CaveRoom('@maze_12',
        article='the',
        called='maze',
        sight='[*/s] [are/v] in _a_maze of _twisty_little_passages, all alike',
        exits={'south': '@brink_with_column', 'east': '@maze_13',
               'west': '@dead_end_12'}),

    CaveRoom('@maze_13',
        article='the',
        called='maze',
        sight='[*/s] [are/v] in _a_maze of _twisty_little_passages, all alike',
        exits={'north': '@brink_with_column', 'west': '@maze_12',
               'northwest': '@dead_end_14'}),

    CaveRoom('@dead_end_12',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'east': '@maze_12', 'leave': '@maze_12'}),

    CaveRoom('@dead_end_13',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'up': '@maze_8', 'leave': '@maze_8'}),

    CaveRoom('@maze_14',
        article='the',
        called='maze',
        sight='[*/s] [are/v] in _a_maze of _twisty_little_passages, all alike',
        exits={'up': '@maze_4', 'down': '@maze_4'}),

    CaveRoom('@narrow_corridor',
        article='the',
        called='narrow corridor',
        sight="""

        [*/s] [are/v] in _a_long,_narrow_corridor stretching out of sight to
        _the_west

        at _the_eastern_end [is/v] _a_hole through which [*/s] [can/v] see
        _a_profusion of _leaves""",
        exits={'down': '@west_pit', 'climb': '@west_pit',
               'east': '@west_pit',
               'west': '@giant_room', 'giant': '@giant_room'}),

    CaveRoom('@steep_incline',
        article='the',
        called='steep incline above large room',
        sight="""

        [*/s] [are/v] at _the_top of _a_steep_incline above _a_large_room

        [*/s] could climb down [here], but [*/s] would not be able to climb up

        there is _a_passage leading back to the north""",
        exits={'north': '@cavern_with_waterfall',
               'cavern': '@cavern_with_waterfall',
               'tunnel': '@cavern_with_waterfall',
               'down': '@large_low_room', 'climb': '@large_low_room'}),

    EggSummoning('@giant_room',
        article='the',
        called='giant room',
        sight="""

        [*/s] [are/v] in _the_Giant_Room

        _the_ceiling [here] [is/1/v] too high up for [*'s] lamp to show
        _it

        _cavernous_passages [lead/2/v] east, north, and south

        on _the_west_wall [is/1/v] scrawled _the_inscription,
        "FEE FIE FOE FOO" \[sic]""",
        exits={'south': '@narrow_corridor', 'east': '@blocked_passage',
               'north': '@end_of_immense_passage'}),

    Thing('@eggs in @giant_room',
        article='some',
        called='golden eggs',
        referring='several gold golden | egg eggs',
        qualities=['treasure', 'metal'],
        number='plural',
        sight='several golden eggs'),

    CaveRoom('@blocked_passage',
        article='the',
        called='blocked passage',
        sight='_the_passage [here] [is/1/v] blocked by _a_recent_cave-in',
        exits={'south': '@giant_room', 'giant': '@giant_room',
               'leave': '@giant_room'}),

    CaveRoom('@end_of_immense_passage',
        article='the',
        called='end of immense passage',
        sight='[*/s] [are/v] at _one_end of _an_immense_north/south_passage',
        exits={'south': '@giant_room', 'giant': '@giant_room',
               'tunnel': '@giant_room', 'north': '@rusty_door'}),

    RustyDoor('@rusty_door',
        article='a',
        called='(massive) (rusty) (iron) door',
        referring='| door',
        qualities=['doorway', 'metal'],
        allowed=can.permit_any_item,
        open=False,
        locked=True,
        connects=['@end_of_immense_passage', '@cavern_with_waterfall'],
        sight="""

        a door, placed to restrict passage to the north, which [is/v]
        [now] [open/@rusty_door/a]"""),

    CaveRoom('@cavern_with_waterfall',
        article='the',
        called='cavern with waterfall',
        sight="""

        [*/s] [are/v] in _a_magnificent_cavern with _a_rushing_stream, which
        [cascade/1/v] over [@waterfall/o] into _a_roaring_whirlpool
        which [disappear/1/v] through _a_hole in _the_floor

        _passages [exit/2/v] to the south and west""",
        exits={'south': '@end_of_immense_passage',
               'leave': '@end_of_immense_passage', 'giant': '@giant_room',
               'west': '@steep_incline'}),

    Thing('@waterfall part_of @cavern_with_waterfall',
        article='a',
        called='sparkling waterfalll',
        referring='rushing sparkling roaring | stream creek river spring ' +
                  'waterfall whirlpool',
        qualities=['liquid'],
        source='@water',
        mention=False),

    Thing('@trident in @cavern_with_waterfall',
        article='a',
        called='jewel-encrusted trident',
        referring='jeweled | trident',
        qualities=['treasure', 'metal'],
        sight='a jewel-encrusted trident'),

    CaveRoom('@soft_room',
        article='the',
        called='soft room',
        sight="""

        [*/s] [are/v] in _the_Soft_Room

        _the_walls [are/2/v] covered with _heavy_curtains, _the_floor with
        _a_thick_pile_carpet

        _moss [cover/1/v] _the_ceiling""",
        exits={'west': '@swiss_cheese_room',
               'leave': '@swiss_cheese_room'}),

    Thing('@pillow in @soft_room',
        article='a',
        called='(small) (velvet) pillow',
        referring='| pillow',
        allowed=can.support_one_item),

    CaveRoom('@oriental_room',
        article='the',
        called='oriental room',
        sight="""

        [this] [is/1/v] _the_Oriental_Room

        _ancient_oriental_cave_drawings [cover/2/v] _the_walls

        _a_gently_sloping_passage [lead/1/v] upward to the north,
        _another_passage [lead/1/v] southeast, and _a_hands_and_knees_crawl
        [lead/1/v] west""",
        exits={'southeast': '@swiss_cheese_room',
               'west': '@large_low_room', 'crawl': '@large_low_room',
               'up': '@misty_cavern', 'north': '@misty_cavern',
               'cavern': '@misty_cavern'}),

    Delicate('@vase in @oriental_room',
        article='a',
        called='(delicate) (precious) (Ming) vase',
        referring='| vase',
        qualities=['treasure'],
        sight='a delicate, precious, Ming vase'),

    CaveRoom('@misty_cavern',
        article='the',
        called='misty cavern',
        sight="""

        [*/s] [are/v] following _a_wide_path around _the_outer_edge of
        _a_large_cavern

        far below, through _a_heavy_white_mist, _strange_splashing_noises
        [are/2/v] heard

        _the_mist [rise/1/v] up through _a_fissure in _the_ceiling

        _the_path [exit/1/v] to the south and west""",
        exits={'south': '@oriental_room', 'oriental': '@oriental_room',
               'west': '@alcove'}),

    CaveRoom('@alcove',
        article='the',
        called='alcove',
        sight="""

        [*/s] [are/v] in _an_alcove

        _a_small_northwest_path [seem/1/v] to widen after _a_short_distance

        _an_extremely_tight_tunnel [lead/1/v] east

        it [look/1/v] like _a_very_tight_squeeze

        _an_eerie_light [is/1/v] seen at _the_other_end""",
        exits={'northwest': '@misty_cavern', 'cavern': '@misty_cavern',
               'east': '@plover_room'}),

    CaveRoom('@plover_room',
        article='the',
        called='plover room',
        sight="""

        [*/s] [are/v] in _a_small_chamber lit by _an_eerie_green_light

        _an_extremely_narrow_tunnel [exit/1/v] to the west

        _a_dark_corridor [lead/1/v] northeast""",
        glow=0.5,
        exits={'west': '@alcove', 'plover': '@y2',
               'northeast': '@dark_room', 'dark': '@dark_room'}),

    Thing('@emerald in @plover_room',
        article='an',
        called='emerald',
        referring='| jewel egg',
        qualities=['treasure'],
        sight='an emerald the size of a plover\'s egg'),

    CaveRoom('@dark_room',
        article='the',
        called='dark room',
        sight="""

        [*/s] [are/v] in _the_Dark_Room

        _a_corridor leading south [is/1/v] _the_only_exit""",
        exits={'south': '@plover_room', 'plover': '@plover_room',
               'leave': '@plover_room'}),

    Thing('@pyramid in @dark_room',
        article='a',
        called='platinum pyramid',
        referring='| platinum pyramid',
        qualities=['treasure', 'metal'],
        sight='a platinum pyramid, eight inches on a side'),

    CaveRoom('@arched_hall',
        article='the',
        called='arched hall',
        sight="""

        [*/s] [are/v] in an arched hall

        _a_coral_passage once continued up and east from [here], but [is/1/v]
        [now] blocked by _debris""",
        smell="sea water",
        exits={'down': '@shell_room', 'shell': '@shell_room',
               'leave': '@shell_room'}),

    CaveRoom('@shell_room',
        article='the',
        called='shell room',
        referring='shell |',
        sight="""

        [*/s] [are/v] in _a_large_room carved out of _sedimentary_rock

        _the_floor and _walls [are/2/v] littered with _bits of _shells embedded
        in _the_stone

        _a_shallow_passage [proceed/1/v] downward, and _a_somewhat_steeper_one
        [lead/1/v] up

        a low hands and knees passage [enter/1/v] from the south""",
        exits={'up': '@arched_hall', 'hall': '@arched_hall',
               'down': '@long_sloping_corridor',
               'south': '@complex_junction'}),

    Oyster('@oyster in @shell_room',
        article='a',
        called='(enormous) clam',
        referring='tightly closed tightly-closed | bivalve',
        open=False,
        sight='a tightly-closed and enormous bivalve'),

    Thing('@pearl in @oyster',
        article='a',
        called='glistening pearl',
        referring='| pearl',
        qualities=['treasure'],
        sight='a glistening pearl'),

    CaveRoom('@long_sloping_corridor',
        article='the',
        called='long sloping corridor',
        sight="""

        [*/s] [are/v] in _a_long_sloping_corridor with _ragged_sharp_walls""",
        exits={'up': '@shell_room', 'shell': '@shell_room',
               'down': '@cul_de_sac'}),

    CaveRoom('@cul_de_sac',
        article='the',
        called='cul-de-sac',
        sight='[*/s] [are/v] in _a_cul-de-sac about eight feet across',
        exits={'up': '@long_sloping_corridor',
               'leave': '@long_sloping_corridor',
               'shell': '@shell_room'}),

    CaveRoom('@anteroom',
        article='the',
        called='anteroom',
        sight="""

        [*/s] [are/v] in _an_anteroom leading to _a_large_passage to the east

        _small_passages [go/2/v] west and up

        _the_remnants of recent digging [are/2/v] evident

        _a_sign in midair [here] [say/1/v]: "Cave under construction beyond
        this point. Proceed at own risk. \[Witt Construction Company]\"""",
        exits={'up': '@complex_junction', 'west': '@bedquilt',
               'east': '@witts_end'}),

    Thing('@magazine in @anteroom',
        article='some',
        called='magazines',
        referring='a few recent | issues magazine magazines',
        number='plural',
        sight='a few recent issues of "Spelunker Today" magazine'),

    CaveRoom('@maze_15',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisty_little_passages, all different""",
        exits={'south': '@maze_17', 'southwest': '@maze_18',
               'northeast': '@maze_19', 'southeast': '@maze_20',
               'up': '@maze_21', 'northwest': '@maze_22', 'east': '@maze_23',
               'west': '@maze_24', 'north': '@maze_25',
               'down': '@west_end_of_long_hall'}),

    CaveRoom('@witts_end',
        called="Witt's End",
        sight="""

        [*/s] [are/v] at _Witt's_End

        _passages [lead/2/v] off ... well, east and west""",
        exits={'east': '@anteroom', 'west': '@crossover'}),
        # NEXT STEPS Passages should lead off "in ALL directions", randomness

    CaveRoom('@mirror_canyon',
        article='the',
        called='mirror canyon',
        sight="""

        [*/s] [are/v] in _a_north/south_canyon about 25 feet across

        _the_floor [is/1/v] covered by _white_mist seeping in from the north

        _the_walls [extend/2/v] upward for well over 100 feet

        suspended from _some_unseen_point far above [*/s],
        _an_enormous_two-sided_mirror [hang/ing/1/v] parallel to and midway 
        between the _canyon_walls

        (_The_mirror [is/1/v] obviously provided for the use of _the_dwarves,
        who are extremely vain.)

        _a_small_window [is/1/v] seen in _either_wall, some fifty feet up""",
        exits={'south': '@secret_canyon_above_room',
               'north': '@reservoir', 'reservoir': '@reservoir'}),

    CaveRoom('@window_on_pit_redux',
        article='the',
        called='window on pit',
        sight="""

        [*/s] [are/v] at _a_low_window overlooking _a_huge_pit, which
        [extend/1/v] up out of sight

        _a_floor [is/1/v] indistinctly visible over 50 feet below

        _traces of _white_mist [cover/2/v] _the_floor of _the_pit, becoming
        thicker to the left

        _marks in _the_dust around _the_window [seem/2/v] to indicate that
        _someone has been [here] recently

        directly across _the_pit from [*/o] and 25 feet away there [is/1/v]
        _a_similar_window looking into _a_lighted_room

        _a_shadowy_figure [is/1/v] seen there peering back at [*/s]""",
        exits={'west': '@junction_of_three_secret_canyons'}),

    CaveRoom('@top_of_stalactite',
        article='the',
        called='top of stalactite',
        sight="""

        _a_large_stalactite [extend/1/v] from _the_roof and almost [reach/1/v]
        _the_floor below

        [*/s] could climb down _it, and jump from _it to _the_floor, but having
        done so [*/s] would be unable to reach _it to climb back up""",
        exits={'north': '@secret_canyon_above_passage', 'down': '@maze_4'}),

    CaveRoom('@maze_16',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_little_maze of _twisting_passages, all different""",
        exits={'southwest': '@maze_17', 'north': '@maze_18',
               'east': '@maze_19', 'northwest': '@maze_20',
               'southeast': '@maze_21', 'northeast': '@maze_22',
               'west': '@maze_23', 'down': '@maze_24', 'up': '@maze_25',
               'south': '@dead_end_15'}),

    CaveRoom('@reservoir',
        article='the',
        called='edge of the reservoir',
        referring='| edge',
        sight="""

        [*/s] [are/v] at _the_edge of _a_large_underground_reservoir

        _an_opaque_cloud of _white_mist [fill/1/v] _the_room and [rise/1/v]
        rapidly upward

        _the_lake [is/1/v] fed by _a_stream, which [tumble/1/v] out of _a_hole
        in _the_wall about 10 feet overhead and [splash/1/v] noisily into
        _the_water somewhere within _the_mist

        _the_only_passage [go/1/v] back toward the south""",
        exits={'south': '@mirror_canyon', 'leave': '@mirror_canyon'}),

    Thing('@lake part_of @reservoir',
        article='a',
        called='a large underground lake',
        referring='large underground | stream creek river spring lake',
        source='@water',
        mention=False),

    CaveRoom('@dead_end_14',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'southeast': '@maze_13'}),

    Thing('@chest in @dead_end_14',
        article='the',
        called="(pirate's) treasure chest",
        referring='| chest',
        qualities=['treasure'],
        sight="the pirate's treasure chest",
        allowed=can.contain_any_treasure),

    CaveRoom('@northeast_end',
        article='the',
        called='northeast end',
        sight="""

        [*/s] [are/v] at _the_northeast_end of _an_immense_room, even larger
        than _the_giant_room

        it [appear/1/v] to be _a_repository for _the_"ADVENTURE"_program

        _massive_torches far overhead [bathe/2/v] _the_room with
        _smoky_yellow_light

        scattered about [*/s] [see/v] _a_pile_of_bottles (all of them
        empty), _a_nursery of _young_beanstalks murmuring quietly, _a_bed of
        _oysters, _a_bundle of _black_rods with _rusty_stars on _their_ends,
        and _a_collection_of_brass_lanterns

        off to _one_side a_great_many_dwarves [sleep/ing/2/v] on _the_floor,
        snoring loudly

        _a_sign nearby [read/1/v]: "Do not disturb the dwarves!"

        _an_immense_mirror [hang/ing/v] against _one_wall, and [stretch/1/v]
        to _the_other_end of _the_room, where _various_other_sundry_objects
        [are/2/v] glimpsed dimly in the distance""",
        exits={'southwest': '@southwest_end'}),

    CaveRoom('@southwest_end',
        article='the',
        called='southwest end',
        sight="""

        [*/s] [are/v] at _the_southwest end of _the_repository

        to _one_side [is/1/v] _a_pit full of _fierce_green_snakes

        on _the_other_side [is/1/v] _a_row of _small_wicker_cages, each of
        which [contain/1/v] _a_little_sulking_bird

        in _one_corner [is/1/v] _a_bundle of _black_rods with _rusty_marks on
        _their_ends

        _a_large_number of _velvet_pillows [are/2/v] scattered about on
        _the_floor

        _a_vast_mirror [stretch/1/v] off to the northeast

        at [*'s] _feet [is/1/v] _a_large_steel_grate, next to which
        [is/1/v] _a_sign which [read/1/v], "Treasure vault. Keys in Main
        Office\"""",
        exits={'northeast': '@northeast_end'}),

    Thing('@black_rod in @southwest_end',
        article='a',
        called='small black rod',
        referring='small black | rod',
        sight='a small black rod'),

    Button('@button in @southwest_end',
        article='a',
        called='button',
        referring='red | button',
        sight='just a red button'),

    CaveRoom('@southwest_side_of_chasm',
        article='the',
        called='southwest side of chasm',
        sight="""

        [*/s] [are/v] on _one_side of _a_large,_deep_chasm

        _a_heavy_white_mist rising up from below [obscure/1/v] _all_view of
        _the_far_side

        _a_southwest_path [lead/1/v] away from _the_chasm into
        _a_winding_corridor""",
        exits={'southwest': '@sloping_corridor',
               'over': '@northeast_side_of_chasm',
               'cross': '@northeast_side_of_chasm',
               'northeast': '@northeast_side_of_chasm'}),

    Troll('@troll in @southwest_side_of_chasm',
        article='a',
        called='(burly) troll',
        referring=' | monster guardian',
        sight='[this] [is/1/v] just a burly troll, barring the way',
        allowed=can.possess_any_treasure,
        blocked=['northeast', 'over', 'cross']),

    CaveRoom('@sloping_corridor',
        article='the',
        called='sloping corridor',
        sight="""

        [*/s] [are/v] in _a_long_winding_corridor sloping out of sight in
        both directions""",
        exits={'down': '@large_low_room',
               'up': '@southwest_side_of_chasm'}),

    CaveRoom('@secret_canyon',
        article='the',
        called='secret canyon',
        sight="""

        [*/s] [are/v] in _a_secret_canyon which [exit/1/v] to the north and
        east""",
        exits={'north': '@secret_canyon_above_room',
               'east': '@secret_east_west_canyon'}),

    Thing('@rug in @secret_canyon',
        article='a',
        called='(Persian) rug',
        referring='persian | rug',
        qualities=['treasure'],
        allowed=can.support_any_item_or_dragon,
        sight='a Persian rug'),

    Dragon('@dragon on @rug',
        article='a',
        called='huge dragon',
        referring='huge green fierce | dragon',
        sight='[this] [is/1/v] just a huge dragon, barring the way',
        blocked=['north', 'onward']),

    CaveRoom('@northeast_side_of_chasm',
        article='the',
        called='northeast side of chasm',
        sight="""

        [*/s] [are/v] on _the_far_side of _the_chasm

        _a_northeast_path [lead/1/v] away from _the_chasm on [this] side""",
        exits={'northeast': '@corridor',
               'over': '@southwest_side_of_chasm',
               'fork': '@fork_in_path',
               'view': '@breath_taking_view',
               'barren': '@front_of_barren_room',
               'southwest': '@southwest_side_of_chasm',
               'cross': '@southwest_side_of_chasm'}),

    CaveRoom('@corridor',
        article='the',
        called='corridor',
        sight="""

        [*/s] [are/v] in a long east/west corridor

        _a_faint_rumbling_noise [is/1/v] heard in the distance""",
        exits={'west': '@northeast_side_of_chasm',
               'east': '@fork_in_path', 'fork': '@fork_in_path',
               'view': '@breath_taking_view',
               'barren': '@front_of_barren_room'}),

    CaveRoom('@fork_in_path',
        article='the',
        called='fork in path',
        sight="""

        _the_path [fork/1/v] [here]

        _the_left_fork [lead/1/v] northeast

        _a_dull_rumbling [seem/1/v] to get louder in that direction

        _the_right_fork [lead/1/v] southeast down _a_gentle_slope

        _the_main_corridor [enter/1/v] from the west""",
        exits={'west': '@corridor',
               'northeast': '@junction_with_warm_walls',
               'left': '@junction_with_warm_walls',
               'southeast': '@limestone_passage',
               'right': '@limestone_passage',
               'down': '@limestone_passage',
               'view': '@breath_taking_view',
               'barren': '@front_of_barren_room'}),

    CaveRoom('@junction_with_warm_walls',
        article='the',
        called='junction with warm walls',
        sight="""

        _the_walls [are/2/v] quite warm here

        from the north [*/s] [hear/v] _a_steady_roar, so loud that
        _the_entire_cave [seem/1/v] to be trembling

        _another_passage [lead/1/v] south, and _a_low_crawl [go/1/v] east""",
        exits={'south': '@fork_in_path', 'fork': '@fork_in_path',
               'north': '@breath_taking_view',
               'view': '@breath_taking_view',
               'east': '@chamber_of_boulders',
               'crawl': '@chamber_of_boulders'}),

    CaveRoom('@breath_taking_view',
        article='the',
        called='breath-taking view',
        sight="""

        [*/s] [are/v] on _the_edge of _a_breath-taking_view

        far below [*/s] [is/1/v] _an_active_volcano, from which _great_gouts
        of _molten_lava [come/2/v] surging out, cascading back down into
        _the_depths

        _the_glowing_rock [fill/1/v] _the_farthest_reaches of _the_cavern with
        _a_blood-red_glare, giving _everything _an_eerie,_macabre_appearance

        _the_air [is/1/v] filled with flickering sparks of ash

        _the_walls [are/2/v] hot to the touch, and _the_thundering of
        _the_volcano [drown/1/v] out all other sounds

        embedded in _the_jagged_roof far overhead [are/1/v]
        _myriad_twisted_formations composed of _pure_white_alabaster,
        which scatter _the_murky_light into _sinister_apparitions upon
        _the_walls

        to _one_side [is/1/v] _a_deep_gorge, filled with _a_bizarre_chaos of
        _tortured_rock which seems to have been crafted by _the_devil _himself

        _an_immense_river of _fire [crash/1/v] out from _the_depths of
        _the_volcano, [burn/1/v] its way through _the_gorge, and [plummet/1/v]
        into _a_bottomless_pit far off to [*'s] left

        to _the_right, _an_immense_geyser of _blistering_steam [erupt/1/v]
        continuously from _a_barren_island in _the_center of
        _a_sulfurous_lake, which bubbles ominously

        _the_far_right_wall [is/1/v] aflame with _an_incandescence of its
        own, which [lend/1/v] _an_additional_infernal_splendor to
        _the_already_hellish_scene

        _a_dark,_foreboding_passage [exit/1/v] to the south""",
        smell="a heavy smell of brimstone",
        exits={'south': '@junction_with_warm_walls',
               'tunnel': '@junction_with_warm_walls',
               'leave': '@junction_with_warm_walls',
               'fork': '@fork_in_path',
               'down': '@west_end_of_long_hall',
               'jump': '@west_end_of_long_hall'}),

    CaveRoom('@chamber_of_boulders',
        article='the',
        called='chamber of boulders',
        sight="""

        [*/s] [are/v] in _a_small_chamber filled with _large_boulders

        _the_walls [are/2/v] very warm, causing _the_air in _the_room to be
        almost stifling from _the_heat

        _the_only_exit [is/1/v] _a_crawl heading west, through which [is/1/v]
        coming _a_low_rumbling""",
        exits={'west': '@junction_with_warm_walls',
               'leave': '@junction_with_warm_walls',
               'crawl': '@junction_with_warm_walls',
               'fork': '@fork_in_path', 'view': '@breath_taking_view'}),

    Thing('@spices in @chamber_of_boulders',
        article='some',
        called='rare spices',
        referring='rare | spice spices',
        qualities=['treasure'],
        sight='rare spices'),

    CaveRoom('@limestone_passage',
        article='the',
        called='limestone passage',
        sight="""

        [*/s] [are/v] walking along _a_gently_sloping_north/south_passage
        lined with _oddly_shaped_limestone_formations""",
        exits={'north': '@fork_in_path', 'up': '@fork_in_path',
               'fork': '@fork_in_path',
               'south': '@front_of_barren_room',
               'down': '@front_of_barren_room',
               'barren': '@front_of_barren_room',
               'view': '@breath_taking_view'}),

    CaveRoom('@front_of_barren_room',
        article='the',
        called='front of barren room',
        sight="""

        [*/s] [stand/ing/v] at _the_entrance to _a_large,_barren_room

        _a_sign posted above _the_entrance [read/1/v]: "Caution! Bear in
        room!\"""",
        exits={'west': '@limestone_passage',
               'up': '@limestone_passage', 'fork': '@fork_in_path',
               'east': '@barren_room', 'in': '@barren_room',
               'barren': '@barren_room', 'enter': '@barren_room',
               'view': '@breath_taking_view'}),

    CaveRoom('@barren_room',
        article='the',
        called='barren room',
        sight="""

        [*/s] [are/v] inside _a_barren_room

        _the_center of _the_room [is/1/v] completely empty except for
        _some_dust

        marks in _the_dust [lead/2/v] away toward _the_far_end of _the_room

        the only exit [is/1/v] the way you came in""",
        exits={'west': '@front_of_barren_room',
               'leave': '@front_of_barren_room',
               'fork': '@fork_in_path',
               'view': '@breath_taking_view'}),

    Bear('@bear in @barren_room',
        article='a',
        called='(ferocious) (cave) bear',
        referring=' | animal creature',
        sight='a ferocious cave bear, currently [angry/@bear/a]',
        allowed=can.possess_any_thing),

    Thing('@hook part_of @barren_room',
        article='a',
        called='(small) hook',
        referring='| peg',
        qualities=['metal'],
        allowed=can.support_chain,
        sight='a small metal hook, somehow affixed to the cave wall'),

    Thing('@chain on @hook',
        article='a',
        called='(golden) chain',
        referring='gold | leash',
        qualities=['treasure', 'metal'],
        sight='just an ordinary golden chain'),

    CaveRoom('@maze_17',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _twisting_little_passages, all different""",
        exits={'west': '@maze_15', 'southeast': '@maze_18',
               'northwest': '@maze_19', 'southwest': '@maze_20',
               'northeast': '@maze_21', 'up': '@maze_22',
               'down': '@maze_23', 'north': '@maze_24',
               'south': '@maze_25', 'east': '@maze_16'}),

    CaveRoom('@maze_18',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_little_maze of _twisty_passages, all different""",
        exits={'northwest': '@maze_15', 'up': '@maze_17',
               'north': '@maze_19', 'south': '@maze_20', 'west': '@maze_21',
               'southwest': '@maze_22', 'northeast': '@maze_23',
               'east': '@maze_24', 'down': '@maze_25',
               'southeast': '@maze_16'}),

    CaveRoom('@maze_19',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_twisting_maze of _little_passages, all different""",
        exits={'up': '@maze_15', 'down': '@maze_17', 'west': '@maze_18',
               'northeast': '@maze_20', 'southwest': '@maze_21',
               'east': '@maze_22', 'north': '@maze_23',
               'northwest': '@maze_24', 'southeast': '@maze_25',
               'south': '@maze_16'}),

    CaveRoom('@maze_20',
        article='the',
        called='maze',
        sight="""
        [*/s] [are/v] in _a_twisting_little_maze of _passages, all different""",
        exits={'northeast': '@maze_15', 'north': '@maze_17',
               'northwest': '@maze_18', 'southeast': '@maze_19',
               'east': '@maze_21', 'down': '@maze_22',
               'south': '@maze_23', 'up': '@maze_24',
               'west': '@maze_25', 'southwest': '@maze_16'}),

    CaveRoom('@maze_21',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_twisty_little_maze of _passages, all different""",
        exits={'north': '@maze_15', 'southeast': '@maze_17',
               'down': '@maze_18', 'south': '@maze_19',
               'east': '@maze_20', 'west': '@maze_22',
               'southwest': '@maze_23', 'northeast': '@maze_24',
               'northwest': '@maze_25', 'up': '@maze_16'}),

    CaveRoom('@maze_22',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_twisty_maze of _little_passages, all different""",
        exits={'east': '@maze_15', 'west': '@maze_17', 'up': '@maze_18',
               'southwest': '@maze_19', 'down': '@maze_20',
               'south': '@maze_21', 'northwest': '@maze_23',
               'southeast': '@maze_24', 'northeast': '@maze_25',
               'north': '@maze_16'}),

    CaveRoom('@maze_23',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_little_twisty_maze of _passages, all different""",
        exits={'southeast': '@maze_15', 'northeast': '@maze_17',
               'south': '@maze_18', 'down': '@maze_19', 'up': '@maze_20',
               'northwest': '@maze_21', 'north': '@maze_22',
               'southwest': '@maze_24', 'east': '@maze_25',
               'west': '@maze_16'}),

    CaveRoom('@maze_24',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _little_twisting_passages, all different""",
        exits={'down': '@maze_15', 'east': '@maze_17',
               'northeast': '@maze_18', 'up': '@maze_19',
               'west': '@maze_20', 'north': '@maze_21', 'south': '@maze_22',
               'southeast': '@maze_23', 'southwest': '@maze_25',
               'northwest': '@maze_16'}),

    CaveRoom('@maze_25',
        article='the',
        called='maze',
        sight="""

        [*/s] [are/v] in _a_maze of _little_twisty_passages, all different""",
        exits={'southwest': '@maze_15', 'northwest': '@maze_17',
               'east': '@maze_18', 'west': '@maze_19', 'north': '@maze_20',
               'down': '@maze_21', 'southeast': '@maze_22',
               'up': '@maze_23', 'south': '@maze_24',
               'northeast': '@maze_16'}),

    CaveRoom('@dead_end_15',
        article='the',
        called='dead end',
        referring='dead | end',
        exits={'north': '@maze_16', 'leave': '@maze_16'})]

