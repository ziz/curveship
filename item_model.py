'Represent existents with Item classes, instantiated by games/stories.'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import random
import re
import types

import can
import discourse_model

def check_attributes(identifier, required, impossible, attributes):
    'Raise errors if required attributes are missing or impossile ones present.'
    some_wrong = ''
    if 'parent' in impossible:
        if not len(identifier.split()) == 1:
            some_wrong += ('The item "' + identifier + '" has a link and ' +
                           'parent specified, but this type of item is ' +
                           'placed automatically in the item tree and cannot ' +
                           'have these.')
        impossible.remove('parent')
    for missing in required:
        if missing not in attributes:
            some_wrong += ('The item "' + identifier + '" is missing ' +
                'a required attribute: "' + missing + '".\n')
    for present in impossible:
        if present in attributes:
            some_wrong += ('For the item "' + identifier + '" there is ' +
                'an attempt to specify the attribute "' + present + 
                '" which cannot be specified for this type of item.\n')
    if len(some_wrong) > 0:
        raise StandardError(some_wrong[:-1])

def determine_called(called):
    'Using the called string, determine the name triple.'
    match = re.match('(\(.*\)) +[^\(]', called)
    if match is None:
        before_adjs = []
    else:
        before_adjs = match.group(1)[1:-1].split(') (')
        called = called[match.end(1) + 1:]
        for i in range(0, len(before_adjs)):
            before_adjs[i] = before_adjs[i]
    match = re.search('[^\)] +(\(.*\))$', called)
    if match is None:
        after_adjs = []
    else:
        after_adjs = match.group(1)[1:-1].split(') (')
        called = re.sub(' +' + match.group(1), '', called)
        called = called[:match.start(1) - 1:]
        for i in range(0, len(after_adjs)):
            after_adjs[i] = after_adjs[i]
    return (before_adjs, called, after_adjs)

def set_features(item, category, keywords):
    """Sets features modeling the current state (condition) of an Item.

    These data attributes represent the item's important features within
    the fiction/game world. The values held in particular entries are
    changed by Modify actions. The location and configuration of an item
    in the overall context of the world (what parent it has and what its link
    to the parent is) is not represented here. That aspect of the world is
    changed by Configure instead of Modify. These features model the item
    itself, not where it is located.

    The built-in features, represented by data attributes, are:

    article: string
        The initial article to use. "a" will be adjusted to "an" if
        necessary when text is generated.

    called: string
        What the item can be called when text is generated.

    referring: string | None
        Additional words that can be typed to refer to the item. Optional words
        first, separated by spaces; then "|", then space-delimited names. If 
        referring is the '' (the empty string, which is the default), there are 
        no special words added, but the item can still be referred to by words
        derived from its category and qualities. For the special case in which
        there should be no way to refer to an item, set referring to None.

    qualities: list of strings
        Terms describing the item; synonyms of these are used in recognition
        and the terms can be used in simulation.

    gender: 'female' | 'male' | 'neuter'
        Whether the item should be referred to as a she, he, or it.

    glow: float
        How much light the item is radiating, typically in (0, 1).
        Can be set outside of (0, 1) for supernatural reasons.

    number: 'singular' | 'plural'
        Whether the item should be referred to in the singular or plural.

    prominence: float
        How visible or noticeable an item is, typically in (0, 1).

    transparent: True | False
        Can one see through the item and see what is inside?

    mention: True | False
        Should the item ever be mentioned (for instance, in lists)? Almost
        everything should be, but not, for instance, part of another item 
        that is described in the main description of the parent item.

    allowed: can.function(tag, link, world)
        Determines what an item can contain. Specifically, returns whether
        the item 'tag' can be a child of the parent, in the specified link
        relationship, given the situation of world.

    shared: list of strings
        If a Room, the tags of SharedThings that this Room has; otherwise [].

    sight: string
        Template that produces a description of what an agent sees when
        looking at an item.

    touch: string
        Template that produces a description of what an agent feels when
        touching at an item. Should be able to complete the sentence
        "The adventurer feels ..." or "You feel ..."

    hearing: string
        Simimlar template for hearing.

    smell: string
        Simimlar template for hearing.

    taste: string
        Simimlar template for taste."""

    settings = {
        'article': '',
        'called': '',
        'referring': '',
        'qualities': [],
        'glow': 0.0,
        'prominence': 0.5,
        'transparent': False,
        'mention': True,
        'allowed' : can.not_have_items,
        'shared' : []
    }
    settings.update(keywords)
    if (settings['referring'] is not None and
        len(settings['referring']) > 0 and '|' not in settings['referring']):
        raise StandardError('The item tagged "' + str(item) +
         '" has a nonempty "referring" attribute without a "|" ' +
         'separator. Place "|" after any optional words and before ' +
         'any names, at the very beginning or end, if appropriate.')
    if category not in settings['qualities']:
        settings['qualities'] += [category]
    for (name, value) in settings.items():
        if re.search('[^a-z_]', name):
            raise StandardError('A feature with invalid name "' + name +
             '" is used in the fiction module.')
        setattr(item, name, value)
    return item

