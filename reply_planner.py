'Plan a reply, as in "document planning" (but this is a reply in a dialogue).'

__author__ = 'Nick Montfort'
__copyright__ = 'Copyright 2011 Nick Montfort'
__license__ = 'ISC'
__version__ = '0.5.0.0'
__status__ = 'Development'

import operator
import random

def determine_speed(action, discourse):
    'Returns a number in [0, 1], the speed of narration for this Action.'
    if action.salience > 0.75:
        speed = discourse.spin['speed'] + ((1-discourse.spin['speed'])/2)
    elif (action.verb == 'wait' and
          not action.agent == discourse.spin['focalizer']):
        # Do not ever narrate other characters waiting (doing nothing).
        speed = 0.0
    else:
        speed = discourse.spin['speed']
    return speed


def structure_nodes(nodes, ref_time, speech_time, discourse):
    'Return the root node of a reply structure organized using the parameters.'
    children = []
    last_action_time = None
    for node in nodes:
        if node.category == 'action':
            node.speed = determine_speed(node.info, discourse)
            node.prior = last_action_time
            last_action_time = node.info.start
            if node.speed > 0.0:
                discourse.mark_narrated(node.info)
                children.append(node)
        else:
            children.append(node)
    return Internal('-', ref_time, speech_time, children)


def produce_analepsis(key_action, previous, concept, discourse):
    'Finds an analepsis based on and to be inserted after the key Action.'
    if hasattr(key_action, 'direct'):
        for action in previous:
            if (hasattr(action, 'direct') and 
                action.direct == key_action.direct and
                not concept.item[action.direct] == '@adventurer'):
                intro = Commentary("Ah, let's remember ...")
                room = NameRoom(action)
                tell_action = TellAction(action)
                outro = Commentary("Yes, that was a fine recollection.")
                return [structure_nodes([intro, room, tell_action, outro], 
                                        discourse.follow, key_action.end,
                                        discourse)]
    return []


def cull_actions(actions, concept, discourse):
    'Remove Actions that should not be narrated at all from a sorted list.'

    to_remove = []
    to_aggregate = []
    post_final = False
    for action in actions:
        if (action.verb == 'examine' and
            not action.agent == discourse.spin['focalizer'] and
            action.direct == str(concept.room_of(action.agent))):
            to_remove.append(action)
        elif action.salience < .2:
            to_remove.append(action)
        elif post_final:
            to_remove.append(action)
        if action.final:
            post_final = True
    for omit in to_remove:
        actions.remove(omit)
    if discourse.spin['frequency'][0][1] == 'iterative':
        if discourse.spin['frequency'][0][0][0] == 'agent':
            quality = discourse.spin['frequency'][0][0][1]
            for action in actions:
                if quality in concept.item[action.agent].qualities:
                    to_aggregate.append(action)
            if len(to_aggregate) >= 2:
                for omit in to_aggregate:
                    actions.remove(omit)
                actions.append(to_aggregate)
    return actions


def determine_speech_time(discourse):
    'Set speech time all the way ahead, or to follow the events, or back.'

    if discourse.spin['time'] == 'before':
        speech_time = discourse.min
    if discourse.spin['time'] == 'during':
        speech_time = discourse.follow
    if discourse.spin['time'] == 'after':
        speech_time = discourse.max
    return speech_time


def plan(action_ids, concept, discourse):
    'Create a reply structure based on indicated Actions and the spin.'


    speech_time = determine_speech_time(discourse)

    # Determine which Actions this focalizer knows about.
    # Build a list of the appropriate (Action, start time) tuples.
    known_id_times = []
    if discourse.spin['window'] == 'current':
        for i in action_ids:
            if i in concept.act:
                known_id_times.append((i, concept.act[i].start))
    else:
        for i in concept.act:
            known_id_times.append((i, concept.act[i].start))

    # Produce a list of Actions sorted by time.
    actions = [concept.act[id_etc[0]] for id_etc in
               sorted(known_id_times, key=operator.itemgetter(1))]

    if not discourse.spin['window'] == 'current':
        actions = actions[-discourse.spin['window']:]

    # Remove Actions which won't be narrated at all, aggregate others.
    actions = cull_actions(actions, concept, discourse)

    if len(actions) == 0:
        return Leaf('ok')

    if discourse.spin['perfect']:
        reference_time = discourse.right_after
    else:
        reference_time = discourse.follow

    # Sort the Actions chronologically to begin with.
    actions.sort(key=operator.attrgetter('start'))
    if discourse.spin['order'] == 'chronicle':
        nodes = [TellAction(i) for i in actions]
        reply_plan = structure_nodes(nodes, reference_time, speech_time,
                                     discourse)
    elif discourse.spin['order'] == 'retrograde':
        actions.reverse()
        if speech_time == discourse.follow:
            speech_time = actions[0].start
        nodes = [TellAction(i) for i in actions]
        reply_plan = structure_nodes(nodes, reference_time, speech_time,
                                     discourse)
    elif discourse.spin['order'] == 'achrony':
        random.shuffle(actions)
        nodes = [TellAction(i) for i in actions]
        reply_plan = structure_nodes(nodes, reference_time, speech_time,
                                     discourse)
    elif discourse.spin['order'] == 'analepsis':
        nodes = [TellAction(i) for i in actions]
        if actions[-1].id > 4:
            limit = actions[-1].id - 4
            previous = [concept.act[i] for i in
                        range(1, limit) if i in concept.act]
            analepsis = produce_analepsis(actions[0], previous, concept, 
                                          discourse)
            nodes = nodes[:1] + analepsis + nodes[1:]
        reply_plan = structure_nodes(nodes, reference_time, speech_time,
                                     discourse)
    elif discourse.spin['order'] == 'syllepsis':
        nodes = [TellAction(i) for i in actions]
        reply_plan = structure_nodes(nodes, reference_time, speech_time,
                                     discourse)
    return reply_plan


class ReplyNode(object):
    'Abstract base class for reply structure nodes.'

    def __init__(self, category):
        if self.__class__ == ReplyNode:
            raise StandardError('Attempt to instantiate abstract base ' +
                                'class reply_planner.ReplyNode')
        self.category = category


class Internal(ReplyNode):
    'Internal node in a reply structure, representing organization.'

    def __init__(self, category, reference_time, speech_time, children):
        self.ref = reference_time
        self.speech = speech_time
        self.children = children
        ReplyNode.__init__(self, category)

    def __str__(self):
        string = self.category + ' ('
        for child in self.children:
            string += str(child) + ' '
        string = string[:-1] + ') '
        return string


class Leaf(ReplyNode):
    'Leaf node in a reply structure, representing something to narrate.'

    def __init__(self, category, info=None):
        if info is not None:
            self.info = info
        self.speed = None
        self.event = None
        self.prior = None
        if category == 'action' or category == 'room':
            self.event = info.start
        ReplyNode.__init__(self, category)

    def __str__(self):
        return self.category + ' ' + str(self.info)


class Commentary(Leaf):
    'A statement that does not narrate or describe: "Be careful, dear reader!"'

    def __init__(self, info):
        Leaf.__init__(self, 'commentary', info)


class NameRoom(Leaf):
    'A statement naming the Room in which the Action took place.'

    def __init__(self, info):
        Leaf.__init__(self, 'room', info)
        self.prior = self.event - 0.5


class TellAction(Leaf):
    'A statement narrating an Action.'

    def __init__(self, info):
        Leaf.__init__(self, 'action', info)

