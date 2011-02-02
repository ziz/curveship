"""Lost One

A demo interactive fiction in Curveship, an IF development system by
Nick Montfort. Shows how narrative distance can be changed based on the
player character's actions."""

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import random
import time

from item_model import Actor, Thing
from action_model import Behave, Sense
import can

import fiction.plaza

discourse = {
    'metadata': {
        'title': 'Lost One',
        'headline': 'An Interactive Demo',
        'people': [('by', 'Nick Montfort')]},

    'action_templates': [
        ('KICK', '[agent/s] [give/v] [direct/o] a fierce kick'),
        ('SHINE', 'the sun [hit/1/v] the plaza')],

    'spin': {
        'focalizer': '@visitor',
        'commanded': '@visitor',
        'speed': 0.5,
        'time': 'during',
        'order': 'chronicle',
        'narratee': '@visitor',
        'narrator': None,
        'known_directions': False,
        'room_name_headings': False,
        'time_words': False,
        'dynamic': True}}

SHINE = Behave('shine', '@cosmos', direct='@visitor')
SHINE.after ="""

[now] they [drive/2/v] cars, seeking flatpacks across the sprawl

once they were supposed to cluster [here]

[@visitor/s] [arrive/ed/v], visitor to this place where [@visitor/s] briefly 
lived years ago, where [@visitor/s] knew spaces and faces now almost forgotten

there is one [here] less lost to you than the others, though, and it [is/1/v] 
right [here] in this plaza, about [now], that [@visitor/s] [are/v] to meet him

somewhere right around [here]"""

SEE_PLAZA = Sense('see', '@visitor', direct='@plaza_center', modality='sight')

initial_actions = [SHINE, SEE_PLAZA]


class Distance_Filter:
    'Increases narrative distance by changing to less immediate styles.'

    def __init__(self, how_far):
        self.suffixes = [', apparently ', ', evidently', ', or so it seemed', 
                         ', if memory serves', ', perhaps']
        self.prefixes = ['it seemed that','it appeared that', 
                         'it looked like','it was as if','no doubt,']
        # For each step of distance, we roll one die; that is, 0 if we are at
        # distance 0, 8 if we are at distance 8, etc.
        # If any of these rolls are successful, a suffix (half the time) or a
        # prefix (half the time) will be added.
        # The base probability gives our chance for one die being successful.
        self.base_prob = 0.0
        self.update(how_far)

    def update(self, how_far):
        self.distance = how_far
        no_success = 1.0 - self.base_prob
        self.expression_prob = .5 * (1.0 - (no_success ** self.distance))

    def sentence_filter(self, phrases):
        pick = random.random()
        if pick < self.expression_prob * .5:
            prefix = [random.choice(self.prefixes)]
            time_words = []
            if phrases[0] in ['before that,', 'meanwhile,', 'then,']:
                time_words = [phrases.pop(0)]
            phrases = time_words + prefix + phrases
        elif pick < self.expression_prob:
            suffix = random.choice(self.suffixes)
            phrases.append(suffix)
        return phrases

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



distance_filter = Distance_Filter(0)


class Cosmos(Actor):

    def __init__(self, tag, **keywords):
        self.visitor_places = []
        self.visitor_moved = []
        self.distance = 0
        self.distance_filter = distance_filter
        self.timer = 16
        Actor.__init__(self, tag, **keywords)

    def act(self, command_map, concept):
        actions = []
        if (self.distance == 0 and concept.ticks > 80 and
            str(concept.item['@visitor'].place(concept)) == '@plaza_center'):
            smile = Behave('smile', '@visitor')
            smile.final = True
            smile.before = """[@visitor/s] [turn/v] and [see/v] [@visitor's] 
                           friend"""
            actions.append(smile)
        return actions

    def interval(self):
        if self.timer > 0:
            self.timer -= 1
        time.sleep(self.timer / 5.0)

    def update_distance(self, spin):
        spin['time'] = ('during', 'after')[self.distance > 2]
        self.distance_filter.base_prob = (0.0, (1.0/6.0))[self.distance > 2]
        spin['narratee'] = ('@visitor', None)[self.distance > 4]
        spin['time_words'] = (False, True)[self.distance > 5]
        spin['commanded'] = ('@visitor', None)[self.distance > 9]
        self.distance_filter.update(self.distance)
        spin['sentence_filter'] = [distance_filter.sentence_filter]
        if self.distance < 6:
            spin['order'] = 'chronicle'
        elif self.distance < 8:
            spin['order'] = 'retrograde'
        else:
            spin['order'] = 'achrony'
        return spin

    def update_spin(self, concept, discourse):
        if discourse.spin['dynamic']:
            if len(self.visitor_places) > 0:
                self.visitor_moved.append( not self.visitor_places[-1] == \
                 concept.item['@visitor'].place(concept) )
            new_place = concept.item['@visitor'].place(concept)
            self.visitor_places.append(new_place)
            if sum(self.visitor_moved[-1:]) > 0:
                self.distance += 1
            else:
                if self.distance > 0:
                    self.distance -= .25
            discourse.spin = self.update_distance(discourse.spin)
        else:
            self.distance = 1
        return discourse.spin