class Item(object):
    'Abstract base class for items.'

    def __init__(self, tag_and_parent, category, **keywords):        
        if self.__class__ == Item:
            raise StandardError('Attempt in Item "' + self._tag +
                  '" to instantiate abstract base class world_model.Item')
        if tag_and_parent == '@cosmos':
            self._tag = tag_and_parent
            (self.link, self.parent) = (None, None)
        else:
            (self._tag, self.link, self.parent) = tag_and_parent.split()
        if (not type(self._tag) == types.StringType) or len(self._tag) == 0:
            raise StandardError('An Item lacking a "tag" attribute, ' +
             'or with a non-string or empty tag, has been specified. A ' +
             'valid tag is required for each item.')
        if not re.match('@[a-z0-9_]{2,30}', self._tag):
            raise StandardError('The tag "' + self._tag +
             '" is invalid. Tags start with "@" and otherwise consist of ' +
             '2-30 characters which are only lowercase letters, numerals, ' +
             'and underscores.')
        self._children = []
        for i in ['actor', 'door', 'room', 'thing', 'substance']:
            setattr(self, i, (category == i))
        self.blanked = False
        # Five of these features have to be set "manually" (private properties
        # set directly) now because their setters depend on each other.
        #
        # Called: what an item is called is included in the way to refer to it.
        # Gender and number: pronouns that can refer to an item depend on those.
        # Referring extra: The string with "extra" referring expressions.
        # Qualities: These are expanded into elements of a referring expression.
        #
        # Once the four setters run, whichever one runs last will leave 
        # "._referring" in the correct state.
        self._called = ([], '', [])
        self._gender = 'neuter'
        self._number = 'singular'
        self._referring_extra = '|'
        self._qualities = []
        self._referring = (set(), set(), set())
        self._sense = {}
        for sense in ['sight', 'touch', 'hearing', 'smell', 'taste']:
            setattr(self, sense, '')
        self = set_features(self, category, keywords)

    def __str__(self):
        return self._tag

    def __eq__(self, item):
        if item is None:
            return False
        if type(item) == types.StringType:
            return str(self) == item
        self_list = [str(self), self.article, self.called]
        item_list = [str(item), item.article, item.called]
        equal_attrs = (set(dir(self)) == set(dir(item)))
        if equal_attrs:
            for i in dir(self):
                if (not i[0] == '_' and not callable(getattr(self, i))):
                    equal_attrs &= (getattr(self, i) == getattr(item, i))
        return (self_list == item_list) and equal_attrs

    def __ne__(self, item):
        return not self.__eq__(item)

    def get_called(self):
        return self._called
    def set_called(self, string):
        self._called = determine_called(string)
        self._update_referring()
    called = property(get_called, set_called, 'Names used in output.')

    def get_referring(self):
        return self._referring
    def set_referring(self, string):
        self._referring_extra = string
        self._update_referring()
    referring = property(get_referring, set_referring,
                         'Triple of referring expressions.')

    def get_gender(self):
        return self._gender
    def set_gender(self, string):
        self._gender = string
        self._update_referring()
    gender = property(get_gender, set_gender, 'Grammatical gender.')

    def get_number(self):
        return self._number
    def set_number(self, string):
        self._number = string
        self._update_referring()
    number = property(get_number, set_number, 'Grammatical number.')

    def get_qualities(self):
        return self._qualities
    def set_qualities(self, quality_list):
        self._qualities = quality_list
        self._update_referring()
    qualities = property(get_qualities, set_qualities,
                         'Terms used to add referring words.')

    def get_sight(self):
        return self._sense['sight']
    def set_sight(self, string):
        self._sense['sight'] = discourse_model.reformat(string)
    sight = property(get_sight, set_sight,
                     'What is seen when an Item is looked at.')

    def get_touch(self):
        return self._sense['touch']
    def set_touch(self, string):
        'Setter. Needed because strings must be reformatted before being set.'
        self._sense['touch'] = discourse_model.reformat(string)
    touch = property(get_touch, set_touch,
                     'What is felt when an Item is touched.')

    def get_hearing(self):
        return self._sense['hearing']
    def set_hearing(self, string):
        self._sense['hearing'] = discourse_model.reformat(string)
    hearing = property(get_hearing, set_hearing,
                       'What is heard when an Item is listened to.')

    def get_smell(self):
        return self._sense['smell']
    def set_smell(self, string):
        self._sense['smell'] = discourse_model.reformat(string)
    smell = property(get_smell, set_smell,
                     'What is smelled when an Item is sniffed.')

    def get_taste(self):
        return self._sense['taste']
    def set_taste(self, string):
        self._sense['taste'] = discourse_model.reformat(string)
    taste = property(get_taste, set_taste,
                     'What is tasted when an Item is sampled.')

    def _update_referring(self):
        'Determine or update the triple of referring words.'
        if self._referring_extra is None:
            self._referring = ('', '', '')
        else:
            optional, _, names = self._referring_extra.partition('|')
            before = set(optional.strip().split() + self._called[0])
            after = set(optional.strip().split() + self._called[2])
            names = set(names.strip().split())
            if not ' ' in self._called[1]:
                names.add(self._called[1])
            if self.number == 'singular':
                if self.gender == 'neuter':
                    names.add('it')
                elif self.gender == 'female':
                    names.add('her')
                else:
                    names.add('him')
            else:
                names.add('them')
            for i in self.qualities:
                if i in discourse_model.QUALITY_WORDS:
                    (q_before,
                     q_names) = discourse_model.QUALITY_WORDS[i].split('|')
                    before.update(q_before.strip().split())
                    names.update(q_names.strip().split())
            self._referring = (before, names, after)

    def blank(self):
        'Erase an Item when nothing is known about it by an Actor.'
        self.article = 'the'
        self.called = 'object'
        if self.room:
            self.called = 'place'
        elif self.actor:
            self.called = 'individual'
        self.referring = None
        for attr in ['link', 'parent', 'sight', 'touch', 'hearing', 'smell',
                     'taste']:
            setattr(self, attr, '')
        self._children = []
        self.allowed = can.not_have_items
        self.blanked = True

    def noun_phrase(self, discourse=None, entire=True, extra_adjs='',
                    length=0.0):
        'Return the noun phrase representing this Item.'
        string = self.called[1]
        if len(self.called[0]) > 0 and length > 0.0:
            before_adjs = random.choice(self.called[0] + [''])
            string = (before_adjs + ' ' + string).strip()
        if len(self.called[2]) > 0 and length > 0.0:
            after_adjs = random.choice(self.called[2] + [''])
            string = (string + ' ' + after_adjs).strip()
        string = (extra_adjs + ' ' + string).strip()
        if discourse is None:
            # This method was called without a discourse parameter. In this
            # case, the correct article can't be generated and the givens list
            # can't be updated; so, return the noun phrase without an article.
            return string
        if entire:
            use_article = self.article
            if (self.article in discourse.indefinite and
                str(self) in discourse.givens):
                use_article = 'the'
            else:
                if self.article in ['a', 'an']:
                    use_article = 'a'
                    if string[:1] in ['a', 'e', 'i', 'o', 'u']:
                        use_article += 'n'
            if len(use_article) > 0:
                string = use_article + ' ' + string
        discourse.givens.add(str(self))
        return string

    def place(self, world):
        'Returns the Room this Item is located in, according to World.'
        tag = str(self)
        while not world.has('room', tag) and not tag == '@cosmos':
            tag = world.item[tag].parent
        return world.item[tag]

    @property
    def children(self):
        'Return the children of this Item.'
        return self._children

    def add_child(self, link, item, making_change=True):
        'Add (or remove) a child from this Item.'
        if not making_change:
            self.remove_child(link, item)
        else:
            if (link, item) not in self._children:
                self._children.append((link, item))

    def remove_child(self, link, item, making_change=True):
        'Remove (or add) a child from this Item.'
        if not making_change:
            self.add_child(link, item)
        else:
            if (link, item) in self._children:
                self._children.remove((link, item))

    def prevent(self, _, __):
        'By default, items do not prevent actions Subclasses can override.'
        return False

    def react(self, _, __):
        'By default, items do nothing when reacting. Subclasses can override.'
        return []

    def react_to_failed(self, _, __):
        'By default, items do nothing when reacting to a failed action.'
        return []


class Actor(Item):
    """Any Item that can initiate action, whether human-like or not.

    Features of interest:

    alive: True | False
        Actors can only act and react if alive. If not specified, this feature
        will always be True. Things can also have an alive feature, but it must
        be set when needed. It should probably be set on a subclass created
        for a particular Thing that can react and prevent.

    refuses: list of (string, when.function(world), string)
        Determines what an actor will refuse to do when commanded. The first
        string is matched against actions; the function determines whether or
        not the refusal will take place given a match; and the final string
        is a template used to generate a message explaining the refusal."""

    def __init__(self, tag_and_parent, **keywords):
        if 'alive' not in keywords:
            self.alive = True
        if 'refuses' not in keywords:
            self.refuses = []
        else:
            self.refuses = keywords['refuses']
            del(keywords['refuses'])
        Item.__init__(self, tag_and_parent, 'actor', **keywords)

    def exits(self, concept):
        "Return this Actor's current Room's exit dictionary."
        return concept.room_of(str(self)).exits

    def act(self, command_map, concept):
        'The default act method runs a script, if there is one.'
        if hasattr(self, 'script') and len(self.script) > 0:
            next_command = self.script.pop(0)
            if hasattr(self, 'script_loops'):
                self.script.append(next_command)
            next_command = next_command.split()
            return [self.do_command(next_command, command_map, concept)]
        return []

    def do_command(self, command_words, command_map, concept):
        'Return the Action that would result from the provided command.'
        if type(command_words) == types.StringType:
            command_words = command_words.split()
        head = command_words[0].lower()
        if not hasattr(command_map, head):
            raise StandardError('The command headed with "' + head +
             '" is defined in the discourse, but the routine to build an ' +
             'action from it is missing.')
        else:
            mapping = getattr(command_map, head)
            return mapping(str(self), command_words, concept)