cosmos = Cosmos('@cosmos', called='creation', allowed=can.have_any_item)


class Wanderer(Actor):
    '@visitor is the only instance. act() is used when commanded is None.'

    def act(self, command_map, concept):
        if random.random() < self.walk_probability:
            way = random.choice(self.place(concept).exits.keys())
            return [self.do_command(['leave', way], command_map, concept)]
        return []


class Collector(Actor):
    'Not used! @collector uses a deterministic script instead.'

    def act(self, command_map, concept):
        for (tag, link) in list(concept.item[str(self)].r(concept).child()):
            if link == 'in' and 'trash' in concept.item[tag].qualities:
                return [self.do_command(['take', tag], command_map, concept)]
        if random.random() < self.walk_probability:
            way = random.choice(self.place(concept).exits.keys())
            return [self.do_command(['leave', way], command_map, concept)]
        return []


class Kicker(Actor):
    'Not used! @punk uses a deterministic script instead.'

    def act(self, command_map, concept):
        if random.random() < self.walk_probability:
            way = random.choice(self.place(concept).exits.keys())
            return [self.do_command(['leave', way], command_map, concept)]
        elif random.random() < self.kick_probability:
            for (tag, link) in concept.item[str(self)].r(concept).child():
                if link == 'part_of':
                    return [self.do_command(['kick', tag], command_map,
                                            concept)]
        return []


items = fiction.plaza.items + [

    Wanderer('@visitor in @plaza_center',
        article='the',
        called='visitor',
        referring='|',
        allowed=can.possess_any_thing,
        qualities=['person', 'woman'],
        gender='female',
        sight='[*/s] [see/v] someone who is out of place',
        walk_probability=0.7,
        start=25),

    Thing('@tortilla of @visitor',
        article='a',
        called='(tasty) (corn) tortilla',
        referring='tasty typical circular thin white corn | circle disc disk',
        sight='a thin white circle, a corn tortilla',
        taste='bland but wholesome nutriment',
        consumable=True,
        prominence=0.2),

    Actor('@flaneur in @plaza_center',
        article='a',
        called='flaneur',
        referring='distracted foppish | flaneur',
        allowed=can.possess_any_thing,
        sight='a foppish man who [seem/1/v] dedicated to strolling about',
        qualities=['person', 'man'],
        gender='male',
        script=['leave north','wait','wait','wander','wait','leave east','wait',
                'wait','wander','wait','leave south','wait','wander','wait',
                'wander','wait','wait','leave south','wait','wait',
                'leave west','wait','wait','wander','wait','wait',
                'leave west','wait','wait','wander','wait','wait',
                'leave north','wait','wait','wander','wait','wait',
                'leave north','wait', 'wait','leave east','wait','wait',
                'leave southwest','wait','wait'],
        start=5),

    Actor('@punk in @plaza_w',
        article='some',
        called='punk',
        referring='angry punky | punk',
        allowed=can.possess_any_thing,
        sight='a girl who clearly [participate/ing/v] in the punk subculture',
        qualities=['person', 'woman'],
        gender='female',
        angry=True,
        script=['kick @tree', 'wait', 'wait', 'leave southeast', 
                'kick @obelisk', 'wait', 'wait', 'leave north', 'leave west'],
        script_loops=True,
        start=10),

    Actor('@collector in @plaza_sw',
        article='a',
        called='trash collector',
        referring='some nondescript trash | collector',
        allowed=can.possess_any_thing,
        sight='a nondescript man who seems to be a bona fide trash collector',
        qualities=['person', 'man'],
        gender='male',
        script=['take @candy_wrapper',
                'leave north',
                'take @smashed_cup',
                'leave north',
                'leave east',
                'leave south',
                'leave south',
                'leave east',
                'take @scrap',
                'leave north',
                'take @shredded_shirt',
                'take @newspaper_sheet'],
        start=45),

    Actor('@boy in @plaza_ne',
        article='a',
        called='boy',
        referring='| child',
        allowed=can.possess_any_thing,
        sight='an unremarkable boy',
        qualities=['person', 'man'],
        gender='male',
        script=['throw @ball', 'take @ball', 'wait'],
        script_loops=True,
        start=20),

    Thing('@ball of @boy',
        article='a',
        called='ball',
        referring='| ball baseball')]