class Door(Item):
    """An Item representing a doorway, portal, or passage between two places.

    Features of interest

    connects: list of two strings
        Each string is the tag of a Room; This Door connects the two."""

    def __init__(self, tag, **keywords):
        check_attributes(tag, ['connects'], ['parent', 'shared'], keywords)
        tag_and_parent = tag + ' of @cosmos'
        keywords['allowed'] = can.permit_any_item
        Item.__init__(self, tag_and_parent, 'door', **keywords)


class Room(Item):
    """An Item representing a physical location.

    Features that are particular to Rooms:

    exits: dictionary of string: string
        The key is a direction; the value is the tag of the Door or Room in 
        that direction.

    shared: list of strings
        Each string is the tag of a SharedThing; That Item is present in this
        room and all other rooms that list it.

    view: dictionary of string: (float, string)
        The key is the tag of a Room which is visible from this one; the tuple
        that is the value has the visibility of that room (a floating point
        number in (0, 1)) and a string which is used to generate a textual
        description of the direction of that room."""

    def __init__(self, tag, **keywords):
        check_attributes(tag, ['exits'], ['parent'], keywords)
        tag_and_parent = tag + ' of @cosmos'
        keywords['allowed'] = can.contain_permit_and_have_parts
        self.exits = keywords['exits']
        del(keywords['exits'])
        self.view = {}
        if 'view' in keywords:
            self.view = keywords['view']
            del(keywords['view'])
        if 'glow' not in keywords:
            keywords['glow'] = 1.0
        keywords['prominence'] = 1.0
        Item.__init__(self, tag_and_parent, 'room', **keywords)

    def exit(self, direction):
        'Return the Room or Door that lies in this direction, if there is one.'
        if direction in self.exits and self.exits[direction][0] == '@':
            # The key exists in the dictionary and the value begins with
            # '@', which means it is a tag. If someone writes a template
            # beginning with '@', this will fail.
            return self.exits[direction]
        else:
            return None


class Thing(Item):
    'An item that is not a room, has no concept, and cannot act.'

    def __init__(self, tag_and_parent, **keywords):
        check_attributes(tag_and_parent, [], ['exits', 'refuses', 'shared'],
                         keywords)
        Item.__init__(self, tag_and_parent, 'thing', **keywords)


class SharedThing(Thing):
    """A special sort of (large) Thing that appears in more than one room.

    Note that SharedThing is a subclass of Thing and shares the same category:
    example.thing is True for a SharedThing; there is no 'sharedthing' category.
    However, all SharedThings will have an attribute "sharedthing" that is set
    to True. Testing hasattr(item, 'sharedthing') will determine if the item is
    a SharedThing.

    SharedThing is provided to allow implementation of things like the sky, the
    sun, or a massive wall of the sort the United States has erected along the
    US/Mexico border. Becasue shared things are meant to represent these sorts
    of entities, they have an allowed expression that always returns False.
    Nothing can be placed in one, on one, through one, be part of one, or be 
    held by one. If it were possible, for instance, to place a sticker on a 
    massive border wall, this implementation would make the sticker visible in
    every room along the border, which makes no sense.

    A SharedThing does *not* have a shared feature. The Rooms that it is
    located in have shared features which are lists containing the tags of each
    shared item."""

    def __init__(self, tag_and_parent, **keywords):
        check_attributes(tag_and_parent, [], ['allowed', 'parent'], keywords)
        tag_and_parent = tag_and_parent + ' of @cosmos'
        keywords['allowed'] = can.not_have_items
        self.sharedthing = True
        Thing.__init__(self, tag_and_parent, **keywords)


class Substance(Item):
    'Includes powders and liquids; must be in a source or vessel.'

    def __init__(self, tag, **keywords):
        check_attributes(tag, [], ['exits', 'shared', 'refuses'], keywords)
        tag_and_parent = tag + ' of @cosmos'
        keywords['allowed'] = can.have_any_item
        Item.__init__(self, tag_and_parent, 'substance', **keywords)

